"""
Yapay Zeka İçgörü & Tahmin Motoru - Playwright Doğrulama ve Ekran Yakalama Betiği
"""

import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

def verify_ai_forecast():
    print("AI Tahmin Motoru Doğrulama Testi Başlatılıyor...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="msedge")
        
        # ========================================================
        # TEST 1: Streamlit Native AI Sayfası (?page=ai_tahmin)
        # ========================================================
        print("\n--- TEST 1: Streamlit Native Sayfası (?page=ai_tahmin) ---")
        page = browser.new_page(viewport={"width": 1600, "height": 1100})
        page.goto("http://localhost:8501/?page=ai_tahmin", wait_until="networkidle", timeout=45000)
        time.sleep(3)
        
        # Sayfa başlığı ve bileşenlerin kontrolü
        body_text = page.locator("body").inner_text()
        assert "Yapay Zeka İçgörü & Tahmin Motoru" in body_text, "AI başlığı bulunamadı!"
        assert "Kategori A" in body_text, "Kategori A bulunamadı!"
        assert "Kategori B" in body_text, "Kategori B bulunamadı!"
        print("✓ AI Sayfası ve başlıklar başarıyla yüklendi.")
        
        # Iğdır (Kategori A) Ekran Görüntüsü
        shot_a = os.path.join(ASSETS_DIR, "rendered_ai_forecast_native_cat_a.png")
        page.screenshot(path=shot_a)
        print(f"✓ Kategori A (Iğdır) ekran görüntüsü kaydedildi: {shot_a}")
        
        # İl seçiciden Bursa'yı seç (Kategori B testi)
        print("Bursa seçilerek Kategori B testi yapılıyor...")
        # Streamlit selectbox tıklama
        page.locator('div[data-testid="stSelectbox"]').click()
        time.sleep(0.5)
        # Bursa seçeneğini ara ve tıkla
        page.keyboard.type("Bursa")
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(2)
        
        bursa_text = page.locator("body").inner_text()
        assert "Kategori B" in bursa_text, "Bursa için Kategori B tespit edilemedi!"
        assert "yoğun OSB ve endüstriyel faaliyetler" in bursa_text, "Kategori B neden-sonuç metni eşleşmedi!"
        print("✓ Bursa başarıyla Kategori B olarak sınıflandırıldı.")
        
        shot_b = os.path.join(ASSETS_DIR, "rendered_ai_forecast_native_cat_b.png")
        page.screenshot(path=shot_b)
        print(f"✓ Kategori B (Bursa) ekran görüntüsü kaydedildi: {shot_b}")
        
        # ========================================================
        # TEST 2: Dashboard İçi AI Sekmesi (Sol Panel Navigasyonu)
        # ========================================================
        print("\n--- TEST 2: Dashboard İçi Sol Menü AI Sekmesi ---")
        page.goto("http://localhost:8501", wait_until="networkidle", timeout=45000)
        time.sleep(3)
        
        frame = page.frame_locator("iframe").first
        frame.locator('.nav-item[data-view="ai_tahmin"]').wait_for(timeout=15000)
        
        print("Sol panelden '🤖 AI Tahmin' sekmesine tıklanıyor...")
        frame.locator('.nav-item[data-view="ai_tahmin"]').click()
        time.sleep(2)
        
        # view-ai_tahmin aktif oldu mu kontrol et
        ai_section = frame.locator("#view-ai_tahmin")
        assert "active" in ai_section.get_attribute("class"), "view-ai_tahmin aktif olmadı!"
        print("✓ view-ai_tahmin modülü aktif hale geldi.")
        
        # Dashboard içi ekran görüntüsü
        shot_dash = os.path.join(ASSETS_DIR, "rendered_ai_forecast_dashboard.png")
        page.screenshot(path=shot_dash)
        print(f"✓ Dashboard AI görünümü kaydedildi: {shot_dash}")
        
        # Dashboard içinde il değiştirme testi
        print("Dashboard içinde Kategori B ili (Bursa) seçiliyor...")
        frame.locator("#aiCitySelectBox").select_option("Bursa")
        time.sleep(1.5)
        
        shot_dash_bursa = os.path.join(ASSETS_DIR, "rendered_ai_forecast_dash_bursa.png")
        page.screenshot(path=shot_dash_bursa)
        print(f"✓ Dashboard Bursa görünümü kaydedildi: {shot_dash_bursa}")
        
        browser.close()
        print("\n==============================================")
        print("TÜM YAPAY ZEKA DOĞRULAMA TESTLERİ BAŞARIYLA GEÇTİ!")
        print("==============================================")

if __name__ == "__main__":
    verify_ai_forecast()
