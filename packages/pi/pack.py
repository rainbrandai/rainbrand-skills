#!/usr/bin/env python3
"""Build the Pi tarball from canonical sources in a temporary package root."""

import argparse
import json
from pathlib import Path
import runpy
import subprocess
import tarfile
import tempfile


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SKILL = 'skills/rainbrand/SKILL.md'


def pack(destination):
    renderer = runpy.run_path(str(ROOT / 'scripts/render-plugin-manifests.py'))
    skill = renderer['read_skill_metadata']()
    config = renderer['read_json'](ROOT / 'plugin-config.json')['mcp']
    manifest = renderer['read_json'](PACKAGE / 'package.template.json')
    manifest.update({key: skill[key] for key in ('version', 'description', 'author', 'license')})
    expected = {
        'package.json': renderer['render'](manifest).encode('utf-8'),
        'mcp.json': renderer['render']({
            'mcpServers': {config['name']: {'url': config['endpoint']}},
        }).encode('utf-8'),
        SKILL: (ROOT / SKILL).read_bytes(),
        'extension.js': (PACKAGE / 'extension.js').read_bytes(),
        'README.md': (PACKAGE / 'README.md').read_bytes(),
        'LICENSE': (ROOT / 'LICENSE').read_bytes(),
    }

    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.rainbrand-pi-', dir=destination) as directory:
        staging = Path(directory)
        for name, contents in expected.items():
            path = staging / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(contents)
            path.chmod(0o644)

        result = subprocess.run(
            ['pnpm', 'pack', '--json'], cwd=staging, check=True,
            stdout=subprocess.PIPE, text=True,
        )
        tarball = staging / Path(json.loads(result.stdout)['filename']).name
        with tarfile.open(tarball, 'r:gz') as archive:
            members = archive.getmembers()
            if sorted(member.name for member in members) != sorted(f'package/{name}' for name in expected):
                raise ValueError('Unexpected Pi tarball contents')
            for member in members:
                name = member.name.removeprefix('package/')
                if not member.isfile():
                    raise ValueError(f'Expected a regular Pi tarball member: {member.name}')
                contents = archive.extractfile(member).read()
                # pnpm may rewrite the manifest's formatting during packing.
                matches = json.loads(contents) == manifest if name == 'package.json' else contents == expected[name]
                if not matches:
                    raise ValueError(f'Unexpected Pi tarball member: {member.name}')

        return tarball.replace(destination / tarball.name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path, help='directory for the validated tarball')
    args = parser.parse_args()
    print(pack(args.destination.resolve()))
