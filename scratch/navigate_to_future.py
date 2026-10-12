from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 1100})
    page.goto('http://localhost:8501', wait_until='networkidle')
    time.sleep(2)
    
    # Check if collapsed sidebar button exists
    collapse_btn = page.query_selector('[data-testid="stSidebarCollapsedControl"] button')
    if collapse_btn:
        collapse_btn.click()
        time.sleep(1)
        
    # Find the radio button for future_2035
    radio_labels = page.query_selector_all('[data-testid="stRadio"] label')
    for r in radio_labels:
        txt = r.inner_text()
        if "2035" in txt:
            r.dispatch_event('click')
            time.sleep(3)
            break
            
    # Take screenshot of the rendered page
    page.screenshot(path='scratch/rendered_future_page.png', full_page=True)
    print("Saved scratch/rendered_future_page.png")
    
    # Check text inside cards
    cards = page.query_selector_all('.fork-card')
    print("Found fork cards:", len(cards))
    for i, c in enumerate(cards):
        print(f"=== CARD {i} TEXT ===")
        safe_txt = c.inner_text().encode('ascii', errors='replace').decode('ascii')
        print(safe_txt[:400])
        
    browser.close()
