import sys, time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel="msedge")
    page = browser.new_page(viewport={"width": 1400, "height": 950})
    page.goto("http://localhost:8501/?page=genel_bakis", wait_until="networkidle")
    time.sleep(3)
    
    wrap = page.locator(".future-showcase-wrap")
    wrap.scroll_into_view_if_needed()
    time.sleep(1)
    page.screenshot(path="assets/rendered_overview_showcase_centered.png", full_page=False)
    print("Captured centered showcase screenshot with scroll_into_view_if_needed!")
    browser.close()
