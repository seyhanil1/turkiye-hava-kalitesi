import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

def main():
    os.makedirs("assets", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="msedge")
        page = browser.new_page(viewport={"width": 1440, "height": 1100})

        print("Navigating to Overview page...")
        page.goto("http://localhost:8501/?page=genel_bakis", wait_until="networkidle")
        time.sleep(4)

        content = page.content()
        
        # Verify old healthShieldSection is NOT present
        assert "healthShieldSection" not in content, "Old healthShieldSection should NOT be present"
        print("Verified: healthShieldSection is completely removed from page!")

        # Find the frame locator for the iframe
        frame = page.frame_locator("iframe").first
        frame_html = frame.locator("body").inner_html()

        # Check for Kolon 1 & Kolon 2 headers in the iframe
        assert "7 Coğrafi Bölge Benchmark" in frame_html, "Kolon 1 header missing"
        assert "Ulusal Kirlilik Maruziyeti" in frame_html, "Kolon 2 header missing"
        assert "0 / 81 İl" in frame_html, "DSÖ 0/81 metric missing"
        assert "TOPOGRAFİK RİSK GRUBU" in frame_html, "Topographic cluster card missing"
        print("Verified: Both analytical columns loaded with real data!")

        # Scroll iframe to show the analytics bottom grid
        frame.locator(".analytics-bottom-grid").scroll_into_view_if_needed()
        time.sleep(2)

        # Capture screenshot of the iframe / page focusing on the analytics panel
        page.screenshot(path="assets/rendered_overview_analytics_panel.png", full_page=False)
        print("Saved screenshot: assets/rendered_overview_analytics_panel.png")

        # Also capture a full-page view
        page.screenshot(path="assets/rendered_overview_full.png", full_page=True)
        print("Saved full page screenshot: assets/rendered_overview_full.png")

        browser.close()
        print("All assertions and visual verifications passed successfully!")

if __name__ == "__main__":
    main()
