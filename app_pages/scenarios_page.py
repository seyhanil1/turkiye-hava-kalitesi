"""
Senaryolar ve Politika Simülatörü Sayfası
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

Bu sayfa, Yeşil Dönüşüm politika simülasyonu ile 2035 Gelecek Yol Ayrımı projeksiyonlarını
tek bir stratejik karar destek merkezinde birleştirir.
"""

import streamlit as st
import pandas as pd
from app_pages.green_page import render_green_page
from app_pages.future_fork_page import render_future_fork_page


def render_scenarios_page(df: pd.DataFrame):
    """
    Politika müdahale simülatörü ve 10 yıllık gelecek projeksiyonlarını
    sekme yapısıyla kullanıcıya sunar.
    """
    st.markdown("""
    <div style="margin-bottom: 18px;">
        <h2 style="margin:0; font-size:24px; font-weight:800; color:#ffffff; letter-spacing:-0.5px;">
            Hava Kalitesi Senaryoları &amp; Politika Simülatörü
        </h2>
        <p style="margin:4px 0 0 0; font-size:13px; color:#cbd5e1;">
            Emisyon kontrol politikalarının 10 yıllık sağlık, çevre ve kamu bütçesi bilançosu.
        </p>
    </div>
    """, unsafe_allow_html=True)

    cities = sorted(df["il"].unique().tolist()) if (df is not None and not df.empty) else []
    default_idx = 0
    if "Iğdır" in cities:
        default_idx = cities.index("Iğdır")
    elif "selected_city" in st.session_state and st.session_state["selected_city"] in cities:
        default_idx = cities.index(st.session_state["selected_city"])

    selected_city = st.selectbox(
        "Senaryo Analizi Yapılacak İli Seçin:",
        cities,
        index=default_idx,
        key="scenario_selected_city"
    )

    tab_sim, tab_2035 = st.tabs([
        "Politika & Dönüşüm Simülatörü",
        "2035: Gelecek Yol Ayrımı (Temiz Yol vs. Gri Yol)"
    ])

    with tab_sim:
        render_green_page(df, selected_city=selected_city)

    with tab_2035:
        render_future_fork_page(df)
