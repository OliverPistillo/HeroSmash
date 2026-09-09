"""Verify the installed source identity and pinned runtime distributions."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--installation', type=Path, required=True)
    args = parser.parse_args()
    integration = Path(__file__).resolve().parent
    identity = json.loads((integration/'patch_identity.json').read_text())
    sha = lambda data: hashlib.sha256(data).hexdigest()
    patch = integration/identity['patch_file']
    assert sha(patch.read_bytes()) == identity['patch_sha256']
    src = args.installation/'src'
    git = lambda *a: subprocess.check_output(['git', '-C', str(src), *a])
    assert git('rev-parse', 'HEAD').decode().strip() == identity['upstream_commit']
    expected = sorted(row['path'] for row in identity['files'] if row['modified'])
    assert sorted(git('diff', '--name-only').decode().splitlines()) == expected
    from blender_mcp import server
    installed = Path(server.__file__).parent
    assert installed.resolve() == (args.installation/'venv/Lib/site-packages/blender_mcp').resolve()
    for row in identity['files']:
        rel = Path(row['path'])
        assert sha(git('show', identity['upstream_commit']+':'+row['path'])) == row['upstream_sha256']
        assert sha((src/rel).read_bytes()) == row['patched_and_installed_sha256']
        assert sha((installed/rel.relative_to('src/blender_mcp')).read_bytes()) == row['patched_and_installed_sha256']
    constraints = integration.parents[1]/'docs/codex/blender-mcp.dependencies.txt'
    count = 0
    for line in constraints.read_text().splitlines():
        if not line or line.startswith('#'):
            continue
        name, version = line.split('==')
        assert importlib.metadata.version(name) == version, line
        count += 1
    subprocess.run([sys.executable, '-m', 'pip', 'check'], check=True)
    print(json.dumps({'result': 'PASS', 'python': sys.executable,
                      'source_files_verified': len(identity['files']),
                      'patched_files': expected, 'runtime_versions_verified': count,
                      'patch_sha256': identity['patch_sha256']}, indent=2))

if __name__ == '__main__':
    main()
