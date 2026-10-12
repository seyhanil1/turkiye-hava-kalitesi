"""
Playwright script to correctly click selectbox option in Streamlit.
"""

import os
import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="msedge")
        page = browser.new_page(viewport={"width": 1400, "height": 1100})
        page.goto("http://localhost:8501/?page=yesil_donusum", wait_until="networkidle")
        time.sleep(3)

        # 1. Verify default Iğdır
        print("Verifying Iğdır...")
        content = page.content()
        assert "Çanak Topoğrafyası & Evsel Katı Yakıt" in content
        assert "+181 Kişi" in content

        # 2. Select Osmaniye
        print("Selecting Osmaniye...")
        page.locator('div[data-baseweb="select"]').first.click()
        time.sleep(0.5)
        # Click option with text Osmaniye
        page.locator('li').filter(has_text="Osmaniye").first.click()
        time.sleep(2)

        content = page.content()
        assert "Ağır Sanayi & Endüstriyel Emisyon" in content, "Osmaniye diagnosis failed"
        assert "SEÖS" in content, "SEÖS action item failed"
        page.screenshot(path="assets/rendered_green_strategy_osmaniye.png", full_page=True)
        print("Osmaniye verified and screenshot captured!")

        # 3. Select İstanbul
        print("Selecting İstanbul...")
        page.locator('div[data-baseweb="select"]').first.click()
        time.sleep(0.5)
        page.locator('li').filter(has_text="İstanbul").first.click()
        time.sleep(2)

        content = page.content()
        assert "Kentsel Yoğunluk, Ulaşım & İnşaat Tozu" in content, "İstanbul diagnosis failed"
        assert "Düşük Emisyon Bölgeleri" in content, "LEZ action item failed"
        page.screenshot(path="assets/rendered_green_strategy_istanbul.png", full_page=True)
        print("İstanbul verified and screenshot captured!")

        browser.close()
        print("All tests passed completely!")

if __name__ == "__main__":
    main()
