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

        print("1. Testing Overview Page Showcase...")
        page.goto("http://localhost:8501/?page=genel_bakis", wait_until="networkidle")
        time.sleep(4)

        content = page.content()
        assert "2035: Türkiye'nin Gelecek Yol Ayrımı (Politika Simülatörü)" in content, "Showcase header missing"
        assert "+18.500 Kurtarılan Can" in content, "Showcase Clean KPI missing"
        assert "+145.000 Erken Ölüm" in content, "Showcase Gray KPI missing"
        assert "Gelecek Simülasyonunu Detaylı Keşfet" in content, "Showcase Redirect button missing"
        print("Overview showcase assertions passed!")

        # Scroll down slightly to capture the showcase section and take screenshot
        page.evaluate("window.scrollTo(0, 1000)")
        time.sleep(1)
        page.screenshot(path="assets/rendered_overview_showcase.png", full_page=False)
        print("Overview showcase screenshot saved: assets/rendered_overview_showcase.png")

        # Click the redirect button
        print("2. Testing Redirect Button...")
        redirect_btn = page.locator("button:has-text('Gelecek Simülasyonunu Detaylı Keşfet')").first
        redirect_btn.click()
        time.sleep(3)

        # Confirm we navigated to Future Fork page
        content_after_click = page.content()
        assert "🔮 2035: Türkiye'nin Gelecek Yol Ayrımı" in content_after_click, "Redirection failed to load Future Fork page"
        print("Redirect successfully navigated to Future Fork page!")

        # 3. Testing Future Fork Page Features & SVGs
        print("3. Testing Future Fork Page...")
        svg_count = page.locator("svg").count()
        print(f"SVGs detected on page: {svg_count}")
        assert svg_count >= 1, "At least 1 SVG illustration should be rendered"

        # Check clean path KPIs
        assert "18.500" in content_after_click or "Kurtarılan Can" in content_after_click, "Clean KPI missing"
        page.screenshot(path="assets/rendered_future_fork_svg_clean.png", full_page=True)
        print("Clean Future Fork screenshot saved: assets/rendered_future_fork_svg_clean.png")

        # 4. Switch to Gray Path
        print("4. Switching to Gray Path in Segmented Control...")
        gray_option = page.locator('button, label, [role="button"], [role="radio"]').filter(has_text="Gri Gelecek").first
        if gray_option.is_visible():
            gray_option.click()
            time.sleep(2)
            content_gray = page.content()
            assert "Ağır Bedel" in content_gray or "İhmal" in content_gray or "145.000" in content_gray
            page.screenshot(path="assets/rendered_future_fork_svg_gray.png", full_page=True)
            print("Gray Future Fork screenshot saved: assets/rendered_future_fork_svg_gray.png")
        else:
            print("Gray option locator not found directly, clicking by text...")
            page.get_by_text("🌫️ 2. YOL (Gri Gelecek)").click()
            time.sleep(2)
            page.screenshot(path="assets/rendered_future_fork_svg_gray.png", full_page=True)

        browser.close()
        print("All visual and functional checks completed successfully!")

if __name__ == "__main__":
    main()
