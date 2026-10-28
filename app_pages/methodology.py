"""
Veri ve Yöntem Sayfası (Data & Methodology)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import streamlit as st
import pandas as pd
from data_sources.constants import KIRLILIK_KADEMELERI, DSO_KILAVUZ_DEGERLERI, get_dataset_date_info


def render_methodology_page(df: pd.DataFrame = None):
    """
    Platformun veri akışı, atmosferik model kaynakları, epidemiyolojik hesaplamaları,
    eksik veri politikası ve bilinen teknik sınırlamaları hakkında teknik metodoloji dokümanı.
    """
    date_info = get_dataset_date_info()

    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="margin:0; font-size:24px; font-weight:800; color:#ffffff; letter-spacing:-0.5px;">
            Veri Kaynakları ve Hesaplama Yöntemi
        </h2>
        <p style="margin:4px 0 0 0; font-size:13px; color:#cbd5e1;">
            Platformun veri mimarisi, matematiksel modelleri, varsayımları ve teknik sınırlamaları.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 1. Veri Kaynağı ve Türü
    st.markdown("### 1. Veri Kaynakları ve Veri Türü (Ölçüm vs. Model)")
    st.markdown("""
    - **Yıllık PM2.5 (ana gösterge):** Her il için **Copernicus CAMS** atmosfer modelinin (Open-Meteo Air Quality API) il merkezi
      noktasındaki **2025 yılı 8.760 saatlik değerlerinin ortalamasıdır** (kış/ısınma sezonu dahil 12 ay; veri tamlığı %75 altında
      kalan il değeri boş bırakılır). Aynı yöntemle yıllık PM10 da hesaplanır.
      *Önemli:* Bu değerler istasyon ölçümü değil, ~10 km çözünürlüklü **model tahminidir**; yerel ısınma, trafik ve kapalı havza
      (inversiyon) kirliliğini genellikle **olduğundan düşük** gösterir.
    - **İstasyon karşılaştırması:** Temiz Hava Hakkı Platformu **Kara Rapor 2025**, ÇŞİDB istasyonlarının 2024 verisiyle yalnızca en yüksek
      10 istasyonun yıllık PM2.5 ortalamasını yayımlamıştır (en yüksek: Iğdır 46,8 µg/m³). Bu değerler ilgili iller için doğrulama katmanı
      olarak gösterilir; 81 ili kapsamadığından ana gösterge olarak kullanılmaz. Rapora göre PM2.5 ölçüm altyapısı olan 189 istasyonun
      yalnızca 113'ünden yeterli veri alınabilmiştir.
    - **Günlük seri:** Son ~90 gün için il merkezlerinin CAMS günlük ortalamaları (en az 18 saat dolu günler). "Türkiye geneli" serisi
      81 ilin **nüfus ağırlıklı** ortalamasıdır. Veri alınamazsa sentetik değer üretilmez, "veri yok" gösterilir.
    - **Kaldırılan veri:** Önceki sürümlerde kullanılan `hava_kirliligi.xlsx` il değerleri, Kara Rapor 2025'in yayımlanmış PM2.5 ve PM10
      bulgularıyla uyuşmadığı ve kaynağı doğrulanamadığı için kaldırılmıştır.
    - **Nüfus Verisi:** TÜİK Adrese Dayalı Nüfus Kayıt Sistemi (ADNKS 2023 il nüfusları).
    - **Ölüm ve Sağlık İstatistikleri:** TÜİK Ölüm ve Ölüm Nedeni İstatistikleri (2024; 2022–2024 ortalaması). Solunum sistemi hastalıklarına
      bağlı ölümler **ham (kaba) hızlardır**, yaşa göre standardize edilmemiştir.
    - **Sanayi ve OSB Verisi:** OSBÜK (Ekim 2026) OSB envanteri: il bazında toplam/faal OSB sayısı, alan ve parsel.
    """)

    # 2. Seviye Eşikleri ve Kademelendirme
    st.markdown("### 2. Seviye Eşikleri ve Kademelendirme Mantığı")
    st.markdown("""
    Yıllık ortalama PM2.5 için 5 düzeyli bir sınıflandırma kullanılır. Eşikler Dünya Sağlık Örgütü 2021 kılavuzunun **yıllık ara hedeflerinden**
    (IT-1 35, IT-2 25, IT-3 15, IT-4 10 µg/m³) alınmıştır. Kademe adları platforma özgüdür; DSÖ'nün resmi bir "5 kademeli risk ölçeği" yoktur.
    Kılavuz değeri (5 µg/m³) altında güvenli eşik bulunmadığından en düşük kademe "iyi" olarak adlandırılmaz:
    """)

    pm25_kademeler = KIRLILIK_KADEMELERI.get("pm25", [])
    rows_list = []
    for k in pm25_kademeler:
        range_str = f"≤ {k['max_val']} µg/m³" if k['min_val'] == 0 else (
            f"> {k['min_val']} µg/m³" if k['max_val'] >= 900 else f"{k['min_val']} - {k['max_val']} µg/m³"
        )
        badge_style = f"display:inline-block; padding:3px 10px; border-radius:4px; font-weight:700; color:{k['renk']}; background:{k['bg']}; border:1px solid {k['border']}; font-size:12px;"
        rows_list.append(
            f'<tr style="border-bottom:1px solid #093452;">'
            f'<td style="padding:10px 14px;"><span style="{badge_style}">{k["etiket"]}</span></td>'
            f'<td style="padding:10px 14px; color:#ffffff; font-weight:600; font-size:13px;">{range_str}</td>'
            f'<td style="padding:10px 14px; color:#cbd5e1; font-size:12.5px;">{k["aciklama"]}</td>'
            f'</tr>'
        )
    tbody_content = "".join(rows_list)

    table_html = (
        '<table style="width:100%; border-collapse:collapse; background:#031b2e; '
        'border:1px solid #093452; border-radius:8px; overflow:hidden; font-size:13px; margin:12px 0 20px 0;">'
        '<thead>'
        '<tr style="background:#04253e; color:#cbd5e1; text-align:left; border-bottom:1px solid #093452;">'
        '<th style="padding:10px 14px; font-size:12px; text-transform:uppercase; letter-spacing:0.05em; width:130px;">Kademe</th>'
        '<th style="padding:10px 14px; font-size:12px; text-transform:uppercase; letter-spacing:0.05em; width:170px;">PM2.5 Aralığı</th>'
        '<th style="padding:10px 14px; font-size:12px; text-transform:uppercase; letter-spacing:0.05em;">Referans & Risk Açıklaması</th>'
        '</tr>'
        '</thead>'
        f'<tbody>{tbody_content}</tbody>'
        '</table>'
    )
    st.markdown(table_html, unsafe_allow_html=True)

    # 3. İstatistiksel Hesaplamalar
    st.markdown("### 3. İstatistiksel Hesaplamalar ve Modeller")
    st.markdown("""
    - **81 İl Ortalaması:** 81 ilin PM2.5 değerlerinin ağırlıksız aritmetik ortalamasıdır. İllerin yüzölçümü veya nüfusu hesaba katılmaksızın her il eşit ağırlıktadır.
    - **Bölge Ortalamaları:** İlgili coğrafi bölgedeki illerin PM2.5 konsantrasyonlarının bölgesel aritmetik ortalamasıdır.
    - **Korelasyonlar:** Sanayi göstergeleri ve hava kirliliği arasındaki ilişki, doğrusal olmayan dağılımlara duyarlı **Spearman Sıra Korelasyon Katsayısı (ρ)** ve Pearson katsayısı ile hesaplanmakta, iki yönlü p-değeri ile test edilmektedir.
    - **Çoklu Regresyon (OLS):** PM2.5 kirlilik yükünün OSB sayısı, ortalama rakım ve il nüfusu (100 Bin Kişi normalize) bağımsız değişkenleriyle doğrusal ilişkisi modellenmiştir.
    - **PM2.5'e Atfedilebilir Ölüm Tahmini:** Kara Rapor 2025 ile aynı AirQ+ log-lineer yaklaşımı kullanılır: göreli risk her 10 µg/m³ için
      **RR = 1,08**, karşı-olgu düzeyi 5 µg/m³; atfedilebilir pay = 1 − 1/RR^((PM2.5−5)/10). TÜİK il verisinde 30+ yaş ve dış nedenler
      ayrıştırılamadığından tüm ölümler kullanılır (üst yönlü sapma); CAMS'ın düşük tahmin eğilimi ise alt yönlü sapma yaratır.
    - **Solunum Ölüm Payı:** Solunum ölümlerinin tüm ölümler içindeki yüzdesi; kaba hızın aksine illerin genel ölüm düzeyini (dolayısıyla
      yaş yapısını) kısmen dengeler.
    - **PM2.5'e Atfedilebilir Ölüm Tahmini:** Kara Rapor 2025 ile aynı AirQ+ log-lineer yaklaşımı kullanılır: göreli risk her 10 µg/m³ için
      **RR = 1,08**, karşı-olgu düzeyi 5 µg/m³; atfedilebilir pay = 1 − 1/RR^((PM2.5−5)/10). TÜİK il verisinde 30+ yaş ve dış nedenler
      ayrıştırılamadığından tüm ölümler kullanılır (üst yönlü sapma); CAMS'ın düşük tahmin eğilimi ise alt yönlü sapma yaratır.
    - **Solunum Ölüm Payı:** Solunum ölümlerinin tüm ölümler içindeki yüzdesi; kaba hızın aksine illerin genel ölüm düzeyini (dolayısıyla
      yaş yapısını) kısmen dengeler.
    - **Mekânsal Otokorelasyon (Global Moran's I):** İllerin enlem/boylam koordinatları üzerinden ters mesafe ağırlık matrisi (W) oluşturularak kirliliğin coğrafi havzalarda kümelenme eğilimi (Spatial Lag) test edilmiştir.
    - **Bölgesel Varyans Analizi:** Coğrafi bölgeler arası farklar Tek Yönlü ANOVA (F testi), Kruskal-Wallis (H testi) ve Levene varyans homojenliği testi ile sınanmıştır.
    """)

    # 4. Eksik Veri Yaklaşımı ve Sınırlamalar
    st.markdown("### 4. Eksik Veri Yaklaşımı ve Bilinen Sınırlamalar")
    st.markdown("""
    - **Eksik Veri (Missing Data):** Eksik veya sıfır bildirilmiş kayıtlar hesaplamaya dahil edilmemiş, yalnızca geçerli gözlem günleri baz alınmıştır.
    - **Model Çözünürlüğü ve Sapma:** CAMS (~10 km) bölgesel arka plan kirliliğini yakalar; ancak trafik, konut ısınması ve kapalı havzalardaki
      birikimi düşük tahmin eder. Örnek: Iğdır için CAMS 2025 yıllık ortalaması ~12 µg/m³ iken Kara Rapor 2025'te Iğdır istasyonu 46,8 µg/m³'tür.
      Bu nedenle mutlak değerler alt sınır, il sıralamaları ise yaklaşık olarak yorumlanmalıdır.
    - **Kaba Ölüm Hızı ve Yaş Standardizasyonu:** Kullanılan TÜİK solunum ölüm oranları 'kaba ölüm hızı' olup il nüfuslarının yaş piramidine göre standardize edilmemiştir. Yaşlı nüfusu yoğun illerde oranlar yapısal olarak daha yüksektir.
    - **Ekolojik Yanılgı (Ecological Fallacy):** İl düzeyinde saptanan makro-mekânsal ve endüstriyel korelasyonlar, bireylerin kişisel maruziyetine veya tekil sağlık çıktılarına doğrudan nedensellik atfetmek için kullanılamaz.
    """)
