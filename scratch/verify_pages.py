import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    
    # 1. TEST EKONOMİ
    page = browser.new_page(viewport={'width': 1440, 'height': 1100})
    print("Navigating to ?page=ekonomi ...")
    page.goto('http://localhost:8501/?page=ekonomi', wait_until='networkidle')
    time.sleep(4)
    page.wait_for_selector('text=Hava Kirliliğinin Yıllık Ekonomik & Sağlık Faturası', timeout=10000)
    page.screenshot(path='scratch/screen_ekonomi.png', full_page=True)
    print("Saved scratch/screen_ekonomi.png")
    page.close()

    # 2. TEST SANAYİ PROFİLİ
    page2 = browser.new_page(viewport={'width': 1440, 'height': 1100})
    print("Navigating to ?page=sanayi_profili ...")
    page2.goto('http://localhost:8501/?page=sanayi_profili', wait_until='networkidle')
    time.sleep(4)
    page2.wait_for_selector('text=Sanayi Baskısı, OSB Kümeleri & Çevre Karnesi', timeout=10000)
    page2.screenshot(path='scratch/screen_sanayi.png', full_page=True)
    print("Saved scratch/screen_sanayi.png")
    page2.close()

    browser.close()
