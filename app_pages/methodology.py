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
    - **Hava Kalitesi Verisi:** Platformdaki ince partikül madde (PM2.5) verileri, 
      **Copernicus Atmosphere Monitoring Service (CAMS)** atmosferik reanaliz modelleri ve Open-Meteo Air Quality API aracılığıyla elde edilmektedir.
      *Önemli Not:* Bu veriler zemin seviyesindeki fiziksel ölçüm istasyonu verisi değil; uydu gözlemleri, kimyasal taşınım modelleri ve meteorolojik verilerin harmanlandığı **0.1° (~11 km) çözünürlüklü ızgaralanmış atmosferik model tahmin/reanaliz verisidir**.
    - **Veri Dönemi:** Doğrulanmış 12 Aylık Konsolidasyon Dönemi (yıllık model ve istasyon konsolidasyonu; Copernicus CAMS zaman serisi 11.10.2025 – 10.10.2026 (12 Aylık Doğrulanmış Konsolidasyon) gözlem aralığını kapsar). Canlı veya anlık veri iddiası taşımamaktadır.
    - **Nüfus Verisi:** TÜİK Adrese Dayalı Nüfus Kayıt Sistemi (ADNKS 2023/2024 resmi il nüfusları).
    - **Ölüm ve Sağlık İstatistikleri:** TÜİK Ölüm ve Ölüm Nedeni İstatistikleri (2022–2024). Dolaşım ve solunum sistemi hastalıklarına (ICD-10 J00-J99) bağlı **ham ölüm hızlarıdır** (yaşa göre standardize edilmemiştir).
    - **Sanayi ve OSB Verisi:** OSB verileri: OSBÜK (Ekim 2026) (81 ildeki faal/onaylı OSB sayıları ve faal işletme/üretim oranları (OSBÜK Ekim 2026)).
    """)

    # 2. Seviye Eşikleri ve Kademelendirme
    st.markdown("### 2. Seviye Eşikleri ve Kademelendirme Mantığı")
    st.markdown("""
    Platform, Dünya Sağlık Örgütü'nün (WHO 2021) 24 saatlik 15 µg/m³ kılavuz değerini ve kademeli Ara Hedeflerini referans alarak 
    81 ilin tamamını kapsayan 5 düzeyli operasyonel bir sınıflandırma kullanır:
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
    - **Mekânsal Otokorelasyon (Global Moran's I):** İllerin enlem/boylam koordinatları üzerinden ters mesafe ağırlık matrisi (W) oluşturularak kirliliğin coğrafi havzalarda kümelenme eğilimi (Spatial Lag) test edilmiştir.
    - **Bölgesel Varyans Analizi:** Coğrafi bölgeler arası farklar Tek Yönlü ANOVA (F testi), Kruskal-Wallis (H testi) ve Levene varyans homojenliği testi ile sınanmıştır.
    """)

    # 4. Eksik Veri Yaklaşımı ve Sınırlamalar
    st.markdown("### 4. Eksik Veri Yaklaşımı ve Bilinen Sınırlamalar")
    st.markdown("""
    - **Eksik Veri (Missing Data):** Eksik veya sıfır bildirilmiş kayıtlar hesaplamaya dahil edilmemiş, yalnızca geçerli gözlem günleri baz alınmıştır.
    - **Model Çözünürlüğü:** CAMS ızgara çözünürlüğü (~11 km) genel bölgesel arka plan kirliliğini çok iyi yakalamakla birlikte; yoğun trafik arterleri, sokak kanyonları veya vadi tabanlarındaki mikro-ölçekli kirlilik birikimlerini yer istasyonları kadar hassas yansıtmayabilir.
    - **Kaba Ölüm Hızı ve Yaş Standardizasyonu:** Kullanılan TÜİK solunum ölüm oranları 'kaba ölüm hızı' olup il nüfuslarının yaş piramidine göre standardize edilmemiştir. Yaşlı nüfusu yoğun illerde oranlar yapısal olarak daha yüksektir.
    - **Ekolojik Yanılgı (Ecological Fallacy):** İl düzeyinde saptanan makro-mekânsal ve endüstriyel korelasyonlar, bireylerin kişisel maruziyetine veya tekil sağlık çıktılarına doğrudan nedensellik atfetmek için kullanılamaz.
    """)
