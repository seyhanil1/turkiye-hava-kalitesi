import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, channel="msedge")
    page = b.new_page(viewport={"width": 1400, "height": 1100})
    
    print("Testing homepage (overview)...")
    page.goto("http://localhost:8501/", wait_until="networkidle")
    time.sleep(4)
    
    content = page.content()
    assert "HAVAATLASI" in content, "Homepage failed to load"
    assert "DSÖ Kılavuz Standartları" in content, "Health shield section missing"
    
    page.screenshot(path="assets/rendered_overview_fixed.png", full_page=True)
    print("Homepage loaded perfectly without any NameError!")
    
    b.close()
