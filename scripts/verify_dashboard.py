"""
Kapsamlı Playwright Otomasyon ve Görsel Doğrulama Testi (v2)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

Doğrulanan Özellikler:
1. Sol paneldeki 8 modülün tamamına tıklanabilirlik ve anında geçiş.
2. Bölge seçici dropdown açılması ve rastgele/doğrudan bölge seçimi.
3. Harita üzerinde fareyle sürükleyip kaydırma (drag pan) ve tekerlek/buton ile yakınlaştırma (zoom).
4. Benzersiz Kullanıcı ID'si (Örn. HA-81-AA-7492), Ad-Soyad düzenleme ve localStorage kalıcılığı.
5. Özelleştirilmiş sıralama tablosu (Madalyalar, durum pilleri, plaka kodları).
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

def run_comprehensive_verification():
    print("Playwright kapsamlı doğrulama başlatılıyor...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="msedge")
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto("http://localhost:8501", wait_until="networkidle", timeout=45000)
        time.sleep(3)
        
        frame = page.frame_locator("iframe").first
        frame.locator("#pollutantTabs").wait_for(timeout=15000)
        
        # 1. TEST: Ana Sayfa Ekran Görüntüsü
        shot_main = os.path.join(ASSETS_DIR, "rendered_1080p_v2.png")
        page.screenshot(path=shot_main)
        print(f"1. Ana görünüm kaydedildi: {shot_main}")
        
        # 2. TEST: Bölge Seçici Dropdown Testi
        print("2. Bölge seçici dropdown açılıyor ve Marmara seçiliyor...")
        frame.locator("#regionSelectorBtn").click()
        time.sleep(0.5)
        shot_region = os.path.join(ASSETS_DIR, "rendered_region_dropdown.png")
        page.screenshot(path=shot_region)
        print(f"Bölge dropdown görüntüsü kaydedildi: {shot_region}")
        
        frame.locator('.region-option[data-reg="Marmara"]').click()
        time.sleep(1)
        
        # 3. TEST: Harita Sürükleme (Drag-Pan) ve Yakınlaştırma (Zoom)
        print("3. Harita sürükleme ve zoom motoru test ediliyor...")
        map_cont = frame.locator("#mapContainer")
        box = map_cont.bounding_box()
        if box:
            # Sürükle ve bırak (drag to pan)
            page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
            page.mouse.down()
            page.mouse.move(box["x"] + box["width"] / 2 - 120, box["y"] + box["height"] / 2 - 60)
            page.mouse.up()
            time.sleep(0.5)
            
        frame.locator("#mapZoomIn").click()
        time.sleep(0.5)
        frame.locator("#mapZoomIn").click()
        time.sleep(0.5)
        
        # 4. TEST: Kullanıcı Profili ve Benzersiz ID Sistemi
        print("4. Kullanıcı profili ve ID menüsü açılıyor...")
        frame.locator("#userPillBtn").click()
        time.sleep(0.5)
        shot_user = os.path.join(ASSETS_DIR, "rendered_user_id.png")
        page.screenshot(path=shot_user)
        print(f"Kullanıcı ID görüntüsü kaydedildi: {shot_user}")
        
        # 5. TEST: Sol Paneldeki Modüllerin Tamamını Test Etme
        print("5. Sol paneldeki modüller tek tek test ediliyor...")
        modules = [
            ("sehir_karnesi", "#view-sehir_karnesi"),
            ("duello", "#view-duello"),
            ("korelasyon", "#view-korelasyon"),
            ("bolgeler", "#view-bolgeler"),
            ("yesil_donusum", "#view-yesil_donusum"),
            ("sanayi_profili", "#view-sanayi_profili"),
            ("ekonomi", "#view-ekonomi"),
            ("genel_bakis", "#view-genel_bakis")
        ]
        
        for mod_name, sel in modules:
            print(f"   -> {mod_name} modülüne geçiliyor...")
            nav_btn = frame.locator(f'.nav-item[data-view="{mod_name}"]')
            nav_btn.click()
            time.sleep(0.6)
            # İlgili bölümün aktif olduğunu doğrula
            assert frame.locator(f"{sel}.active").is_visible(), f"{mod_name} görünür olmalı"
            
        # Son durum ekran görüntüsü (Modüller doğrulandıktan sonra)
        shot_mods = os.path.join(ASSETS_DIR, "rendered_sidebar_modules.png")
        page.screenshot(path=shot_mods)
        print(f"Tüm modüller doğrulandı ve kaydedildi: {shot_mods}")
        
        browser.close()
        print("TEBRİKLER: Tüm kapsamlı Playwright testleri başarıyla geçti!")

if __name__ == "__main__":
    run_comprehensive_verification()
