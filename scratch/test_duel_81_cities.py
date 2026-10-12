import os
import sys
import pandas as pd
from streamlit.testing.v1 import AppTest

app_file = os.path.abspath("app/app.py")
df_master = pd.read_csv("data/master_data.csv")
cities = sorted(df_master["il"].unique().tolist())

print(f"Toplam test edilecek il sayisi: {len(cities)}", flush=True)

at = AppTest.from_file(app_file, default_timeout=30)
at.query_params["sayfa"] = "Düello"
at.run()

forbidden_terms = ["p-değeri", "p-degeri", "pm10", "hipotez"]

failed_pairs = []
found_forbidden = []
successful_tests = 0

for i in range(len(cities)):
    city_a = cities[i]
    city_b = cities[(i + 1) % len(cities)]
    
    try:
        at.selectbox[2].select(city_a)
        at.selectbox[3].select(city_b)
        at.run()
        
        errors = [e.value for e in at.error]
        exceptions = [str(exc.value) for exc in at.exception]
        
        if errors or exceptions:
            failed_pairs.append((city_a, city_b, errors, exceptions))
            print(f"[HATA] {city_a} vs {city_b}: Errors={errors}, Exc={exceptions}", flush=True)
            continue
            
        # Ekrandaki metinleri tara
        all_texts = []
        for el in at.main:
            for attr in ["value", "body", "caption", "label", "help"]:
                val = getattr(el, attr, None)
                if val:
                    all_texts.append(str(val))
                    
        screen_content = " ".join(all_texts).lower()
        
        for term in forbidden_terms:
            if term in screen_content:
                found_forbidden.append((city_a, city_b, term))
                print(f"[YASAK KELIME] {city_a} vs {city_b} sayfasinda '{term}' bulundu!", flush=True)
                
        successful_tests += 1
        if (i + 1) % 15 == 0 or (i + 1) == len(cities):
            print(f"Ilerleme: {i + 1}/{len(cities)} il cifti test edildi...", flush=True)
            
    except Exception as e:
        failed_pairs.append((city_a, city_b, [], [str(e)]))
        print(f"[EXCEPTION] {city_a} vs {city_b}: {e}", flush=True)

print("\n" + "="*50)
print("81 IL DUELLO APPTEST VE KELIME TARAMA RAPORU")
print("="*50)
print(f"Toplam Test Edilen Cift: {len(cities)}")
print(f"Hatasiz Calisan: {successful_tests}")
print(f"Hata Veren: {len(failed_pairs)}")
print(f"Yasak Kelime Bulunan: {len(found_forbidden)}")

if failed_pairs:
    print("\nHATA VEREN CIFTLER:")
    for fa in failed_pairs:
        print(f" - {fa[0]} vs {fa[1]}: {fa[2]} {fa[3]}")
else:
    print("\n81 ilin TAMAMI farkli ciftlerle AppTest'ten basariyla gecti (0 hata, 0 exception).")

if found_forbidden:
    print("\nYASAK KELIME BULGULARI:")
    for ff in found_forbidden:
        print(f" - {ff[0]} vs {ff[1]}: '{ff[2]}'")
else:
    print("Ekranda 'p-değeri', 'PM10', 'hipotez' kelimelerinin kalmadigi TAMAMEN dogrulandi (0 eslesme).")
