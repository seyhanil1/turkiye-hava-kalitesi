"""
Playwright Otomasyon ve Görsel Doğrulama: Yerel & Çevrimdışı AI Veri Asistanı (Chatbot)
"""

import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

def verify_chat_assistant():
    print("Yerel AI Veri Asistanı Doğrulama Testi Başlatılıyor...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="msedge")
        page = browser.new_page(viewport={"width": 1600, "height": 1100})

        # ========================================================
        # TEST 1: Streamlit Native Chatbot (?page=chat_assistant)
        # ========================================================
        print("\n--- TEST 1: Streamlit Native Chatbot (?page=chat_assistant) ---")
        page.goto("http://localhost:8501/?page=chat_assistant", wait_until="networkidle", timeout=45000)
        
        # Streamlit WebSocket yüklenene kadar başlığı bekle
        page.locator("text=HavaAtlası Yerel Veri Asistanı").first.wait_for(timeout=20000)
        print("✓ Yerel Chatbot sayfası başarıyla yüklendi.")

        # 4 Hazır Butonun Varlığını Kontrol Et
        btn_riskli = page.locator("button:has-text('🚨 En Riskli 3 Şehir')")
        btn_temiz = page.locator("button:has-text('🌿 En Temiz 3 Şehir')")
        btn_osb = page.locator("button:has-text('🏭 En Çok OSB\\'li 3 İl')")
        btn_vs = page.locator("button:has-text('⚖️ İstanbul vs Ankara Kıyasla')")

        btn_riskli.wait_for(timeout=10000)
        assert btn_riskli.is_visible(), "🚨 En Riskli 3 Şehir butonu görünmüyor!"
        assert btn_temiz.is_visible(), "🌿 En Temiz 3 Şehir butonu görünmüyor!"
        assert btn_osb.is_visible(), "🏭 En Çok OSB'li 3 İl butonu görünmüyor!"
        assert btn_vs.is_visible(), "⚖️ İstanbul vs Ankara Kıyasla butonu görünmüyor!"
        print("✓ 4 hazır buton eksiksiz ve görünür durumda.")

        # Test Buton 1: 🚨 En Riskli 3 Şehir
        print("\nButon 1 tıklanıyor: '🚨 En Riskli 3 Şehir'...")
        btn_riskli.click()
        page.locator("text=DSÖ sınırının").first.wait_for(timeout=15000)
        time.sleep(1)
        txt = page.locator("body").inner_text()
        assert "Osmaniye" in txt and "Iğdır" in txt, "En riskli 3 şehir yanıtı eksik!"
        print("✓ Buton 1 başarılı (Osmaniye, Iğdır listelendi).")

        # Test Buton 2: 🌿 En Temiz 3 Şehir
        print("\nButon 2 tıklanıyor: '🌿 En Temiz 3 Şehir'...")
        btn_temiz.click()
        page.locator("text=güçlü rüzgar koridorları").first.wait_for(timeout=15000)
        time.sleep(1)
        txt = page.locator("body").inner_text()
        assert "Tunceli" in txt and "Artvin" in txt, "En temiz 3 şehir yanıtı eksik!"
        print("✓ Buton 2 başarılı (Tunceli, Artvin listelendi).")

        # Test Buton 3: 🏭 En Çok OSB'li 3 İl
        print("\nButon 3 tıklanıyor: '🏭 En Çok OSB\\'li 3 İl'...")
        btn_osb.click()
        page.locator("text=OSB").first.wait_for(timeout=15000)
        time.sleep(1)
        txt = page.locator("body").inner_text()
        assert "Bursa" in txt, "OSB listesi bulunamadı!"
        print("✓ Buton 3 başarılı (En çok OSB'li iller listelendi).")

        # Test Buton 4: ⚖️ İstanbul vs Ankara Kıyasla
        print("\nButon 4 tıklanıyor: '⚖️ İstanbul vs Ankara Kıyasla'...")
        btn_vs.click()
        page.locator("text=Karşılaştırmalı Hava Kalitesi").first.wait_for(timeout=15000)
        time.sleep(1)
        txt = page.locator("body").inner_text()
        assert "İstanbul vs Ankara" in txt and "Karşılaştırmalı" in txt, "İstanbul vs Ankara karşılaştırması yapılmadı!"
        print("✓ Buton 4 başarılı (İki il yan yana tablo olarak karşılaştırıldı).")

        # Test Tek İl Yazma: 'Iğdır hava kirliliği karnesi'
        print("\nMetin kutusuna tek il yazılıyor: 'Iğdır hava kirliliği karnesi'...")
        chat_inp = page.locator('div[data-testid="stChatInput"] textarea')
        chat_inp.fill("Iğdır hava kirliliği karnesi")
        chat_inp.press("Enter")
        page.locator("text=Iğdır İli Çevre & Hava Kalitesi Karnesi").first.wait_for(timeout=10000)
        print("✓ Tek il karnesi formatı başarıyla görüntülendi.")

        # Test Genel Eşleşmeyen Soru: 'Merhaba'
        print("\nMetin kutusuna genel soru yazılıyor: 'Merhaba'...")
        chat_inp.fill("Merhaba")
        chat_inp.press("Enter")
        page.locator("text=kalıplarla soru sorabilirsiniz").first.wait_for(timeout=10000)
        txt = page.locator("body").inner_text()
        assert "kalıplarla soru sorabilirsiniz" in txt or "Nasıl soru sorabilirsiniz" in txt, "Genel rehber gösterilemedi!"
        print("✓ Eşleşmeyen genel soruda rehber başarıyla gösterildi.")

        # Ekran görüntüsü al
        shot_native = os.path.join(ASSETS_DIR, "rendered_chat_assistant_offline.png")
        page.screenshot(path=shot_native)
        print(f"✓ Yerel Chatbot ekran görüntüsü kaydedildi: {shot_native}")

        browser.close()
        print("\n==============================================")
        print("TÜM YEREL CHATBOT TESTLERİ VE DOĞRULAMALARI BAŞARIYLA TAMAMLANDI!")
        print("==============================================")

if __name__ == "__main__":
    verify_chat_assistant()
