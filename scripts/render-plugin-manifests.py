#!/usr/bin/env python3

"""Render provider manifests and MCP configs from canonical package sources."""

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = ROOT / 'skills/rainbrand/SKILL.md'
COPY_PATH = ROOT / 'plugin-copy.json'
CONFIG_PATH = ROOT / 'plugin-config.json'
OUTPUT_PATHS = {
    'codex': ROOT / '.codex-plugin/plugin.json',
    'claude': ROOT / '.claude-plugin/plugin.json',
    'cursor': ROOT / '.cursor-plugin/plugin.json',
    'cursor-archive': ROOT / '.cursor-plugin/archive-plugin.json',
    'codex-mcp': ROOT / '.codex-plugin/.mcp.json',
    'claude-mcp': ROOT / '.mcp.json',
    'portable': ROOT / 'plugin.json',
    'portable-mcp': ROOT / 'mcp.json',
    'claude-marketplace': ROOT / '.claude-plugin/marketplace.json',
}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=unique_object)


def yaml_scalar(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return json.loads(value)
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def read_skill_metadata():
    lines = SKILL_PATH.read_text().splitlines()
    if not lines or lines[0] != '---':
        raise ValueError(f'Missing Skill frontmatter: {SKILL_PATH}')
    try:
        end = lines.index('---', 1)
    except ValueError as error:
        raise ValueError(f'Unclosed Skill frontmatter: {SKILL_PATH}') from error

    metadata = {}
    in_metadata = False
    for line in lines[1:end]:
        if line == 'metadata:':
            in_metadata = True
            continue
        if line and not line.startswith(' '):
            in_metadata = False
        if in_metadata and line.startswith('  ') and ': ' in line:
            key, value = line.strip().split(': ', 1)
            metadata[key] = yaml_scalar(value)
        elif not in_metadata and ': ' in line:
            key, value = line.split(': ', 1)
            metadata[key] = yaml_scalar(value)

    required = ('name', 'description', 'license', 'author', 'version', 'url')
    missing = [key for key in required if not metadata.get(key)]
    if missing:
        raise ValueError(f'Missing Skill metadata: {", ".join(missing)}')
    return metadata


def build_outputs():
    skill = read_skill_metadata()
    copy = read_json(COPY_PATH)
    config = read_json(CONFIG_PATH)
    shared = copy['shared']
    claude = copy['claude']
    codex = copy['codex']
    cursor = copy['cursor']
    mcp = config['mcp']

    author = {'name': skill['author'], 'url': shared['homepage']}
    identity = {
        'name': skill['name'],
        'version': skill['version'],
        'description': skill['description'],
    }
    repository_fields = {
        'homepage': shared['homepage'],
        'repository': shared['repository'],
        'license': skill['license'],
    }

    interface_copy = codex['interface']
    codex_manifest = {
        **identity,
        'author': author,
        **repository_fields,
        'keywords': codex['keywords'],
        'skills': './skills/',
        'mcpServers': './.mcp.json',
        'interface': {
            'displayName': shared['displayName'],
            'shortDescription': interface_copy['shortDescription'],
            'longDescription': interface_copy['longDescription'],
            'developerName': skill['author'],
            'category': interface_copy['category'],
            'capabilities': interface_copy['capabilities'],
            'websiteURL': shared['homepage'],
            'supportURL': shared['supportUrl'],
            'privacyPolicyURL': shared['privacyPolicyUrl'],
            'termsOfServiceURL': shared['termsOfServiceUrl'],
            'defaultPrompt': interface_copy['defaultPrompt'],
            'logo': './assets/rainbrand-logo.png',
            'composerIcon': './assets/rainbrand-logo.png',
        },
        'extensions': {
            'com.openai': {
                'review': codex['review'],
                'publication': codex['publication'],
            }
        },
    }

    claude_manifest = {
        'name': skill['name'],
        'displayName': shared['displayName'],
        'version': skill['version'],
        'description': claude['description'],
        'author': author,
        **repository_fields,
        'icon': './assets/rainbrand-logo.png',
        'documentationUrl': skill['url'],
        'supportUrl': shared['supportUrl'],
        'privacyPolicyUrl': shared['privacyPolicyUrl'],
        'termsOfServiceUrl': shared['termsOfServiceUrl'],
    }

    cursor_manifest = {
        'name': skill['name'],
        'displayName': shared['displayName'],
        'version': skill['version'],
        'minClientVersions': {'cursor': cursor['minimumVersion']},
        'description': skill['description'],
        'author': {'name': skill['author']},
        **repository_fields,
        'logo': 'assets/rainbrand-logo.png',
        'keywords': cursor['keywords'],
        'category': cursor['category'],
        'tags': cursor['tags'],
        'skills': './skills/',
        'mcpServers': './.mcp.json',
    }
    # Keep existing Cursor ZIPs identical while repository installs use the
    # native config separately from the portable root mcp.json.
    cursor_archive_manifest = {**cursor_manifest, 'mcpServers': './mcp.json'}

    codex_mcp = {
        'mcpServers': {
            mcp['name']: {
                'url': mcp['endpoint'],
            },
        },
    }
    native_mcp = {
        'mcpServers': {
            mcp['name']: {
                'type': 'http',
                'url': mcp['endpoint'],
            },
        },
    }

    portable_manifest = {
        '$schema': 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json',
        **identity,
        'author': author,
        **repository_fields,
        'keywords': codex['keywords'],
        'extensions': {
            'com.openai': {
                'interface': codex_manifest['interface'],
                **codex_manifest['extensions']['com.openai'],
            },
        },
    }
    portable_mcp = {
        '$schema': 'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json',
        'mcpServers': {
            mcp['name']: {
                'type': 'streamable-http',
                'url': mcp['endpoint'],
            },
        },
    }
    claude_marketplace = {
        'name': skill['name'],
        'owner': author,
        'description': claude['description'],
        'plugins': [{'name': skill['name'], 'source': './claude'}],
    }

    return {
        'codex': codex_manifest,
        'claude': claude_manifest,
        'cursor': cursor_manifest,
        'cursor-archive': cursor_archive_manifest,
        'codex-mcp': codex_mcp,
        'claude-mcp': native_mcp,
        'portable': portable_manifest,
        'portable-mcp': portable_mcp,
        'claude-marketplace': claude_marketplace,
    }


def render(manifest):
    return json.dumps(manifest, indent=2, ensure_ascii=False) + '\n'


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true', help='fail if generated plugin files are stale')
    mode.add_argument('--write', action='store_true', help='rewrite generated provider files')
    args = parser.parse_args()
    check = not args.write

    stale = []
    for output, document in build_outputs().items():
        path = OUTPUT_PATHS[output]
        expected = render(document)
        if check:
            if not path.is_file() or path.read_text() != expected:
                stale.append(path.relative_to(ROOT))
        else:
            if path.parent.is_symlink() or not path.parent.is_dir():
                raise ValueError(f'Expected a regular output directory: {path.parent}')
            if path.is_symlink() or (path.exists() and not path.is_file()):
                raise ValueError(f'Expected a regular output file: {path}')
            path.write_text(expected)

    if stale:
        names = ', '.join(map(str, stale))
        print(f'Generated plugin file is stale: {names}', file=sys.stderr)
        print('Run: python3 scripts/render-plugin-manifests.py --write', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
