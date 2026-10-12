from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.goto('http://localhost:8501', wait_until='networkidle')
    
    # Click sidebar radio for 2035: Gelecek Yol Ayrımı
    sidebar = page.locator('[data-testid="stSidebar"]')
    radio_option = sidebar.locator('text=2035: Gelecek Yol Ayrımı')
    print('Radio option count:', radio_option.count())
    if radio_option.count() > 0:
        radio_option.click()
        page.wait_for_timeout(2000)
    
    body_text = page.locator('body').inner_text()
    print('Body text snippet:', body_text[:600])
    
    cards = page.locator('.fork-card')
    print('Cards count:', cards.count())
    for i in range(cards.count()):
        c = cards.nth(i)
        print(f'=== CARD {i} ===')
        print(c.inner_text()[:400])
        
    page.screenshot(path='scratch/future_after_radio_click.png', full_page=True)
    print('Saved scratch/future_after_radio_click.png')
    browser.close()
