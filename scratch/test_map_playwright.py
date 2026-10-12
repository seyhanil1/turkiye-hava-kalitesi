from playwright.sync_api import sync_playwright
import time

def test_map():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='msedge', headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = context.new_page()
        page.goto('http://localhost:8501', wait_until='networkidle')
        
        iframe_elem = page.wait_for_selector('iframe', timeout=15000)
        frame = iframe_elem.content_frame()
        frame.wait_for_selector('#mapContainer', timeout=15000)
        time.sleep(1)

        # 1. Normal view screenshot
        page.screenshot(path='scratch/page_normal.png')
        print('Saved scratch/page_normal.png')

        # 2. Click Ankara to select and highlight
        ankara = frame.wait_for_selector('.province-path[data-name="Ankara"]')
        if ankara:
            ankara.click()
            time.sleep(0.5)
            page.screenshot(path='scratch/page_selected.png')
            print('Saved scratch/page_selected.png')
            
        # 3. Switch pollutant to PM10
        pm10_btn = frame.wait_for_selector('#pollutantTabs button[data-pol="PM10"]')
        if pm10_btn:
            pm10_btn.click()
            time.sleep(1.0) # Wait for smooth transition
            page.screenshot(path='scratch/page_pm10.png')
            print('Saved scratch/page_pm10.png')
            
        # 4. Test Fullscreen Mode
        fs_btn = frame.wait_for_selector('#mapFullscreenBtn')
        if fs_btn:
            fs_btn.click()
            time.sleep(0.8)
            page.screenshot(path='scratch/map_fullscreen.png')
            print('Saved scratch/map_fullscreen.png')
            
            # Close fullscreen via Esc key
            page.keyboard.press('Escape')
            time.sleep(0.6)
            page.screenshot(path='scratch/page_after_esc.png')
            print('Saved scratch/page_after_esc.png')

        browser.close()

if __name__ == '__main__':
    test_map()
