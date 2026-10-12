import sys
from playwright.sync_api import sync_playwright
import time

sys.stdout.reconfigure(encoding='utf-8')

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, channel="msedge")
    page = b.new_page(viewport={"width": 1400, "height": 1100})
    page.goto("http://localhost:8501/?page=yesil_donusum", wait_until="networkidle")
    time.sleep(3)
    
    sel = page.locator('[data-testid="stSelectbox"]')
    print("Selectbox inner text:", sel.inner_text())

    # Check category
    content = page.content()
    if "Çanak Topoğrafyası" in content:
        print("FOUND: Çanak Topoğrafyası (Iğdır default)")
    elif "Ağır Sanayi" in content:
        print("FOUND: Ağır Sanayi")
    elif "Kentsel Yoğunluk" in content:
        print("FOUND: Kentsel Yoğunluk")
    else:
        print("NONE FOUND!")
    
    b.close()
