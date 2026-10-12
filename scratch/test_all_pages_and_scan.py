import os
import sys
import re
from streamlit.testing.v1 import AppTest

app_file = os.path.abspath("app/app.py")

pages_to_test = [
    "Genel Bakış",
    "Şehir Karnesi",
    "Düello",
    "Bölgeler",
    "Korelasyon",
    "Sanayi Profili",
    "AI Tahmin",
    "Senaryolar",
    "Yapılması Gerekenler",
    "Terimler Sözlüğü",
    "AI Asistan",
    "Veri ve Yöntem",
    "Sürüm Notları",
    # Direct access / deprecated route check
    "Ekonomi"
]

BANNED_WORDS = ["maliyet", "₺", "VSL", "OECD", "Milyon"]
BANNED_REGEX = re.compile(r"(maliyet|₺|\bvsl\b|\boecd\b|milyon)", re.IGNORECASE)

results = {}
word_hits = {}

def extract_all_text(at: AppTest) -> list[str]:
    texts = []
    # Markdown & HTML
    for m in at.markdown:
        if hasattr(m, 'value') and m.value:
            texts.append(str(m.value))
    # Titles & Headers
    for t in at.title:
        if hasattr(t, 'value') and t.value:
            texts.append(str(t.value))
    for h in at.header:
        if hasattr(h, 'value') and h.value:
            texts.append(str(h.value))
    for sh in at.subheader:
        if hasattr(sh, 'value') and sh.value:
            texts.append(str(sh.value))
    # Captions & Text
    for c in at.caption:
        if hasattr(c, 'value') and c.value:
            texts.append(str(c.value))
    for tx in at.text:
        if hasattr(tx, 'value') and tx.value:
            texts.append(str(tx.value))
    # Metrics
    for mt in at.metric:
        if hasattr(mt, 'label') and mt.label:
            texts.append(str(mt.label))
        if hasattr(mt, 'value') and mt.value:
            texts.append(str(mt.value))
    # Alerts
    for inf in at.info:
        if hasattr(inf, 'value') and inf.value:
            texts.append(str(inf.value))
    for w in at.warning:
        if hasattr(w, 'value') and w.value:
            texts.append(str(w.value))
    for sc in at.success:
        if hasattr(sc, 'value') and sc.value:
            texts.append(str(sc.value))
    # Chat messages
    for cm in at.chat_message:
        if hasattr(cm, 'name') and cm.name:
            texts.append(str(cm.name))
    return texts

for p in pages_to_test:
    print(f"Testing page: '{p}'...", flush=True)
    try:
        at = AppTest.from_file(app_file, default_timeout=35)
        at.query_params["sayfa"] = p
        at.run()
        
        errors = [str(e.value) for e in at.error]
        exceptions = [str(exc.value) for exc in at.exception]
        
        # Extract rendered text
        rendered_texts = extract_all_text(at)
        combined_text = "\n".join(rendered_texts)
        
        # Scan for banned words
        page_hits = []
        for line in combined_text.splitlines():
            m = BANNED_REGEX.search(line)
            if m:
                page_hits.append((m.group(0), line.strip()[:100]))
        
        results[p] = {
            "success": len(errors) == 0 and len(exceptions) == 0,
            "errors": errors,
            "exceptions": exceptions,
            "element_count": len(rendered_texts)
        }
        word_hits[p] = page_hits
        
    except Exception as ex:
        results[p] = {
            "success": False,
            "errors": [],
            "exceptions": [str(ex)],
            "element_count": 0
        }
        word_hits[p] = []

print("\n" + "="*60, flush=True)
print("APPTEST TÜM SAYFALAR VE YASAKLI KELİME TARAMA RAPORU", flush=True)
print("="*60, flush=True)

failed_pages = []
any_word_hits = False

for p, res in results.items():
    status = "GEÇTİ" if res["success"] else "HATA"
    hits = word_hits.get(p, [])
    hit_str = f"TEMİZ ({res['element_count']} öğe)" if not hits else f"UYARI: {len(hits)} YASAKLI İFADE BULUNDU"
    if hits:
        any_word_hits = True
    print(f"[{status}] {p:<22} | {hit_str}")
    if not res["success"]:
        failed_pages.append(p)
        if res["errors"]:
            print(f"   st.error mesajları: {res['errors']}")
        if res["exceptions"]:
            print(f"   Exceptions: {res['exceptions']}")
    if hits:
        for word, sample in hits[:5]:
            print(f"   -> Bulunan: '{word}' | Satır: {sample}")

print("\nÖZET:", flush=True)
print(f"Toplam Test Edilen Sayfa/Rota: {len(pages_to_test)}")
print(f"Başarılı (Hatasız): {len(pages_to_test) - len(failed_pages)}")
print(f"Hata Veren: {len(failed_pages)}")
print(f"Yasaklı Kelime Eşleşmesi: {'VAR' if any_word_hits else 'YOK (TÜM SAYFALAR TERTEMİZ)'}")
