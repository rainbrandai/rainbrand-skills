"""Regression tests for the published Pi package and temporary staging."""

from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
MEMBERS = {
    'package/package.json', 'package/extension.js', 'package/mcp.json',
    'package/skills/rainbrand/SKILL.md', 'package/README.md', 'package/LICENSE',
}


class PiPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='rainbrand-pi-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        for name in ('packages/pi', 'scripts/render-plugin-manifests.py',
                     'skills/rainbrand/SKILL.md', 'plugin-config.json', 'LICENSE'):
            source = ROOT / name
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__'))
            else:
                shutil.copyfile(source, target)
        spec = importlib.util.spec_from_file_location('pi_pack', self.root / 'packages/pi/pack.py')
        self.builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.builder)
        self.output = Path(self.temp.name) / 'output'

    def contents(self, tarball):
        with tarfile.open(tarball) as archive:
            self.assertEqual(set(archive.getnames()), MEMBERS)
            self.assertEqual(len(archive.getmembers()), len(MEMBERS))
            self.assertTrue(all(member.isfile() for member in archive.getmembers()))
            return {name: archive.extractfile(name).read() for name in MEMBERS}

    def assert_clean(self):
        self.assertFalse(list(self.output.glob('.rainbrand-pi-*')))
        self.assertFalse((self.root / 'packages/pi/skills').exists())
        self.assertFalse((self.root / 'packages/pi/mcp.json').exists())

    def test_tarball_contents_and_canonical_parity(self):
        contents = self.contents(self.builder.pack(self.output))
        manifest = json.loads(contents['package/package.json'])
        metadata = self.builder.runpy.run_path(str(self.root / 'scripts/render-plugin-manifests.py'))
        skill = metadata['read_skill_metadata']()
        for field in ('version', 'description', 'author', 'license'):
            self.assertEqual(manifest[field], skill[field])
        self.assertIn('pi-package', manifest['keywords'])
        self.assertEqual(manifest['pi'], {
            'extensions': ['./extension.js'], 'skills': ['./skills/rainbrand/SKILL.md'],
        })
        config = json.loads((self.root / 'plugin-config.json').read_text())['mcp']
        self.assertEqual(json.loads(contents['package/mcp.json']), {
            'mcpServers': {config['name']: {'url': config['endpoint']}},
        })
        for name in ('skills/rainbrand/SKILL.md', 'LICENSE'):
            self.assertEqual(contents[f'package/{name}'], (self.root / name).read_bytes())
        self.assert_clean()

    def test_canonical_updates_and_scope_change_flow_into_pack(self):
        skill = self.root / 'skills/rainbrand/SKILL.md'
        renderer = self.builder.runpy.run_path(str(self.root / 'scripts/render-plugin-manifests.py'))
        version = renderer['read_skill_metadata']()['version']
        skill.write_text(skill.read_text().replace(f'version: "{version}"', 'version: "9.8.7"'))
        (self.root / 'plugin-config.json').write_text(json.dumps({
            'mcp': {'name': 'renamed', 'endpoint': 'https://example.com/mcp'},
        }))
        template = self.root / 'packages/pi/package.template.json'
        manifest = json.loads(template.read_text())
        manifest['name'] = '@rainbrand/pi-plugin'
        template.write_text(json.dumps(manifest))
        contents = self.contents(self.builder.pack(self.output))
        packed = json.loads(contents['package/package.json'])
        self.assertEqual(packed['name'], '@rainbrand/pi-plugin')
        self.assertEqual(packed['version'], '9.8.7')
        self.assertEqual(json.loads(contents['package/mcp.json']), {
            'mcpServers': {'renamed': {'url': 'https://example.com/mcp'}},
        })

    def test_pack_is_reproducible_across_timezones_and_umasks(self):
        first = self.builder.pack(self.output).read_bytes()
        old_umask = os.umask(0o077)
        try:
            with patch.dict(os.environ, {'TZ': 'Pacific/Honolulu'}):
                second = self.builder.pack(self.output).read_bytes()
        finally:
            os.umask(old_umask)
        self.assertEqual(first, second)
        self.assert_clean()

    def test_concurrent_packs(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _: self.builder.pack(self.output).read_bytes(), range(2)))
        self.assertEqual(*results)
        self.assert_clean()

    def test_failed_pack_cleans_staging_and_preserves_previous_tarball(self):
        tarball = self.builder.pack(self.output)
        original = tarball.read_bytes()
        with patch.object(self.builder.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'pnpm')):
            with self.assertRaises(subprocess.CalledProcessError):
                self.builder.pack(self.output)
        self.assertEqual(tarball.read_bytes(), original)
        self.assert_clean()

    def test_invalid_archive_cleans_staging(self):
        real_run = subprocess.run

        def corrupt_archive(*args, **kwargs):
            result = real_run(*args, **kwargs)
            archive = Path(kwargs['cwd']) / json.loads(result.stdout)['filename']
            with tarfile.open(archive, 'w:gz'):
                pass
            return result

        with patch.object(self.builder.subprocess, 'run', side_effect=corrupt_archive):
            with self.assertRaisesRegex(ValueError, 'Unexpected Pi tarball contents'):
                self.builder.pack(self.output)
        self.assertEqual(list(self.output.iterdir()), [])
        self.assert_clean()

    def test_packed_extension_registers_native_mcp_and_warns_on_old_pi(self):
        tarball = self.builder.pack(self.output)
        extracted = Path(self.temp.name) / 'unpacked'
        with tarfile.open(tarball) as archive:
            archive.extractall(extracted, filter='data')
        result = subprocess.run(['node', '--input-type=module', '-e', '''
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import extension from './package/extension.js';
const config = JSON.parse(readFileSync('./package/mcp.json', 'utf8')).mcpServers;
const calls = [];
extension({ registerMcpServer: (...args) => calls.push(args) });
assert.deepEqual(calls, Object.entries(config));
let warned = false;
extension({ on(event, handler) {
  assert.equal(event, 'session_start');
  handler({}, { ui: { notify(message, level) {
    assert.match(message, /Pi 0.99.0/);
    assert.equal(level, 'warning');
    warned = true;
  } } });
} });
assert.equal(warned, true);
'''], cwd=extracted, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
