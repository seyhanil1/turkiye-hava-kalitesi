import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, channel="msedge")
    page = b.new_page(viewport={"width": 1400, "height": 1100})
    page.goto("http://localhost:8501/?page=yesil_donusum", wait_until="networkidle")
    time.sleep(3)

    inp = page.locator('[data-testid="stSelectbox"] input')
    print("Initial value:", inp.input_value())
    inp.click()
    time.sleep(0.3)
    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")
    page.keyboard.type("Kocaeli")
    time.sleep(1)
    
    # Check what options are in the DOM
    options = page.locator('[role="option"]').all_inner_texts()
    print("Options found:", options)
    
    if options:
        page.locator('[role="option"]').first.click()
        time.sleep(3)
        print("After click, input value:", page.locator('[data-testid="stSelectbox"] input').input_value())
        page.screenshot(path="assets/debug_kocaeli_after.png", full_page=True)

    b.close()
