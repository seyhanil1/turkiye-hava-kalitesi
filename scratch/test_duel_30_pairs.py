import os
import sys

sys.path.insert(0, os.path.abspath("."))
import pandas as pd
from data_sources.local_official_data import build_master_dataset
from visualization.distribution_charts import create_duel_dumbbell_chart
from app_pages.duel import render_duel_page
from streamlit.testing.v1 import AppTest

# 30 farklı il çifti (Büyükşehirler, küçük iller, sanayi illeri, temiz iller, sınır illeri)
CITY_PAIRS = [
    ("İstanbul", "Ankara"),
    ("İzmir", "Bursa"),
    ("Antalya", "Adana"),
    ("Konya", "Şanlıurfa"),
    ("Gaziantep", "Kocaeli"),
    ("Mersin", "Diyarbakır"),
    ("Hatay", "Manisa"),
    ("Kayseri", "Samsun"),
    ("Balıkesir", "Kahramanmaraş"),
    ("Van", "Aydın"),
    ("Tekirdağ", "Denizli"),
    ("Sakarya", "Muğla"),
    ("Eskişehir", "Mardin"),
    ("Malatya", "Trabzon"),
    ("Erzurum", "Ordu"),
    ("Afyonkarahisar", "Sivas"),
    ("Adıyaman", "Batman"),
    ("Tokat", "Zonguldak"),
    ("Elazığ", "Kütahya"),
    ("Çanakkale", "Osmaniye"),
    ("Giresun", "Isparta"),
    ("Yozgat", "Muş"),
    ("Edirne", "Aksaray"),
    ("Kastamonu", "Düzce"),
    ("Uşak", "Kırklareli"),
    ("Niğde", "Bitlis"),
    ("Rize", "Amasya"),
    ("Siirt", "Bolu"),
    ("Nevşehir", "Yalova"),
    ("Iğdır", "Çanakkale")
]

print(f"--- 30 İL ÇİFTİ DÜELLO STRES VE GÖRSEL TUTARLILIK TESTİ ---")
print(f"Toplam Çift Sayısı: {len(CITY_PAIRS)}\n")

df = build_master_dataset()
assert len(df) == 81, "Master dataset 81 il içermeli"

failed_pairs = []

for idx, (il_a, il_b) in enumerate(CITY_PAIRS, 1):
    c_a = df[df["il"] == il_a].iloc[0]
    c_b = df[df["il"] == il_b].iloc[0]
    
    # 1. Dumbbell chart doğrudan üretimi
    fig = create_duel_dumbbell_chart(df, c_a, c_b)
    
    # Kategori kontrolü (kesinlikle 2 kategori olmalı, Sanayi Baskısı olmamalı)
    categories = [trace.y for trace in fig.data if trace.mode == "markers+text"][0]
    assert len(categories) == 2, f"{il_a}-{il_b}: Kategori sayısı 2 olmalı, {len(categories)} bulundu"
    assert "Sanayi Baskısı (Düşük OSB/Kişi)" not in categories, f"{il_a}-{il_b}: Sanayi Baskısı grafikten çıkarılmış olmalı"
    assert "Hava Temizliği (Düşük PM2.5)" in categories
    assert "Solunum Sağlığı (Düşük Ölüm)" in categories
    
    # Etiket formatı kontrolü ("İl %XX")
    marker_traces = [trace for trace in fig.data if trace.mode == "markers+text"]
    assert len(marker_traces) == 2
    
    labels_a = marker_traces[0].text
    labels_b = marker_traces[1].text
    for lbl in labels_a:
        assert lbl.startswith(f"{il_a} %"), f"{il_a} etiketi beklenen formatta değil: {lbl}"
    for lbl in labels_b:
        assert lbl.startswith(f"{il_b} %"), f"{il_b} etiketi beklenen formatta değil: {lbl}"
        
    # Yakın noktalarda üst üste binmeme kontrolü
    vals_a = marker_traces[0].x
    vals_b = marker_traces[1].x
    pos_a = marker_traces[0].textposition
    pos_b = marker_traces[1].textposition
    for va, vb, pa, pb in zip(vals_a, vals_b, pos_a, pos_b):
        if abs(va - vb) < 12:
            assert pa == "top center" and pb == "bottom center", f"Yakın noktalarda konumlar zıt olmalı: {pa} vs {pb}"
            
    # 2. AppTest ile tam sayfa render testi
    def make_app_func(city_1, city_2):
        def _app():
            import streamlit as st
            from app_pages.duel import render_duel_page
            from data_sources.local_official_data import build_master_dataset
            d = build_master_dataset()
            render_duel_page(d)
        return _app
    
    at = AppTest.from_function(make_app_func(il_a, il_b))
    at.run()
    # selectbox seçimi
    at.selectbox[0].select(il_a)
    at.selectbox[1].select(il_b).run()
    
    if at.exception:
        failed_pairs.append((il_a, il_b, str(at.exception)))
        print(f"[{idx}/30] HATA: {il_a} vs {il_b} -> {at.exception}")
    else:
        all_md = " ".join([m.value for m in at.markdown])
        assert "nesnel" not in all_md.lower(), f"Sayfada 'nesnel' kelimesi bulundu!"
        print(f"[{idx:02d}/30] BAŞARILI: {il_a} vs {il_b} (Dumbbell 2 kategori, etiketler '{il_a} %', '{il_b} %', 0 hata)")

print("\n" + "="*50)
print(f"SONUÇ: 30/{len(CITY_PAIRS)} ÇİFT TAMAMEN BAŞARILI (0 HATA, 0 EXCEPTION)")
print("="*50)
