from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    
    console_logs = []
    page.on('console', lambda msg: console_logs.append(f'[{msg.type}] {msg.text}'))
    page.on('pageerror', lambda err: console_logs.append(f'[PAGE_ERROR] {err}'))
    
    page.goto('http://localhost:8501', wait_until='networkidle')
    iframe = page.wait_for_selector('iframe', timeout=15000)
    frame = iframe.content_frame()
    frame.wait_for_selector('#mapContainer', timeout=15000)
    
    # Check elements inside iframe
    res = frame.evaluate('''() => {
        const mc = document.getElementById('mapContainer');
        const mw = document.getElementById('mapZoomWrapper');
        const svg = document.querySelector('.turkey-svg-map');
        const paths = document.querySelectorAll('.province-path');
        return {
            mapContainer: mc ? {
                offsetWidth: mc.offsetWidth,
                offsetHeight: mc.offsetHeight,
                clientWidth: mc.clientWidth,
                clientHeight: mc.clientHeight,
                display: window.getComputedStyle(mc).display,
                visibility: window.getComputedStyle(mc).visibility,
                height: window.getComputedStyle(mc).height,
                minHeight: window.getComputedStyle(mc).minHeight
            } : null,
            mapWrapper: mw ? {
                offsetWidth: mw.offsetWidth,
                offsetHeight: mw.offsetHeight,
                display: window.getComputedStyle(mw).display,
                transform: mw.style.transform
            } : null,
            svg: svg ? {
                getBoundingClientRect: svg.getBoundingClientRect(),
                clientWidth: svg.clientWidth,
                clientHeight: svg.clientHeight,
                display: window.getComputedStyle(svg).display,
                visibility: window.getComputedStyle(svg).visibility,
                opacity: window.getComputedStyle(svg).opacity,
                innerHTML_len: svg.innerHTML.length
            } : null,
            pathsCount: paths.length,
            path0: paths.length > 0 ? {
                fill: paths[0].style.fill,
                stroke: paths[0].style.stroke,
                computedFill: window.getComputedStyle(paths[0]).fill,
                computedStroke: window.getComputedStyle(paths[0]).stroke
            } : null
        };
    }''')
    print('Console logs:', console_logs)
    print('DOM res:', res)
    page.screenshot(path='scratch/debug_disappear.png')
    browser.close()
