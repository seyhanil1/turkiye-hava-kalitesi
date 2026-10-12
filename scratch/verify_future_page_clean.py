from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 1100})
    
    console_logs = []
    page.on('console', lambda msg: console_logs.append(f'[{msg.type}] {msg.text}'))
    page.on('pageerror', lambda err: console_logs.append(f'[PAGE_ERROR] {err}'))
    
    page.goto('http://localhost:8501?page=future_2035', wait_until='networkidle')
    time.sleep(2)
    
    # Take screenshot of clean path
    page.screenshot(path='scratch/future_clean_sober.png', full_page=True)
    print('Saved scratch/future_clean_sober.png')
    
    # Click the Gray Path option if available
    buttons = page.query_selector_all('button')
    for b in buttons:
        txt = b.inner_text()
        if 'Gri Gelecek' in txt:
            b.click()
            time.sleep(1.5)
            page.screenshot(path='scratch/future_gray_sober.png', full_page=True)
            print('Saved scratch/future_gray_sober.png')
            break
            
    print('Console logs:', [l for l in console_logs if 'warning' not in l])
    browser.close()
