from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.goto('http://localhost:8501?page=future_2035', wait_until='networkidle')
    page.wait_for_timeout(2000)
    
    # Query all elements with class fork-card
    cards = page.query_selector_all('.fork-card')
    print('Cards found:', len(cards))
    for i, c in enumerate(cards):
        print(f'=== CARD {i} ===')
        print('HTML:', c.inner_html()[:600])
        print('TEXT:', c.inner_text()[:300])
        
    browser.close()
