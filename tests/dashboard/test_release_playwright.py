import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / 'dist' / 'jarvis-ihsg'
CHROME_CANDIDATES = (
    os.environ.get('CHROME_BIN'),
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    shutil.which('google-chrome'),
    shutil.which('google-chrome-stable'),
    shutil.which('chromium'),
    shutil.which('chromium-browser'),
)


def test_release_opens_offline_without_console_or_http_errors():
    playwright_api = pytest.importorskip('playwright.sync_api')
    chrome = next((Path(item) for item in CHROME_CANDIDATES if item and Path(item).is_file()), None)
    if chrome is None:
        pytest.skip('No Chrome/Chromium executable is available for the offline release check.')

    package = subprocess.run(
        [sys.executable, str(ROOT / 'src/dashboard/make_release.py')],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert 'Total package size:' in package.stdout
    assert (RELEASE / 'index.html').is_file()
    assert not (RELEASE / 'data' / 'fixture.data.js').exists()
    assert not (RELEASE / 'data' / 'sample.data.js').exists()
    assert not (RELEASE / 'qa').exists()
    assert not (RELEASE / 'blender').exists()
    assert 'fixture.data.js' not in (RELEASE / 'index.html').read_text(encoding='utf-8')

    http_requests = []
    console_errors = []
    page_errors = []
    with playwright_api.sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=str(chrome))
        context = browser.new_context(viewport={'width': 1280, 'height': 720})

        def block_http(route):
            if route.request.url.startswith(('http://', 'https://')):
                http_requests.append(route.request.url)
                route.abort()
            else:
                route.continue_()

        context.route('**/*', block_http)
        page = context.new_page()
        page.on('console', lambda message: console_errors.append(message.text) if message.type == 'error' else None)
        page.on('pageerror', lambda error: page_errors.append(str(error)))
        page.goto((RELEASE / 'index.html').resolve().as_uri(), wait_until='load', timeout=45_000)
        page.wait_for_function('window.IHSG_DATA && window.Panels && document.querySelector("#month-readout")', timeout=20_000)
        page.wait_for_timeout(7_000)
        assert page.evaluate('window.IHSG_DATA.meta.months.length') == 11
        assert page.evaluate('window.IHSG_DATA.meta.khas.formula') == 'df_share × log(M / support)'
        assert http_requests == []
        assert console_errors == []
        assert page_errors == []
        print('Playwright file:// release check: 0 HTTP(S) requests, 0 console errors, 0 page errors.')
        context.close()
        browser.close()
