from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 1100})
    page.goto('http://localhost:8501/?page=future_2035', wait_until='networkidle')
    page.wait_for_timeout(3000)
    
    # Check text on page
    txt = page.locator('body').inner_text()
    print('Body text (first 500 chars):', repr(txt[:500]))
    
    # Check fork cards
    cards = page.locator('.fork-card')
    print('Cards count:', cards.count())
    if cards.count() > 0:
        for i in range(cards.count()):
            print(f'CARD {i} TEXT:', repr(cards.nth(i).inner_text()[:200]))
            
    page.screenshot(path='scratch/inspect_full_page.png', full_page=True)
    print('Saved scratch/inspect_full_page.png')
    browser.close()
