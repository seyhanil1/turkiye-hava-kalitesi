import os
import sys
from streamlit.testing.v1 import AppTest

app_file = os.path.abspath("app/app.py")

all_pages = [
    "Genel Bakış",
    "Şehir Karnesi",
    "Düello",
    "Bölgeler",
    "Korelasyon",
    "Sanayi Profili",
    "Ekonomi",
    "AI Tahmin",
    "Senaryolar",
    "Yapılması Gerekenler",
    "Terimler Sözlüğü",
    "AI Asistan",
    "Veri ve Yöntem",
    "Sürüm Notları"
]

results = {}

for p in all_pages:
    print(f"Testing page: {p}...", flush=True)
    try:
        at = AppTest.from_file(app_file, default_timeout=30)
        at.query_params["sayfa"] = p
        at.run()
        
        errors = [e.value for e in at.error]
        exceptions = [str(exc.value) for exc in at.exception]
        
        results[p] = {
            "success": len(errors) == 0 and len(exceptions) == 0,
            "errors": errors,
            "exceptions": exceptions
        }
    except Exception as ex:
        results[p] = {
            "success": False,
            "errors": [],
            "exceptions": [str(ex)]
        }

print("\n" + "="*40, flush=True)
print("APPTEST TUM SAYFALAR RAPORU", flush=True)
print("="*40, flush=True)

failed_pages = []
for p, res in results.items():
    status = "GECTI" if res["success"] else "HATA"
    print(f"[{status}] {p}")
    if not res["success"]:
        failed_pages.append(p)
        if res["errors"]:
            print(f"   st.error mesajlari: {res['errors']}")
        if res["exceptions"]:
            print(f"   Exceptions: {res['exceptions']}")

print("\nOZET:", flush=True)
print(f"Toplam Test Edilen: {len(all_pages)}")
print(f"Basarili: {len(all_pages) - len(failed_pages)}")
print(f"Hata Veren: {len(failed_pages)}")
if failed_pages:
    print(f"Hata Veren Sayfalar: {failed_pages}")
else:
    print("Tum sayfalar basariyla gecti!")
