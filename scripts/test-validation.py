#!/usr/bin/env python3
"""Regression checks for the package validators; Python is only a test dependency."""

import copy
import json
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import unittest
import warnings
import zipfile


ROOT = Path(__file__).resolve().parent.parent
REVIEW_RECORDING_URL = (
    'https://github.com/trybloomai/rainbrand-skills/releases/download/v1.1.2/'
    'rainbrand-review-walkthrough-v1.1.2.mp4'
)
PLUGIN_MEMBERS = [
    'plugin.json', 'mcp.json', 'skills/rainbrand/SKILL.md', 'README.md',
    'CHANGELOG.md', 'LICENSE',
]


class PackageValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='rainbrand-tests-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '.context'))
        self.manifest = json.loads((self.root / 'plugin.json').read_text())
        self.mcp = json.loads((self.root / 'mcp.json').read_text())
        # Exercise an intentionally incomplete draft even after final artwork
        # and recording have been added to the real distribution.
        interface = self.manifest['extensions']['com.openai']['interface']
        interface.pop('logo', None)
        interface.pop('composerIcon', None)
        self.manifest['extensions']['com.openai']['review'].pop('demo_recording_url', None)
        artwork = self.root / 'assets/rainbrand-logo.png'
        if artwork.exists():
            artwork.unlink()
        self.write_json('plugin.json', self.manifest)
        self.run_script('package-skill.sh')
        self.run_script('package-plugin.sh')

    def run_script(self, name, *args, succeeds=True, env=None):
        result = subprocess.run(
            ['bash', str(self.root / 'scripts' / name), *map(str, args)],
            cwd=self.root, capture_output=True, text=True, env=env,
        )
        if succeeds:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def write_json(self, name, data):
        (self.root / name).write_text(json.dumps(data, indent=2) + '\n')

    def test_optional_repository(self):
        for repository in (None, 'https://github.com/trybloomai/rainbrand-skills'):
            with self.subTest(repository=repository):
                changed = copy.deepcopy(self.manifest)
                changed.pop('repository', None)
                if repository is not None:
                    changed['repository'] = repository
                self.write_json('plugin.json', changed)
                self.run_script('package-skill.sh')
                self.run_script('package-plugin.sh')
                self.run_script('validate-plugin.sh')

    def test_manifest_rejections(self):
        changes = [
            ('version', '9.9.9'), ('repository', 'https://example.com/repository'),
            ('$schema', 'https://example.com/schema'), ('displayName', 'Rainbrand'),
            ('mcpServers', {}), ('name', 'other'),
        ]
        for field, value in changes:
            with self.subTest(field=field):
                changed = copy.deepcopy(self.manifest)
                changed[field] = value
                self.write_json('plugin.json', changed)
                self.run_script('package-skill.sh', succeeds=False)
        for payload in (
            '{"name":"rainbrand","name":"rainbrand"}',
            '{"name":"rainbrand",}',
            json.dumps(self.manifest) + ' null',
            json.dumps(self.manifest).replace('The brand layer for agents.', r'\u0042loom'),
        ):
            with self.subTest(payload=payload[:40]):
                (self.root / 'plugin.json').write_text(payload)
                self.run_script('package-skill.sh', succeeds=False)

    def test_mcp_rejections(self):
        for changed in (
            {'$schema': self.mcp['$schema'], 'mcpServers': {}},
            {'$schema': self.mcp['$schema'], 'mcpServers': {
                'rainbrand': self.mcp['mcpServers']['rainbrand'],
                'extra': self.mcp['mcpServers']['rainbrand'],
            }},
            {'$schema': self.mcp['$schema'], 'mcpServers': {
                'rainbrand': {'type': 'http', 'url': 'https://mcp.rainbrand.com/mcp'},
            }},
            {'$schema': self.mcp['$schema'], 'mcpServers': {
                'rainbrand': {'type': 'streamable-http', 'url': 'https://example.com/mcp'},
            }},
            {'$schema': self.mcp['$schema'], 'mcpServers': {
                'rainbrand': {**self.mcp['mcpServers']['rainbrand'], 'headers': {'Authorization': 'invalid'}},
            }},
        ):
            with self.subTest(mcp=changed):
                self.write_json('mcp.json', changed)
                self.run_script('package-skill.sh', succeeds=False)

    def test_review_contract_rejections(self):
        changes = [
            ('positive', 5, 'tools_triggered', 'list_workspaces, check_credits'),
            ('positive', 0, 'tools_triggered', 'rainbrand_list_brands'),
            ('positive', 3, 'prompt', 'Onboard Shake Shack.'),
            ('negative', 2, 'prompt', 'What is 18 + 25?'),
        ]
        for group, index, field, value in changes:
            with self.subTest(field=field, value=value):
                changed = copy.deepcopy(self.manifest)
                changed['extensions']['com.openai']['review']['test_cases'][group][index][field] = value
                self.write_json('plugin.json', changed)
                self.run_script('package-skill.sh', succeeds=False)

    def test_submission_gates_and_icon_pair(self):
        self.run_script('validate-plugin.sh')
        blocked = self.run_script('validate-plugin.sh', '--submission', succeeds=False)
        self.assertIn('approved Rainbrand artwork', blocked.stderr)
        changed = copy.deepcopy(self.manifest)
        interface = changed['extensions']['com.openai']['interface']
        interface['logo'] = './assets/rainbrand-logo.png'
        self.write_json('plugin.json', changed)
        self.run_script('package-skill.sh', succeeds=False)
        # Test manifest gates alone, without creating or claiming approved art.
        interface['composerIcon'] = './assets/rainbrand-logo.png'
        changed['extensions']['com.openai']['review']['demo_recording_url'] = REVIEW_RECORDING_URL
        self.write_json('plugin.json', changed)
        command = ['awk', '-v', 'kind=plugin', '-v', 'expected_name=rainbrand',
                   '-v', 'expected_version=' + changed['version'], '-v', 'has_artwork=1',
                   '-v', 'allowed_legacy_url=' + REVIEW_RECORDING_URL,
                   '-v', 'submission=1', '-f', str(self.root / 'scripts/validate-manifests.awk'),
                   str(self.root / 'plugin.json')]
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
        for recording_url in ('', 'http://video.example.com/walkthrough.mp4',
                              'https:///walkthrough.mp4', 'https://video.example.com/bad path',
                              'https://user:password@video.example.com/walkthrough.mp4',
                              'https://github.com/trybloomai/bloom-skills/releases/'
                              'download/v1.1.2/other.mp4', None):
            with self.subTest(recording_url=recording_url):
                changed['extensions']['com.openai']['review']['demo_recording_url'] = recording_url
                self.write_json('plugin.json', changed)
                self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
        del changed['extensions']['com.openai']['review']['demo_recording_url']
        self.write_json('plugin.json', changed)
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('record and upload', result.stderr)

    def test_corrupt_or_unexpected_archive_members(self):
        source = self.root / 'dist/rainbrand.plugin.zip'
        with zipfile.ZipFile(source) as archive:
            originals = [(member, archive.read(member)) for member in archive.infolist()]
        for mutation in ('extra', 'duplicate', 'wrapper', 'changed', 'symlink', 'traversal'):
            with self.subTest(mutation=mutation):
                candidate = self.root / 'candidate.zip'
                with warnings.catch_warnings(), zipfile.ZipFile(candidate, 'w') as archive:
                    warnings.simplefilter('ignore', UserWarning)
                    for member, data in originals:
                        member = copy.copy(member)
                        if mutation == 'wrapper':
                            member.filename = 'wrapper/' + member.filename
                        if mutation == 'changed' and member.filename == 'README.md':
                            data += b'\nChanged bytes\n'
                        if mutation == 'symlink' and member.filename == 'README.md':
                            member.external_attr = (stat.S_IFLNK | 0o777) << 16
                        archive.writestr(member, data)
                    if mutation in ('extra', 'traversal'):
                        archive.writestr('../outside' if mutation == 'traversal' else 'extra.txt', 'extra')
                    if mutation == 'duplicate':
                        archive.writestr(*originals[0])
                self.run_script('validate-plugin.sh', candidate, succeeds=False)
        candidate.write_bytes(b'Not a ZIP')
        self.run_script('validate-plugin.sh', candidate, succeeds=False)

    def test_skill_archive_and_frontmatter_rejections(self):
        path = self.root / 'skills/rainbrand/SKILL.md'
        original = path.read_text()
        path.write_text(original.replace('description: ', 'description: ' + 'x' * 201, 1))
        self.run_script('package-skill.sh', succeeds=False)
        path.write_text(original)
        with zipfile.ZipFile(self.root / 'dist/rainbrand.skill.zip', 'a') as archive:
            archive.writestr('extra.txt', 'extra')
        self.run_script('validate-plugin.sh', succeeds=False)

    def test_skill_workflow_guidance_rejections(self):
        path = self.root / 'skills/rainbrand/SKILL.md'
        original = path.read_text()
        required_guidance = [
            'search the connected Rainbrand tool catalog again',
            'the loaded subset is not the full connection',
            ('Fall back to browser-based docs lookup only when connected tool '
             'discovery is unavailable or fails, or a real tool error requires '
             'documentation.'),
            ('use `onboard_brand` when the user asks to create or onboard a brand '
             'from a website, Instagram, or files.'),
            ('The same tool name has two different contracts; do not mix their '
             'inputs or polling tools.'),
            'If `generate_image` accepts a top-level `prompt` and `brand_session_id`',
            'Rainbrand applies brand styling automatically.',
            ('This catalog also provides `edit_image`, `resize_image`, '
             '`remove_background`, and `vectorize_image`'),
            'If `generate_image` accepts `model` and `input` alongside `brand_session_id`',
            'Omit `brief_id` when the live schema does not advertise it.',
            'If `create_review` and `get_review` are present',
            ('The current MCP Model Gateway catalog supports image, video, and '
             'audio, not SVG generation.'),
        ]
        normalized = original.replace('\n', ' ')
        for marker in required_guidance:
            with self.subTest(marker=marker):
                path.write_text(normalized.replace(marker, 'removed guidance', 1))
                self.run_script('package-skill.sh', succeeds=False)
        for retired_name in (
            'generate_image_with_model', 'generate_svg',
            'list_generation_models', 'get_generation_model',
        ):
            with self.subTest(retired_name=retired_name):
                path.write_text(original + f'\n`{retired_name}`\n')
                self.run_script('package-skill.sh', succeeds=False)

    def test_plugin_rejects_unavailable_generation_claims(self):
        changed = copy.deepcopy(self.manifest)
        interface = changed['extensions']['com.openai']['interface']
        interface['longDescription'] = interface['longDescription'].replace(
            'image, video, or audio models', 'image, video, audio, or SVG models',
        )
        self.write_json('plugin.json', changed)
        self.run_script('package-skill.sh', succeeds=False)

        changed = copy.deepcopy(self.manifest)
        capabilities = changed['extensions']['com.openai']['interface']['capabilities']
        capabilities[-2] = 'Selected image, video, audio, and SVG models'
        self.write_json('plugin.json', changed)
        self.run_script('package-skill.sh', succeeds=False)

    def test_source_symlinks_and_extra_skills(self):
        license_path = self.root / 'LICENSE'
        contents = license_path.read_bytes()
        target = Path(self.temp.name) / 'outside-license'
        target.write_bytes(contents)
        license_path.unlink()
        license_path.symlink_to(target)
        self.run_script('package-skill.sh', succeeds=False)
        license_path.unlink()
        license_path.write_bytes(contents)
        (self.root / 'skills/extra').mkdir()
        self.run_script('package-skill.sh', succeeds=False)

    def test_reproducibility_and_exact_members(self):
        import os
        before = {path.name: path.read_bytes() for path in (self.root / 'dist').glob('*.zip')}
        for timezone in ('Pacific/Honolulu', 'Asia/Tokyo'):
            environment = {**os.environ, 'TZ': timezone}
            command = 'umask 077; bash scripts/package-skill.sh && bash scripts/package-plugin.sh'
            subprocess.run(['bash', '-c', command], cwd=self.root, env=environment,
                           check=True, capture_output=True)
            for name, contents in before.items():
                self.assertEqual((self.root / 'dist' / name).read_bytes(), contents)
        self.run_script('validate-plugin.sh')
        with zipfile.ZipFile(self.root / 'dist/rainbrand.plugin.zip') as archive:
            self.assertEqual(archive.namelist(), PLUGIN_MEMBERS)
        with zipfile.ZipFile(self.root / 'dist/rainbrand.skill.zip') as archive:
            self.assertEqual(archive.namelist(), ['rainbrand/SKILL.md'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
