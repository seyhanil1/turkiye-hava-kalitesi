import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

def main():
    os.makedirs("assets", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="msedge")
        page = browser.new_page(viewport={"width": 1400, "height": 1150})
        
        print("Navigating to http://localhost:8501/?page=future_2035...")
        page.goto("http://localhost:8501/?page=future_2035", wait_until="networkidle")
        time.sleep(3)

        # 1. Option A (Temiz Gelecek - 2026)
        print("Checking Option A (Temiz Gelecek - 2026)...")
        content = page.content()
        assert "2035: Türkiye'nin Gelecek Yol Ayrımı" in content, "Header missing"
        assert "İnsanların ve Toplumun Yaptıkları" in content, "Left card missing"
        assert "Kazanılan Hayatlar ve Refah" in content, "Right card missing"
        assert "N95 maske" in content, "2026 action detail missing"
        
        page.screenshot(path="assets/rendered_future_fork_clean_2026.png", full_page=True)
        print("Captured screenshot: clean 2026.")

        # 2. Switch to Option B (Gri Gelecek)
        print("Switching to Option B (Gri Gelecek)...")
        # In Streamlit, radio items have role="radiogroup"
        gray_option = page.locator('label').filter(has_text="Gri Gelecek").first
        gray_option.click()
        time.sleep(2)

        content = page.content()
        assert "Yapılan Hatalar ve İhmal Edilen Uyarılar" in content, "Gray left card missing"
        assert "Ağır Bedel ve Önlenemeyen Kayıplar" in content, "Gray right card missing"
        assert "kalitesiz linyit" in content, "Gray 2026 action missing"

        page.screenshot(path="assets/rendered_future_fork_gray_2026.png", full_page=True)
        print("Captured screenshot: gray 2026.")

        browser.close()
        print("All visual assertions and interactions passed completely!")

if __name__ == "__main__":
    main()
