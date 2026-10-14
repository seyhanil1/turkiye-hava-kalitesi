import os
import sys

sys.path.insert(0, os.path.abspath("."))
from streamlit.testing.v1 import AppTest
from app.app import CATEGORY_PAGES, PAGE_TO_CATEGORY

app_file = os.path.abspath("app/app.py")

# CATEGORY_PAGES'ten dinamik olarak gerçek sayfaları al
all_pages = [page for cat, pages in CATEGORY_PAGES.items() for page in pages]

# Her sayfanın gerçekten render edildiğini kanıtlayan benzersiz başlık/metin imzaları
EXPECTED_SIGNATURES = {
    "Genel Bakış": ["81 İlin Düz Ortalaması", "HavaAtlası"],
    "Şehir Karnesi": ["Hava Kalitesi ve Sanayi Karnesi", "Karne", "TÜİK Solunum"],
    "Düello": ["İki İl Kafa Kafaya Karşılaştırma", "Dumbbell", "81 İl İçindeki Yüzdelik Sıralama"],
    "Bölgeler": ["7 Coğrafi Bölge", "Bölgesel PM2.5 Dağılımı"],
    "Korelasyon": ["Değişkenler Arası Korelasyon", "Saçılım Grafiği", "Korelasyon Analizi"],
    "Sanayi Profili": ["Sanayi & OSB Yoğunluk Profili", "Organize Sanayi"],
    "İl Grupları": ["İl Grupları", "81 İl İçin Çeyreklik", "Dağılım Grupları"],
    "Yapılması Gerekenler": ["Hava Kalitesi İyileştirme Eylem Rehberi", "Eylem Planı"],
    "Terimler Sözlüğü": ["Hava Kalitesi ve Çevre Sözlüğü", "Sözlük", "Kavramlar"],
    "AI Asistan": ["HavaAtlası Yerel Veri Asistanı", "Veri Asistanı", "Çevrimdışı & Yerel Motor"],
    "Veri ve Yöntem": ["Veri Kaynakları ve Hesaplama Yöntemi", "Copernicus Atmosphere Monitoring Service"],
    "Sürüm Notları": ["Sürüm Notları", "Changelog", "Platform Güncellemeleri"]
}

results = {}

print(f"Toplam Aktif Sayfa Sayısı: {len(all_pages)} (Menüdeki CATEGORY_PAGES'ten otomatik alındı)")
print(f"Sayfalar: {all_pages}\n")

for p in all_pages:
    print(f"Testing page: {p}...", flush=True)
    try:
        at = AppTest.from_file(app_file, default_timeout=60)
        cat = PAGE_TO_CATEGORY[p]
        at.query_params["sayfa"] = p
        at.session_state["active_category"] = cat
        at.session_state["nav_cat_pills"] = cat
        at.session_state["active_page"] = p
        at.session_state[f"nav_page_radio_{cat}"] = p
        at.run()
        
        errors = [e.value for e in at.error]
        exceptions = [str(exc.value) for exc in at.exception]
        
        all_text_list = []
        for attr in ['markdown', 'title', 'header', 'subheader', 'caption', 'text', 'info', 'warning']:
            if hasattr(at, attr):
                for el in getattr(at, attr):
                    if hasattr(el, 'value') and el.value:
                        all_text_list.append(str(el.value))
        
        try:
            for el in at.get("html"):
                if hasattr(el, 'value') and el.value:
                    all_text_list.append(str(el.value))
        except Exception:
            pass

        try:
            for el in at.get("iframe"):
                if hasattr(el, 'value') and el.value:
                    all_text_list.append(str(el.value))
        except Exception:
            pass

        all_text = " ".join(all_text_list)
        
        # Sayfanın gerçekten kendine ait içeriği render ettiğini doğrula
        expected_sigs = EXPECTED_SIGNATURES.get(p, [])
        matched_sig = next((sig for sig in expected_sigs if sig.lower() in all_text.lower()), None)
        signature_found = matched_sig is not None
        
        is_success = len(errors) == 0 and len(exceptions) == 0 and signature_found
        
        results[p] = {
            "success": is_success,
            "errors": errors,
            "exceptions": exceptions,
            "signature_found": signature_found,
            "matched_signature": matched_sig,
            "expected_signatures": expected_sigs
        }
    except Exception as ex:
        results[p] = {
            "success": False,
            "errors": [],
            "exceptions": [str(ex)],
            "signature_found": False,
            "matched_signature": None,
            "expected_signatures": []
        }

print("\n" + "="*50, flush=True)
print("APPTEST GERÇEK SAYFA BAŞLIK DOĞRULAMA RAPORU", flush=True)
print("="*50, flush=True)

failed_pages = []
for p, res in results.items():
    status = "GECTI" if res["success"] else "HATA"
    sig_status = f"BAŞLIK DOĞRULANDI ('{res['matched_signature']}')" if res["signature_found"] else "BAŞLIK BULUNAMADI!"
    print(f"[{status}] {p} -> {sig_status}")
    if not res["success"]:
        failed_pages.append(p)
        if res["errors"]:
            print(f"   st.error: {res['errors']}")
        if res["exceptions"]:
            print(f"   exception: {res['exceptions']}")

print("\nÖZET:")
print(f"Toplam Test Edilen: {len(all_pages)}")
print(f"Başarılı: {len(all_pages) - len(failed_pages)}")
print(f"Hata Veren: {len(failed_pages)}")

if len(failed_pages) == 0:
    print("Tüm aktif sayfalar hatasız ve kendi gerçek başlıklarıyla render edildi!")
    sys.exit(0)
else:
    print(f"Hata veren sayfalar: {failed_pages}")
    sys.exit(1)
