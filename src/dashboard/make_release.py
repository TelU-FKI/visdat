#!/usr/bin/env python3
"""Package the offline dashboard runtime into dist/jarvis-ihsg."""
from __future__ import annotations
import argparse
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DASHBOARD = ROOT / 'dashboard'
DEFAULT_RELEASE = ROOT / 'dist' / 'jarvis-ihsg'
RUNTIME_JS = (
    'bus.js', 'sphere.js', 'ranks.js', 'timeline.js', 'heat.js',
    'headlines.js', 'network.js', 'app.js', 'core3d.js', 'intro.js',
    'p1-init.js', 'core-glb-data.js',
)
RUNTIME_CSS = ('hud.css', 'p1-sphere.css')
FIXTURE_SCRIPT = re.compile(
    r'<script src="data/data\.js"></script>\s*<script src="data/fixture\.data\.js"></script>'
)
INLINE_FIXTURE_SCRIPT = re.compile(
    r'<script>\s*if\(new URLSearchParams\(location\.search\)\.get\("fixture"\)==="1"\)document\.write\(.*?</script>'
)


def build_release(destination: Path = DEFAULT_RELEASE) -> tuple[Path, int]:
    destination = Path(destination).resolve()
    if destination == ROOT or destination == DASHBOARD:
        raise ValueError('Release destination must be a dedicated output directory.')
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)

    source_html = (DASHBOARD / 'index.html').read_text(encoding='utf-8')
    packaged_html, inline_replacements = INLINE_FIXTURE_SCRIPT.subn('', source_html)
    packaged_html, legacy_replacements = FIXTURE_SCRIPT.subn(
        '<script src="data/data.js"></script>', packaged_html
    )
    if inline_replacements + legacy_replacements != 1:
        raise RuntimeError('Expected to remove exactly one fixture script reference from packaged HTML.')
    (destination / 'index.html').write_text(packaged_html, encoding='utf-8')

    for name in RUNTIME_CSS:
        source = DASHBOARD / 'css' / name
        if not source.is_file():
            raise FileNotFoundError(f'Missing runtime stylesheet: {source}')
        target = destination / 'css' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    for name in RUNTIME_JS:
        source = DASHBOARD / 'js' / name
        if not source.is_file():
            raise FileNotFoundError(f'Missing runtime script: {source}')
        target = destination / 'js' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    for directory in ('vendor', 'assets'):
        source = DASHBOARD / directory
        if not source.is_dir():
            raise FileNotFoundError(f'Missing runtime directory: {source}')
        shutil.copytree(source, destination / directory)

    data_source = DASHBOARD / 'data' / 'data.js'
    if not data_source.is_file():
        raise FileNotFoundError(f'Missing browser data bundle: {data_source}')
    (destination / 'data').mkdir()
    shutil.copy2(data_source, destination / 'data' / 'data.js')

    forbidden = ('qa', 'blender', 'p1-test.html', 'fixture.data.js', 'sample.data.js')
    present = [name for name in forbidden if (destination / name).exists()]
    if present:
        raise RuntimeError(f'Non-runtime files leaked into release: {present}')
    total_bytes = sum(path.stat().st_size for path in destination.rglob('*') if path.is_file())
    return destination, total_bytes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_RELEASE)
    args = parser.parse_args()
    path, total_bytes = build_release(args.output_dir)
    print(f'Release: {path}')
    print(f'Total package size: {total_bytes:,} bytes ({total_bytes / (1024 * 1024):.2f} MiB)')
    print('Included runtime only: index.html, CSS, JS, vendor, assets, data/data.js.')


if __name__ == '__main__':
    main()
