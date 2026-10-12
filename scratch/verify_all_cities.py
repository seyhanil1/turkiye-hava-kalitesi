import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

def main():
    os.makedirs("assets", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="msedge")
        page = browser.new_page(viewport={"width": 1400, "height": 1100})
        page.goto("http://localhost:8501/?page=yesil_donusum", wait_until="networkidle")
        time.sleep(3)

        # 1. Verify default Iğdır (Çanak)
        print("Checking default: Iğdır...")
        content = page.content()
        assert "Çanak Topoğrafyası" in content, "Iğdır should be diagnosed as Çanak Topoğrafyası"
        assert "+181 Kişi" in content, "Inaction deaths for Iğdır should be +181"
        assert "525.4 Milyon TL" in content, "Inaction cost for Iğdır should be 525.4"
        page.screenshot(path="assets/rendered_green_strategy_igdir.png", full_page=True)
        print("Verified Iğdır & captured screenshot.")

        # 2. Select Osmaniye (Ağır Sanayi)
        print("Selecting Osmaniye...")
        # In Streamlit, open the selectbox by clicking on it
        page.locator('[data-testid="stSelectbox"]').click()
        time.sleep(0.5)
        # Click the dropdown option for Osmaniye
        page.locator('li').filter(has_text="Osmaniye").click()
        time.sleep(2)

        content = page.content()
        assert "Ağır Sanayi & Endüstriyel Emisyon" in content, "Osmaniye should be Ağır Sanayi"
        assert "SEÖS" in content, "Osmaniye action items should contain SEÖS"
        page.screenshot(path="assets/rendered_green_strategy_osmaniye.png", full_page=True)
        print("Verified Osmaniye & captured screenshot.")

        # 3. Select İstanbul (Kentsel Yoğunluk)
        print("Selecting İstanbul...")
        page.locator('[data-testid="stSelectbox"]').click()
        time.sleep(0.5)
        page.locator('li').filter(has_text="İstanbul").click()
        time.sleep(2)

        content = page.content()
        assert "Kentsel Yoğunluk, Ulaşım & İnşaat Tozu" in content, "İstanbul should be Kentsel Yoğunluk"
        assert "Düşük Emisyon Bölgeleri" in content, "İstanbul action items should contain LEZ"
        page.screenshot(path="assets/rendered_green_strategy_istanbul.png", full_page=True)
        print("Verified İstanbul & captured screenshot.")

        browser.close()
        print("All 3 cities and categories verified perfectly!")

if __name__ == "__main__":
    main()
