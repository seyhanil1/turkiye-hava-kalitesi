import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel="msedge")
    page = browser.new_page(viewport={"width": 1440, "height": 1100})
    page.goto("http://localhost:8501/?page=genel_bakis", wait_until="networkidle")
    
    frame = page.frame_locator("iframe").first
    
    # Measure elements
    info = frame.locator("#mapContainer").evaluate("""el => {
        const rect = el.getBoundingClientRect();
        const svg = el.querySelector('svg');
        const svgRect = svg ? svg.getBoundingClientRect() : null;
        const g = el.querySelector('.provinces-layer');
        const gRect = g ? g.getBoundingClientRect() : null;
        return {
            container: { width: rect.width, height: rect.height, left: rect.left, top: rect.top },
            svg: svgRect ? { width: svgRect.width, height: svgRect.height, left: svgRect.left, top: svgRect.top } : null,
            provincesLayer: gRect ? { width: gRect.width, height: gRect.height, left: gRect.left, top: gRect.top } : null
        };
    }""")
    print("Measurements:", info)
    browser.close()
