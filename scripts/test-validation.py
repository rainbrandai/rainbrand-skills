#!/usr/bin/env python3
"""Regression checks for the package validators; Python is only a test dependency."""

import copy
import json
import os
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
    'CHANGELOG.md', 'LICENSE', 'assets/rainbrand-logo.png',
]
CLAUDE_PLUGIN_MEMBERS = [
    '.claude-plugin/plugin.json', '.mcp.json', 'skills/rainbrand/SKILL.md',
    'README.md', 'CHANGELOG.md', 'LICENSE', 'assets/rainbrand-logo.png',
]


class PackageValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='rainbrand-tests-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '.context'))
        self.manifest = json.loads((self.root / 'plugin.json').read_text())
        self.mcp = json.loads((self.root / 'mcp.json').read_text())
        self.claude_manifest = json.loads((self.root / '.claude-plugin/plugin.json').read_text())
        self.claude_mcp = json.loads((self.root / '.mcp.json').read_text())
        # Keep the baseline incomplete for directory submission. Native upload
        # includes the icon; the portable no-artwork draft is tested separately.
        self.manifest['extensions']['com.openai']['review'].pop('demo_recording_url', None)
        self.write_json('plugin.json', self.manifest)
        self.run_script('package-skill.sh')
        self.run_script('package-plugin.sh')
        self.run_script('package-claude-plugin.sh')

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
        interface = self.manifest['extensions']['com.openai']['interface']
        interface.pop('logo', None)
        interface.pop('composerIcon', None)
        (self.root / 'assets/rainbrand-logo.png').unlink()
        self.write_json('plugin.json', self.manifest)
        # Preserve the portable package's support for no-artwork drafts.
        self.run_script('package-skill.sh')
        self.run_script('package-plugin.sh')
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

    def test_archives_reject_stale_canonical_skill_content(self):
        path = self.root / 'skills/rainbrand/SKILL.md'
        original = path.read_text()
        path.write_text(original + '\nCanonical content changed.\n')
        self.run_script('validate-plugin.sh', succeeds=False)
        self.run_script('validate-claude-plugin.sh', succeeds=False)

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
        before = {path.name: path.read_bytes() for path in (self.root / 'dist').glob('*.zip')}
        for timezone, mask in (('Pacific/Honolulu', '077'), ('Asia/Tokyo', '022')):
            environment = {**os.environ, 'TZ': timezone}
            command = f'umask {mask}; bash scripts/package-release.sh'
            subprocess.run(['bash', '-c', command], cwd=self.root, env=environment,
                           check=True, capture_output=True)
            for name, contents in before.items():
                self.assertEqual((self.root / 'dist' / name).read_bytes(), contents)
        self.run_script('validate-plugin.sh')
        self.run_script('validate-claude-plugin.sh')
        with zipfile.ZipFile(self.root / 'dist/rainbrand.plugin.zip') as archive:
            self.assertEqual(archive.namelist(), PLUGIN_MEMBERS)
        with zipfile.ZipFile(self.root / 'dist/rainbrand.skill.zip') as archive:
            self.assertEqual(archive.namelist(), ['rainbrand/SKILL.md'])
        with zipfile.ZipFile(self.root / 'dist/bloom.skill.zip') as archive:
            self.assertEqual(archive.namelist(), ['bloom/SKILL.md'])
            member = archive.infolist()[0]
            self.assertEqual(member.date_time, (1980, 1, 1, 0, 0, 0))
            self.assertEqual(stat.S_IMODE(member.external_attr >> 16), 0o644)
        with zipfile.ZipFile(self.root / 'dist/rainbrand.claude-plugin.zip') as archive:
            self.assertEqual(archive.namelist(), CLAUDE_PLUGIN_MEMBERS)
            for member in archive.infolist():
                self.assertEqual(member.date_time, (1980, 1, 1, 0, 0, 0))
                self.assertEqual(stat.S_IMODE(member.external_attr >> 16), 0o644)
                self.assertEqual(archive.read(member), (self.root / member.filename).read_bytes())

    def test_claude_manifest_rejections(self):
        changes = [
            ('version', '9.9.9'), ('version', 118), ('name', 'other'),
            ('description', ''), ('description', []), ('author', 'Rainbrand'),
            ('author', {'name': 'Rainbrand', 'unsupported': True}),
            ('homepage', 'https://example.com'), ('repository', False),
            ('license', 'other'), ('$schema', self.manifest['$schema']),
            ('extensions', {}), ('skills', './forked-skill/'),
            ('icon', '../outside.png'), ('icon', '/tmp/logo.png'),
            ('icon', './other.png'), ('icon', None),
        ]
        for field, value in changes:
            with self.subTest(field=field, value=value):
                changed = copy.deepcopy(self.claude_manifest)
                changed[field] = value
                self.write_json('.claude-plugin/plugin.json', changed)
                self.run_script('package-claude-plugin.sh', succeeds=False)
        for field in self.claude_manifest:
            with self.subTest(missing=field):
                changed = copy.deepcopy(self.claude_manifest)
                del changed[field]
                self.write_json('.claude-plugin/plugin.json', changed)
                self.run_script('package-claude-plugin.sh', succeeds=False)
        for payload in (
            '{"name":"rainbrand","name":"rainbrand"}',
            '{"name":"rainbrand",}',
            json.dumps(self.claude_manifest) + ' null',
            json.dumps(self.claude_manifest).replace('Rainbrand', r'\u0042loom'),
        ):
            with self.subTest(payload=payload[:40]):
                (self.root / '.claude-plugin/plugin.json').write_text(payload)
                self.run_script('package-claude-plugin.sh', succeeds=False)

    def test_claude_mcp_rejections(self):
        server = self.claude_mcp['mcpServers']['rainbrand']
        changes = [
            {}, {'mcpServers': []}, {'mcpServers': {}},
            {'mcpServers': {'other': server}},
            {'mcpServers': {'rainbrand': server, 'extra': server}},
            {**self.claude_mcp, '$schema': self.mcp['$schema']},
        ]
        for field, value in (
            ('type', 'streamable-http'), ('type', 'stdio'), ('type', True),
            ('url', 'https://example.com/mcp'), ('url', 'http://mcp.rainbrand.com/mcp'),
            ('url', None), ('headers', {'Authorization': 'invalid'}),
            ('command', 'node'),
        ):
            changes.append({'mcpServers': {'rainbrand': {**server, field: value}}})
        for field in server:
            changed = copy.deepcopy(self.claude_mcp)
            del changed['mcpServers']['rainbrand'][field]
            changes.append(changed)
        for changed in changes:
            with self.subTest(mcp=changed):
                self.write_json('.mcp.json', changed)
                self.run_script('package-claude-plugin.sh', succeeds=False)
        for payload in (
            '{"mcpServers":{},"mcpServers":{}}',
            '{"mcpServers":{},}',
            json.dumps(self.claude_mcp) + ' false',
            json.dumps(self.claude_mcp).replace('"type": "http"', '"type": "http", "type": "http"'),
        ):
            with self.subTest(payload=payload[:40]):
                (self.root / '.mcp.json').write_text(payload)
                self.run_script('package-claude-plugin.sh', succeeds=False)

    def test_claude_corrupt_or_unexpected_archive_members(self):
        source = self.root / 'dist/rainbrand.claude-plugin.zip'
        with zipfile.ZipFile(source) as archive:
            originals = [(member, archive.read(member)) for member in archive.infolist()]
        mutations = ('extra', 'duplicate', 'wrapper', 'symlink', 'traversal',
                     'missing-manifest', 'missing-mcp', 'missing-icon', 'nested-zip',
                     *('changed:' + name for name in CLAUDE_PLUGIN_MEMBERS))
        missing = {'missing-manifest': '.claude-plugin/plugin.json',
                   'missing-mcp': '.mcp.json', 'missing-icon': 'assets/rainbrand-logo.png'}
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                candidate = self.root / 'candidate.zip'
                with warnings.catch_warnings(), zipfile.ZipFile(candidate, 'w') as archive:
                    warnings.simplefilter('ignore', UserWarning)
                    for member, data in originals:
                        member = copy.copy(member)
                        if member.filename == missing.get(mutation):
                            continue
                        if mutation == 'changed:' + member.filename:
                            data += b'\nChanged bytes\n'
                        if mutation == 'wrapper':
                            member.filename = 'wrapper/' + member.filename
                        if mutation == 'symlink' and member.filename == 'assets/rainbrand-logo.png':
                            member.external_attr = (stat.S_IFLNK | 0o777) << 16
                        archive.writestr(member, data)
                    if mutation == 'extra':
                        archive.writestr('plugin.json', '{}')
                    if mutation == 'traversal':
                        archive.writestr('../outside', 'extra')
                    if mutation == 'nested-zip':
                        archive.writestr('dist/rainbrand.plugin.zip', source.read_bytes())
                    if mutation == 'duplicate':
                        archive.writestr(*originals[0])
                self.run_script('validate-claude-plugin.sh', candidate, succeeds=False)
        candidate.write_bytes(b'Not a ZIP')
        self.run_script('validate-claude-plugin.sh', candidate, succeeds=False)
        # The two plugin formats cannot accidentally be accepted interchangeably.
        self.run_script('validate-plugin.sh', source, succeeds=False)
        self.run_script('validate-claude-plugin.sh', self.root / 'dist/rainbrand.plugin.zip', succeeds=False)

    def test_claude_icon_source_and_archive_parity(self):
        path = self.root / 'assets/rainbrand-logo.png'
        original = path.read_bytes()
        path.write_bytes(original + b'changed')
        self.run_script('validate-claude-plugin.sh', succeeds=False)
        path.unlink()
        self.run_script('package-claude-plugin.sh', succeeds=False)
        target = Path(self.temp.name) / 'outside-logo.png'
        target.write_bytes(original)
        path.symlink_to(target)
        self.run_script('package-claude-plugin.sh', succeeds=False)

    def test_claude_manifest_source_guards(self):
        path = self.root / '.claude-plugin/plugin.json'
        target = Path(self.temp.name) / 'outside-manifest.json'
        target.write_bytes(path.read_bytes())
        path.unlink()
        self.run_script('package-claude-plugin.sh', succeeds=False)
        path.symlink_to(target)
        self.run_script('package-claude-plugin.sh', succeeds=False)

    def test_bloom_skill_identity_and_guidance_parity(self):
        canonical = (self.root / 'skills/rainbrand/SKILL.md').read_bytes()
        # Independent expected identity substitutions; compare every guidance byte.
        expected = canonical
        for before, after in (
            (b'docs.rainbrand.com', b'docs.trybloom.ai'),
            (b'www.rainbrand.com', b'www.trybloom.ai'),
            (b'mcp.rainbrand.com', b'mcp.trybloom.ai'),
            (b'Rainbrand', b'Bloom'), (b'rainbrand', b'bloom'),
        ):
            expected = expected.replace(before, after)
        with zipfile.ZipFile(self.root / 'dist/bloom.skill.zip') as archive:
            self.assertEqual(archive.namelist(), ['bloom/SKILL.md'])
            bloom = archive.read('bloom/SKILL.md')
        with zipfile.ZipFile(self.root / 'dist/rainbrand.skill.zip') as archive:
            self.assertEqual(archive.read('rainbrand/SKILL.md'), canonical)
        self.assertEqual(bloom, expected)
        self.assertNotIn(b'rainbrand', bloom.lower())
        self.assertNotIn(b'bloom', canonical.lower())
        self.assertIn(b'name: bloom\n', bloom)
        self.assertIn(b'  author: Bloom\n', bloom)
        version_line = next(line for line in canonical.splitlines() if line.startswith(b'  version:'))
        self.assertIn(version_line, bloom.splitlines())
        self.assertIn(b'  version: "' + self.manifest['version'].encode() + b'"', bloom)
        self.assertIn(b'When the task changes or a needed tool is not loaded', bloom)
        self.assertIn(b'`onboard_brand`', bloom)
        self.assertNotIn(b'generate_image_with_model', bloom)
        self.assertFalse((self.root / 'skills/bloom').exists())
        self.run_script('validate-skills.sh')

    def test_bloom_endpoint_substitution_and_generated_metadata(self):
        canonical_path = self.root / 'skills/rainbrand/SKILL.md'
        canonical_path.write_text(canonical_path.read_text() + '\nRainbrand MCP: https://mcp.rainbrand.com/mcp\n')
        self.run_script('package-skill.sh')
        with zipfile.ZipFile(self.root / 'dist/bloom.skill.zip') as archive:
            bloom = archive.read('bloom/SKILL.md')
        self.assertIn(b'Bloom MCP: https://mcp.trybloom.ai/mcp', bloom)
        renderer = self.root / 'scripts/brand-bloom-skill.awk'
        original = renderer.read_text()
        for mutation in ('    gsub(/Bloom/, "Rainbrand")\n',
                         '    sub(/^  version:.*/, "  version: 9.9.9")\n'):
            with self.subTest(mutation=mutation):
                renderer.write_text(original.replace('    print\n', mutation + '    print\n'))
                self.run_script('package-skill.sh', succeeds=False)

    def test_branding_compatibility_prose_is_scoped(self):
        readme = self.root / 'README.md'
        original = readme.read_text()
        prose = '\nFor Bloom compatibility, `bloom.skill.zip` contains `bloom/SKILL.md` with Bloom identity.\n'
        readme.write_text(original + prose)
        self.run_script('package-skill.sh')
        for text in ('\nUse Bloom.\n', '\nhttps://mcp.trybloom.ai/mcp\n',
                     '\nhttps://docs.trybloom.ai/\n'):
            with self.subTest(text=text):
                readme.write_text(original + text)
                self.run_script('package-skill.sh', succeeds=False)
        readme.write_text(original)
        canonical_path = self.root / 'skills/rainbrand/SKILL.md'
        canonical_path.write_text(canonical_path.read_text() + prose)
        self.run_script('package-skill.sh', succeeds=False)

    def test_bloom_corrupt_or_unexpected_archive_members(self):
        path = self.root / 'dist/bloom.skill.zip'
        with zipfile.ZipFile(path) as archive:
            original_member = archive.infolist()[0]
            original_data = archive.read(original_member)
        for mutation in ('extra', 'duplicate', 'wrapper', 'wrong-name', 'changed',
                         'symlink', 'traversal', 'stale-version', 'wrong-brand'):
            with self.subTest(mutation=mutation):
                member = copy.copy(original_member)
                data = original_data
                if mutation == 'wrapper':
                    member.filename = 'wrapper/bloom/SKILL.md'
                if mutation == 'wrong-name':
                    member.filename = 'rainbrand/SKILL.md'
                if mutation == 'changed':
                    data = data.replace(b'`onboard_brand`', b'`old_tool`')
                if mutation == 'stale-version':
                    data = data.replace(self.manifest['version'].encode(), b'1.0.6')
                if mutation == 'wrong-brand':
                    data = data.replace(b'Bloom', b'Rainbrand')
                if mutation == 'symlink':
                    member.external_attr = (stat.S_IFLNK | 0o777) << 16
                with warnings.catch_warnings(), zipfile.ZipFile(path, 'w') as archive:
                    warnings.simplefilter('ignore', UserWarning)
                    archive.writestr(member, data)
                    if mutation == 'extra':
                        archive.writestr('extra.txt', 'extra')
                    if mutation == 'duplicate':
                        archive.writestr(member, data)
                    if mutation == 'traversal':
                        archive.writestr('../outside', 'extra')
                self.run_script('validate-skills.sh', succeeds=False)
                self.run_script('validate-plugin.sh', succeeds=False)
                self.run_script('validate-claude-plugin.sh', succeeds=False)
        path.write_bytes(b'Not a ZIP')
        self.run_script('validate-skills.sh', succeeds=False)

    def test_release_requires_exact_asset_filenames(self):
        expected = {'bloom.skill.zip', 'rainbrand.skill.zip',
                    'rainbrand.plugin.zip', 'rainbrand.claude-plugin.zip'}
        self.run_script('package-release.sh')
        self.assertEqual({path.name for path in (self.root / 'dist').iterdir()}, expected)
        bloom_path = self.root / 'dist/bloom.skill.zip'
        bloom_path.rename(self.root / 'dist/Bloom.skill.zip')
        self.run_script('validate-release.sh', succeeds=False)
        self.run_script('validate-skills.sh', succeeds=False)
        (self.root / 'dist/Bloom.skill.zip').unlink()
        self.run_script('package-release.sh')
        self.assertEqual({path.name for path in (self.root / 'dist').iterdir()}, expected)
        (self.root / 'dist/unexpected.zip').write_bytes(b'Extra')
        self.run_script('validate-release.sh', succeeds=False)

    def test_release_download_urls_and_zip_validation(self):
        fake_bin = Path(self.temp.name) / 'bin'
        fake_bin.mkdir()
        log = Path(self.temp.name) / 'curl-calls.jsonl'
        curl = fake_bin / 'curl'
        curl.write_text(
            '#!/usr/bin/env python3\n'
            'import json, os, sys\nfrom pathlib import Path\n'
            'args = sys.argv[1:]\n'
            'with open(os.environ["CURL_CALL_LOG"], "a") as log:\n'
            '    log.write(json.dumps(args) + "\\n")\n'
            'output = Path(args[args.index("--output") + 1])\n'
            'output.write_bytes((Path(os.environ["RELEASE_FIXTURES"]) / output.name).read_bytes())\n'
        )
        curl.chmod(0o755)
        environment = {**os.environ, 'PATH': str(fake_bin) + os.pathsep + os.environ['PATH'],
                       'CURL_CALL_LOG': str(log), 'RELEASE_FIXTURES': str(self.root / 'dist')}
        self.run_script('verify-release-downloads.sh', env=environment)
        calls = [json.loads(line) for line in log.read_text().splitlines()]
        self.assertEqual([call[-1] for call in calls], [
            'https://github.com/trybloomai/rainbrand-skills/releases/latest/download/rainbrand.skill.zip',
            'https://github.com/trybloomai/bloom-skills/releases/latest/download/bloom.skill.zip',
        ])
        for call in calls:
            self.assertIn('--fail', call)
            self.assertIn('--location', call)
        # An HTTP success containing a bad ZIP must still fail verification.
        (self.root / 'dist/bloom.skill.zip').write_bytes(b'Not a ZIP')
        self.run_script('verify-release-downloads.sh', env=environment, succeeds=False)


if __name__ == '__main__':
    unittest.main(verbosity=2)
