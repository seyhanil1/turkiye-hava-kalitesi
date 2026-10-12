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
    st.markdown(f"""
    - **Hava Kalitesi Verisi:** Platformdaki ince partikül madde (PM2.5) verileri, 
      **Copernicus Atmosphere Monitoring Service (CAMS)** atmosferik reanaliz modelleri ve Open-Meteo Air Quality API aracılığıyla elde edilmektedir.
      *Önemli Not:* Bu veriler zemin seviyesindeki fiziksel ölçüm istasyonu verisi değil; uydu gözlemleri, kimyasal taşınım modelleri ve meteorolojik verilerin harmanlandığı **0.1° (~11 km) çözünürlüklü ızgaralanmış atmosferik model tahmin/reanaliz verisidir**.
    - **Veri Dönemi:** `{date_info.get('date_range_str', '11.07.2026 – 10.10.2026')}` ({date_info.get('total_days', 92)} günlük doğrulanabilir gözlem dönemi). Canlı veya anlık veri iddiası taşımamaktadır.
    - **Nüfus Verisi:** TÜİK Adrese Dayalı Nüfus Kayıt Sistemi (ADNKS 2023/2024 resmi il nüfusları).
    - **Ölüm ve Sağlık İstatistikleri:** TÜİK Ölüm ve Ölüm Nedeni İstatistikleri (2022–2024). Dolaşım ve solunum sistemi hastalıklarına (ICD-10 J00-J99) bağlı **ham ölüm hızlarıdır** (yaşa göre standardize edilmemiştir).
    - **Sanayi ve OSB Verisi:** OSB verileri: OSBÜK (indirme tarihi: GG.AA.2026) (81 ildeki faal/onaylı OSB sayıları ve hektar büyüklükleri).
    """)

    # 2. Seviye Eşikleri ve Kademelendirme
    st.markdown("### 2. Seviye Eşikleri ve Kademelendirme Mantığı")
    st.markdown("""
    Platform, Dünya Sağlık Örgütü'nün (WHO 2021) 24 saatlik 15 µg/m³ kılavuz değerini ve kademeli Ara Hedeflerini referans alarak 
    81 ilin tamamını kapsayan 5 düzeyli operasyonel bir sınıflandırma kullanır:
    """)

    pm25_kademeler = KIRLILIK_KADEMELERI.get("pm25", [])
    rows_html = ""
    for k in pm25_kademeler:
        max_str = f"≤ {k['max_val']}" if k['max_val'] < 900 else f"> {k['min_val']}"
        range_str = f"{k['min_val']} - {k['max_val']} µg/m³" if k['max_val'] < 900 else f"> {k['min_val']} µg/m³"
        rows_html += f"""
        <tr style="border-bottom:1px solid #093452;">
            <td style="padding:8px 12px; font-weight:700; color:{k['renk']};">{k['etiket']}</td>
            <td style="padding:8px 12px; color:#ffffff;">{range_str}</td>
            <td style="padding:8px 12px; color:#cbd5e1; font-size:12px;">{k['aciklama']}</td>
        </tr>
        """

    st.markdown(f"""
    <table style="width:100%; border-collapse:collapse; background:#031b2e; border:1px solid #093452; border-radius:8px; overflow:hidden; font-size:13px; margin-bottom:16px;">
        <thead>
            <tr style="background:#04253e; color:#cbd5e1; text-align:left; border-bottom:1px solid #093452;">
                <th style="padding:8px 12px;">Kademe</th>
                <th style="padding:8px 12px;">PM2.5 Aralığı</th>
                <th style="padding:8px 12px;">Referans & Risk Açıklaması</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """, unsafe_allow_html=True)

    # 3. İstatistiksel Hesaplamalar
    st.markdown("### 3. İstatistiksel Hesaplamalar ve Ortalamalar")
    st.markdown("""
    - **81 İl Ortalaması:** Kodda `df['pm25'].mean()` formülüyle hesaplanan **düz (nüfus ağırlıksız) aritmetik ortalamadır**. İllerin yüzölçümü veya nüfusu hesaba katılmaksızın her il eşit ağırlıktadır.
    - **Bölge Ortalamaları:** İlgili coğrafi bölgedeki illerin PM2.5 değerlerinin aritmetik ortalamasıdır (`b_df['pm25'].mean()`).
    - **Korelasyonlar:** Sanayi alanı (hektar) ve hava kirliliği arasındaki ilişki, doğrusal olmayan dağılımlara duyarlı **Spearman Sıra Korelasyon Katsayısı (ρ)** ile hesaplanmakta ve iki yönlü p-değeri ile test edilmektedir.
    """)

    # 4. Eksik Veri Yaklaşımı ve Sınırlamalar
    st.markdown("### 4. Eksik Veri Yaklaşımı ve Bilinen Sınırlamalar")
    st.markdown("""
    - **Eksik Veri (Missing Data):** Günlük serilerde eksik veya sıfır bildirilmiş kayıtlar analize dahil edilmemekte (`dropna()`); ortalamalar yalnızca geçerli gözlem günleri üzerinden alınmaktadır.
    - **Model Çözünürlüğü:** CAMS ızgara çözünürlüğü (~11 km) genel bölgesel arka plan kirliliğini çok iyi yakalamakla birlikte; yoğun trafik arterleri, sokak kanyonları veya vadi tabanlarındaki mikro-ölçekli kirlilik birikimlerini yer istasyonları kadar hassas yansıtmayabilir.
    """)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    with st.expander("Yöntem ve Kaynaklar"):
        st.markdown("""
        - **CAMS Atmosphere Reanalysis:** European Centre for Medium-Range Weather Forecasts (ECMWF).
        - **TÜİK:** Ölüm ve Ölüm Nedeni İstatistikleri (2022, 2023, 2024).
        - **OSB verileri: OSBÜK (indirme tarihi: GG.AA.2026)**
        """)
