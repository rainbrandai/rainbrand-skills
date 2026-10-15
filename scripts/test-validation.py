#!/usr/bin/env python3
"""Regression checks for Rainbrand package generation and validation."""

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
SHARED_MEMBERS = [
    'skills/rainbrand/SKILL.md', 'README.md', 'CHANGELOG.md', 'LICENSE',
    'assets/rainbrand-logo.png',
]
PLUGIN_SPECS = {
    'codex': {
        'archive': 'rainbrand.codex-plugin.zip',
        'manifest': '.codex-plugin/plugin.json',
        'mcp': '.mcp.json',
        'package': 'package-codex-plugin.sh',
        'validate': 'validate-codex-plugin.sh',
    },
    'claude': {
        'archive': 'rainbrand.claude-plugin.zip',
        'manifest': '.claude-plugin/plugin.json',
        'mcp': '.mcp.json',
        'package': 'package-claude-plugin.sh',
        'validate': 'validate-claude-plugin.sh',
    },
    'cursor': {
        'archive': 'rainbrand.cursor-plugin.zip',
        'manifest': '.cursor-plugin/plugin.json',
        'mcp': 'mcp.json',
        'package': 'package-cursor-plugin.sh',
        'validate': 'validate-cursor-plugin.sh',
    },
}
EXPECTED_RELEASE_ASSETS = {
    'rainbrand.skill.zip', 'bloom.skill.zip',
    *(spec['archive'] for spec in PLUGIN_SPECS.values()),
}


class PackageValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='rainbrand-tests-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '.context'))
        self.manifests = {
            provider: json.loads((self.root / spec['manifest']).read_text())
            for provider, spec in PLUGIN_SPECS.items()
        }
        self.plugin_copy = json.loads((self.root / 'plugin-copy.json').read_text())
        self.plugin_config = json.loads((self.root / 'plugin-config.json').read_text())
        self.codex_mcp = json.loads((self.root / '.mcp.json').read_text())
        self.native_mcp = json.loads((self.root / 'mcp.json').read_text())
        self.run_script('package-release.sh')

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
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2) + '\n')

    def run_renderer(self, *args, succeeds=True):
        result = subprocess.run(
            ['python3', str(self.root / 'scripts/render-plugin-manifests.py'), *args],
            cwd=self.root, capture_output=True, text=True,
        )
        if succeeds:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def restore_manifest(self, provider):
        self.write_json(PLUGIN_SPECS[provider]['manifest'], self.manifests[provider])

    def archive_path(self, provider):
        return self.root / 'dist' / PLUGIN_SPECS[provider]['archive']

    def test_provider_manifest_contracts_reject_drift(self):
        mutations = {
            'codex': [
                ('version', '9.9.9'), ('name', 'other'), ('skills', './other/'),
                ('mcpServers', './mcp.json'), ('repository', 'https://example.com/repo'),
                ('description', 'Different plugin copy.'),
            ],
            'claude': [
                ('version', '9.9.9'), ('name', 'other'), ('displayName', ''),
                ('icon', './other.png'), ('repository', False),
                ('description', 'Different plugin copy.'),
            ],
            'cursor': [
                ('version', '9.9.9'), ('name', 'other'), ('skills', './other/'),
                ('mcpServers', './.mcp.json'), ('category', 'other'),
                ('logo', './assets/rainbrand-logo.png'),
                ('minClientVersions', {'cursor': '0.0.0'}),
                ('description', 'Different plugin copy.'),
            ],
        }
        for provider, changes in mutations.items():
            spec = PLUGIN_SPECS[provider]
            for field, value in changes:
                with self.subTest(provider=provider, field=field):
                    changed = copy.deepcopy(self.manifests[provider])
                    changed[field] = value
                    self.write_json(spec['manifest'], changed)
                    self.run_script(spec['validate'], succeeds=False)
                    self.restore_manifest(provider)

    def test_plugin_copy_is_the_single_provider_prose_source(self):
        self.run_renderer('--check')

        validator = (self.root / 'scripts/validate-manifests.awk').read_text()
        interface = self.plugin_copy['codex']['interface']
        review = self.plugin_copy['codex']['review']
        prose = [
            interface['shortDescription'], interface['longDescription'],
            *interface['capabilities'], *interface['defaultPrompt'],
            review['commerce_description'],
            self.plugin_copy['codex']['publication']['release_notes'],
        ]
        for cases in review['test_cases'].values():
            for case in cases:
                prose.extend(value for key, value in case.items() if key != 'tools_triggered')
        for value in prose:
            with self.subTest(value=value[:40]):
                self.assertNotIn(value, validator)

        changed_copy = copy.deepcopy(self.plugin_copy)
        changed_copy['codex']['interface']['shortDescription'] = 'Canonical copy changed.'
        self.write_json('plugin-copy.json', changed_copy)
        self.run_renderer('--check', succeeds=False)
        self.run_script('package-codex-plugin.sh')
        rendered = json.loads((self.root / '.codex-plugin/plugin.json').read_text())
        self.assertEqual(rendered['interface']['shortDescription'], 'Canonical copy changed.')

        skill_path = self.root / 'skills/rainbrand/SKILL.md'
        original_description = self.manifests['codex']['description']
        replacement = 'Use the canonical Rainbrand package description.'
        skill_path.write_text(skill_path.read_text().replace(original_description, replacement, 1))
        self.run_renderer('--check', succeeds=False)
        self.run_renderer('--write')
        for spec in PLUGIN_SPECS.values():
            manifest = json.loads((self.root / spec['manifest']).read_text())
            self.assertEqual(manifest['description'], replacement)

    def test_mcp_outputs_share_one_endpoint_source(self):
        endpoint = self.plugin_config['mcp']['endpoint']
        validator = (self.root / 'scripts/validate-manifests.awk').read_text()
        self.assertNotIn(endpoint, validator)
        self.assertEqual(
            self.codex_mcp['mcpServers']['rainbrand']['url'], endpoint)
        self.assertEqual(
            self.native_mcp['mcpServers']['rainbrand']['url'], endpoint)

        changed_config = copy.deepcopy(self.plugin_config)
        changed_config['mcp']['endpoint'] = 'https://mcp.example.com/mcp'
        self.write_json('plugin-config.json', changed_config)
        self.run_renderer('--check', succeeds=False)
        self.run_script('package-codex-plugin.sh')
        for path in ('.mcp.json', 'mcp.json'):
            generated = json.loads((self.root / path).read_text())
            self.assertEqual(
                generated['mcpServers']['rainbrand']['url'],
                changed_config['mcp']['endpoint'],
            )

    def test_codex_submission_metadata_contract(self):
        manifest = self.manifests['codex']
        changes = []
        missing_video = copy.deepcopy(manifest)
        del missing_video['extensions']['com.openai']['review']['demo_recording_url']
        changes.append(('missing video', missing_video))
        four_positive = copy.deepcopy(manifest)
        four_positive['extensions']['com.openai']['review']['test_cases']['positive'].pop()
        changes.append(('four positive cases', four_positive))
        six_positive = copy.deepcopy(manifest)
        six_positive['extensions']['com.openai']['review']['test_cases']['positive'].append(
            copy.deepcopy(six_positive['extensions']['com.openai']['review']['test_cases']['positive'][0]))
        changes.append(('six positive cases', six_positive))
        wrong_tool = copy.deepcopy(manifest)
        wrong_tool['extensions']['com.openai']['review']['test_cases']['positive'][2]['tools_triggered'] = 'other'
        changes.append(('wrong tool', wrong_tool))
        missing_logo = copy.deepcopy(manifest)
        del missing_logo['interface']['logo']
        changes.append(('missing logo', missing_logo))
        missing_url = copy.deepcopy(manifest)
        del missing_url['interface']['privacyPolicyURL']
        changes.append(('missing listing URL', missing_url))
        commerce = copy.deepcopy(manifest)
        commerce['extensions']['com.openai']['review']['commerce'] = True
        changes.append(('commerce declaration', commerce))
        long_subtitle = copy.deepcopy(manifest)
        long_subtitle['interface']['shortDescription'] = 'x' * 31
        changes.append(('long subtitle', long_subtitle))
        bad_prompt = copy.deepcopy(manifest)
        bad_prompt['interface']['defaultPrompt'][0] = '@rainbrand show brands'
        changes.append(('changed starter prompt', bad_prompt))

        for label, changed in changes:
            with self.subTest(label=label):
                self.write_json('.codex-plugin/plugin.json', changed)
                self.run_script('validate-codex-plugin.sh', succeeds=False)
                self.restore_manifest('codex')

        self.assertEqual(
            manifest['extensions']['com.openai']['review']['demo_recording_url'],
            self.plugin_copy['codex']['review']['demo_recording_url'],
        )
        self.assertEqual(
            len(manifest['extensions']['com.openai']['review']['test_cases']['positive']), 5)
        self.assertEqual(
            len(manifest['extensions']['com.openai']['review']['test_cases']['negative']), 3)

    def test_malformed_and_duplicate_json_is_rejected(self):
        for provider, spec in PLUGIN_SPECS.items():
            original = json.dumps(self.manifests[provider])
            payloads = (
                '{"name":"rainbrand","name":"rainbrand"}',
                '{"name":"rainbrand",}',
                original + ' null',
                original.replace('Rainbrand', r'\u0042loom'),
            )
            for payload in payloads:
                with self.subTest(provider=provider, payload=payload[:30]):
                    (self.root / spec['manifest']).write_text(payload)
                    self.run_script(spec['validate'], succeeds=False)
                    self.restore_manifest(provider)

    def test_mcp_contract_and_provider_parity(self):
        codex_server = self.codex_mcp['mcpServers']['rainbrand']
        codex_changes = [
            {}, {'mcpServers': []}, {'mcpServers': {}},
            {'mcpServers': {'other': codex_server}},
            {'mcpServers': {'rainbrand': codex_server, 'extra': codex_server}},
            {'mcpServers': {'rainbrand': {**codex_server, 'type': 'http'}}},
            {'mcpServers': {'rainbrand': {**codex_server, 'url': 'https://example.com/mcp'}}},
        ]
        for changed in codex_changes:
            with self.subTest(changed=changed):
                self.write_json('.mcp.json', changed)
                self.run_script('validate-codex-plugin.sh', succeeds=False)
                self.write_json('.mcp.json', self.codex_mcp)

        native_server = self.native_mcp['mcpServers']['rainbrand']
        native_changes = [
            {}, {'mcpServers': []}, {'mcpServers': {}},
            {'mcpServers': {'other': native_server}},
            {'mcpServers': {'rainbrand': native_server, 'extra': native_server}},
            {'mcpServers': {'rainbrand': {**native_server, 'type': 'streamable-http'}}},
            {'mcpServers': {'rainbrand': {**native_server, 'url': 'https://example.com/mcp'}}},
            {'mcpServers': {'rainbrand': {**native_server, 'headers': {'Authorization': 'invalid'}}}},
        ]
        for changed in native_changes:
            with self.subTest(changed=changed):
                self.write_json('mcp.json', changed)
                self.run_script('validate-claude-plugin.sh', succeeds=False)
                self.run_script('validate-cursor-plugin.sh', succeeds=False)
                self.write_json('mcp.json', self.native_mcp)

        codex_url = self.codex_mcp['mcpServers']['rainbrand']['url']
        native_url = self.native_mcp['mcpServers']['rainbrand']['url']
        self.assertEqual(codex_url, native_url)
        self.assertEqual(codex_url, self.plugin_config['mcp']['endpoint'])

    def test_root_portable_manifest_is_retired(self):
        self.assertFalse((self.root / 'plugin.json').exists())
        (self.root / 'plugin.json').write_text('{}\n')
        self.run_script('package-skill.sh', succeeds=False)
        for spec in PLUGIN_SPECS.values():
            self.run_script(spec['package'], succeeds=False)

    def test_source_symlinks_extra_files_and_extra_skills(self):
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
        (self.root / 'skills/extra').rmdir()

        (self.root / 'skills/bloom/extra.md').write_text('Unexpected source.\n')
        self.run_script('package-skill.sh', succeeds=False)
        (self.root / 'skills/bloom/extra.md').unlink()

        (self.root / '.cursor-plugin/extra.json').write_text('{}\n')
        self.run_script('package-cursor-plugin.sh', succeeds=False)

    def test_archives_have_exact_members_modes_timestamps_and_source_bytes(self):
        canonical_skill = (self.root / 'skills/rainbrand/SKILL.md').read_bytes()
        for provider, spec in PLUGIN_SPECS.items():
            expected = [spec['manifest'], spec['mcp'], *SHARED_MEMBERS]
            with self.subTest(provider=provider), zipfile.ZipFile(self.archive_path(provider)) as archive:
                self.assertEqual(archive.namelist(), expected)
                self.assertEqual(archive.read('skills/rainbrand/SKILL.md'), canonical_skill)
                for member in archive.infolist():
                    self.assertEqual(member.date_time, (1980, 1, 1, 0, 0, 0))
                    self.assertEqual(stat.S_IMODE(member.external_attr >> 16), 0o644)
                    source = member.filename
                    if provider == 'claude' and source == '.mcp.json':
                        source = 'mcp.json'
                    self.assertEqual(archive.read(member), (self.root / source).read_bytes())

        with zipfile.ZipFile(self.root / 'dist/rainbrand.skill.zip') as archive:
            self.assertEqual(archive.namelist(), ['rainbrand/SKILL.md'])
            self.assertEqual(archive.read('rainbrand/SKILL.md'), canonical_skill)

        bloom_skill = (self.root / 'skills/bloom/SKILL.md').read_bytes()
        with zipfile.ZipFile(self.root / 'dist/bloom.skill.zip') as archive:
            self.assertEqual(archive.namelist(), ['bloom/SKILL.md'])
            self.assertEqual(archive.read('bloom/SKILL.md'), bloom_skill)

    def test_corrupt_or_unexpected_members_fail_each_provider(self):
        for provider, spec in PLUGIN_SPECS.items():
            source = self.archive_path(provider)
            with zipfile.ZipFile(source) as archive:
                originals = [(member, archive.read(member)) for member in archive.infolist()]
            for mutation in ('extra', 'duplicate', 'wrapper', 'changed-skill', 'symlink', 'traversal'):
                with self.subTest(provider=provider, mutation=mutation):
                    candidate = self.root / f'{provider}-candidate.zip'
                    with warnings.catch_warnings(), zipfile.ZipFile(candidate, 'w') as archive:
                        warnings.simplefilter('ignore', UserWarning)
                        for original_member, original_data in originals:
                            member = copy.copy(original_member)
                            data = original_data
                            if mutation == 'wrapper':
                                member.filename = 'wrapper/' + member.filename
                            if mutation == 'changed-skill' and member.filename == 'skills/rainbrand/SKILL.md':
                                data += b'\nChanged bytes\n'
                            if mutation == 'symlink' and member.filename == 'README.md':
                                member.external_attr = (stat.S_IFLNK | 0o777) << 16
                            archive.writestr(member, data)
                        if mutation == 'extra':
                            archive.writestr('extra.txt', 'extra')
                        if mutation == 'traversal':
                            archive.writestr('../outside', 'extra')
                        if mutation == 'duplicate':
                            archive.writestr(*originals[0])
                    self.run_script(spec['validate'], candidate, succeeds=False)
            candidate.write_bytes(b'Not a ZIP')
            self.run_script(spec['validate'], candidate, succeeds=False)

    def test_provider_archives_are_not_interchangeable(self):
        for provider, spec in PLUGIN_SPECS.items():
            for other_provider in PLUGIN_SPECS:
                if provider != other_provider:
                    with self.subTest(validator=provider, archive=other_provider):
                        self.run_script(
                            spec['validate'], self.archive_path(other_provider), succeeds=False)

    def test_stale_canonical_skill_fails_every_plugin(self):
        path = self.root / 'skills/rainbrand/SKILL.md'
        path.write_text(path.read_text() + '\nCanonical content changed.\n')
        for spec in PLUGIN_SPECS.values():
            self.run_script(spec['validate'], succeeds=False)

    def test_image_contract_and_archive_parity(self):
        path = self.root / 'assets/rainbrand-logo.png'
        original = path.read_bytes()
        path.write_bytes(original[:16] + b'\x00\x00\x00\x20' + original[20:])
        for spec in PLUGIN_SPECS.values():
            self.run_script(spec['package'], succeeds=False)
        path.write_bytes(original)
        path.unlink()
        for spec in PLUGIN_SPECS.values():
            self.run_script(spec['package'], succeeds=False)

    def test_reproducible_builds_across_timezone_and_umask(self):
        before = {path.name: path.read_bytes() for path in (self.root / 'dist').glob('*.zip')}
        self.assertEqual(set(before), EXPECTED_RELEASE_ASSETS)
        for timezone, mask in (('Pacific/Honolulu', '077'), ('Asia/Tokyo', '022')):
            environment = {**os.environ, 'TZ': timezone}
            command = f'umask {mask}; bash scripts/package-release.sh'
            subprocess.run(
                ['bash', '-c', command], cwd=self.root, env=environment,
                check=True, capture_output=True,
            )
            for name, contents in before.items():
                self.assertEqual((self.root / 'dist' / name).read_bytes(), contents)

    def test_bloom_skill_archive_matches_independent_source(self):
        source = (self.root / 'skills/bloom/SKILL.md').read_bytes()
        with zipfile.ZipFile(self.root / 'dist/bloom.skill.zip') as archive:
            self.assertEqual(archive.namelist(), ['bloom/SKILL.md'])
            bloom = archive.read('bloom/SKILL.md')
        self.assertEqual(bloom, source)
        self.assertNotIn(b'rainbrand', bloom.lower())

    def test_rainbrand_changes_do_not_change_bloom_skill_archive(self):
        bloom_archive = self.root / 'dist/bloom.skill.zip'
        before = bloom_archive.read_bytes()
        rainbrand_skill = self.root / 'skills/rainbrand/SKILL.md'
        rainbrand_skill.write_text(
            rainbrand_skill.read_text() + '\nRainbrand-only guidance.\n')
        self.run_script('package-skill.sh')
        self.assertEqual(bloom_archive.read_bytes(), before)

    def test_skill_versions_can_move_independently(self):
        bloom_skill = self.root / 'skills/bloom/SKILL.md'
        lines = bloom_skill.read_text().splitlines()
        version_index = next(
            index for index, line in enumerate(lines)
            if line.startswith('  version: ')
        )
        lines[version_index] = '  version: "1.0.0"'
        bloom_skill.write_text('\n'.join(lines) + '\n')
        self.run_script('package-skill.sh')
        with zipfile.ZipFile(self.root / 'dist/bloom.skill.zip') as archive:
            self.assertEqual(
                archive.read('bloom/SKILL.md'), bloom_skill.read_bytes())

    def test_skill_description_keeps_correct_media_scope(self):
        skill = (self.root / 'skills/rainbrand/SKILL.md').read_text()
        description = next(line for line in skill.splitlines() if line.startswith('description: '))
        description = description.split(': ', 1)[1]
        self.assertIn('images, videos, and audio', description)
        self.assertNotIn('SVG', description)
        for provider, manifest in self.manifests.items():
            with self.subTest(provider=provider):
                self.assertEqual(manifest['description'], description)

    def test_branding_compatibility_prose_is_scoped(self):
        readme = self.root / 'README.md'
        original = readme.read_text()
        allowed = '\nFor Bloom compatibility, `bloom.skill.zip` contains `bloom/SKILL.md` with Bloom identity.\n'
        readme.write_text(original + allowed)
        self.run_script('package-skill.sh')
        for text in ('\nUse Bloom.\n', '\nhttps://mcp.trybloom.ai/mcp\n'):
            with self.subTest(text=text):
                readme.write_text(original + text)
                self.run_script('package-skill.sh', succeeds=False)

    def test_release_requires_exact_asset_filenames(self):
        self.assertEqual({path.name for path in (self.root / 'dist').iterdir()}, EXPECTED_RELEASE_ASSETS)
        path = self.root / 'dist/rainbrand.codex-plugin.zip'
        path.rename(self.root / 'dist/rainbrand.plugin.zip')
        self.run_script('validate-release.sh', succeeds=False)
        (self.root / 'dist/rainbrand.plugin.zip').unlink()
        self.run_script('package-release.sh')
        (self.root / 'dist/unexpected.zip').write_bytes(b'Extra')
        self.run_script('validate-release.sh', succeeds=False)

    def test_release_download_urls_and_archive_validation(self):
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
        environment = {
            **os.environ,
            'PATH': str(fake_bin) + os.pathsep + os.environ['PATH'],
            'CURL_CALL_LOG': str(log),
            'RELEASE_FIXTURES': str(self.root / 'dist'),
        }
        self.run_script('verify-release-downloads.sh', env=environment)
        calls = [json.loads(line) for line in log.read_text().splitlines()]
        self.assertEqual([call[-1] for call in calls], [
            'https://github.com/trybloomai/rainbrand-skills/releases/latest/download/rainbrand.skill.zip',
            'https://github.com/trybloomai/rainbrand-skills/releases/latest/download/rainbrand.codex-plugin.zip',
            'https://github.com/trybloomai/rainbrand-skills/releases/latest/download/rainbrand.claude-plugin.zip',
            'https://github.com/trybloomai/rainbrand-skills/releases/latest/download/rainbrand.cursor-plugin.zip',
            'https://github.com/trybloomai/bloom-skills/releases/latest/download/bloom.skill.zip',
        ])
        for call in calls:
            self.assertIn('--fail', call)
            self.assertIn('--location', call)
        (self.root / 'dist/rainbrand.cursor-plugin.zip').write_bytes(b'Not a ZIP')
        self.run_script('verify-release-downloads.sh', env=environment, succeeds=False)

    def test_readme_names_only_supported_distributions(self):
        readme = (self.root / 'README.md').read_text()
        customer_assets = EXPECTED_RELEASE_ASSETS - {'bloom.skill.zip'}
        for asset in customer_assets:
            self.assertIn(asset, readme)
        self.assertNotIn('bloom.skill.zip', readme)
        self.assertNotIn('rainbrand.plugin.zip', readme)
        self.assertNotIn('Portable plugin', readme)
        self.assertNotIn('Agent Plugins 1.0', readme)


if __name__ == '__main__':
    unittest.main(verbosity=2)
