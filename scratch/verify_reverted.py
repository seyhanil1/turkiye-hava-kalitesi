from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.goto('http://localhost:8501', wait_until='networkidle')
    iframe = page.wait_for_selector('iframe', timeout=20000)
    frame = iframe.content_frame()
    frame.wait_for_selector('#mapContainer', timeout=20000)
    time.sleep(1)

    res = frame.evaluate('''() => {
        const mc = document.getElementById('mapContainer');
        const mw = document.getElementById('mapZoomWrapper');
        const svg = document.querySelector('.turkey-svg-map');
        const paths = document.querySelectorAll('.province-path');
        return {
            mapContainer: mc ? {
                offsetWidth: mc.offsetWidth,
                offsetHeight: mc.offsetHeight,
                display: window.getComputedStyle(mc).display
            } : null,
            svg: svg ? {
                clientWidth: svg.clientWidth,
                clientHeight: svg.clientHeight,
                display: window.getComputedStyle(svg).display
            } : null,
            pathsCount: paths.length
        };
    }''')
    print('Reverted DOM res:', res)
    page.screenshot(path='scratch/reverted_page.png')
    print('Saved scratch/reverted_page.png')
    browser.close()
