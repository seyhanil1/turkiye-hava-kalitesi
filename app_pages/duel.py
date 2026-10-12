"""
Şehir Düellosu Sayfası (City Duel)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from visualization.components import render_metric_card
from visualization.distribution_charts import create_duel_radar_chart


def render_duel_page(df: pd.DataFrame):
    """
    Kullanıcının seçtiği iki ili kafa kafaya karşılaştırır ve
    çevre, sanayi ve sağlık profillerini görselleştirir.
    """
    st.markdown("### Şehir Düellosu & Karşılaştırma Motoru")
    st.markdown(
        "<p style='color:#94a3b8;'>İki ili kafa kafaya karşılaştırın, çok kriterli çevre radarı ve gösterge profilleriyle aralarındaki farkı inceleyin.</p>",
        unsafe_allow_html=True
    )
    
    iller = sorted(df["il"].unique().tolist())
    
    col1, col2 = st.columns(2)
    with col1:
        default_a = iller.index("İstanbul") if "İstanbul" in iller else 0
        il_a_name = st.selectbox("1. Şehir (Grup A):", iller, index=default_a)
    with col2:
        default_b = iller.index("Ankara") if "Ankara" in iller else 1
        il_b_name = st.selectbox("2. Şehir (Grup B):", iller, index=default_b)
        
    if il_a_name == il_b_name:
        st.info("Lütfen karşılaştırma için iki farklı şehir seçiniz.")
        return
        
    city_a = df[df["il"] == il_a_name].iloc[0]
    city_b = df[df["il"] == il_b_name].iloc[0]
    
    # 1. KAFA KAFAYA METRİK KARTLARI
    st.markdown("#### Kafa Kafaya Metrik Karşılaştırması")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        diff_pm = round(city_a["pm25"] - city_b["pm25"], 1)
        sign = "+" if diff_pm > 0 else ""
        render_metric_card(
            title="PM2.5 Kirliliği",
            value=f"{city_a['pm25']} vs {city_b['pm25']}",
            unit="µg/m³",
            delta=f"{sign}{diff_pm} µg/m³ fark",
            delta_type="positive" if diff_pm > 0 else "negative"
        )
    with m2:
        render_metric_card(
            title="TÜİK Solunum Ölümü",
            value=f"{city_a['solunum_olum_100k']} vs {city_b['solunum_olum_100k']}",
            unit="/ 100k",
            delta=f"{round(city_a['solunum_olum_100k'] - city_b['solunum_olum_100k'], 1)} oran farkı",
            delta_type="neutral"
        )
    with m3:
        render_metric_card(
            title="Toplam OSB Sayısı",
            value=f"{city_a['toplam_osb']} vs {city_b['toplam_osb']}",
            unit="OSB",
            delta=f"{city_a['faal_osb']} vs {city_b['faal_osb']} Faal",
            delta_type="neutral"
        )
    with m4:
        render_metric_card(
            title="Yeşil Dönüşüm Skoru",
            value=f"{city_a['yesil_skor']} vs {city_b['yesil_skor']}",
            unit="/ 100",
            delta="Yüksek skor = Daha temiz",
            delta_type="negative" if city_a['yesil_skor'] > city_b['yesil_skor'] else "positive"
        )
        
    st.write("")
    
    # 2. RADAR VE ÇUBUK GRAFİK
    col_radar, col_bars = st.columns([1.1, 1.0])
    with col_radar:
        fig_radar = create_duel_radar_chart(city_a, city_b)
        st.plotly_chart(fig_radar, use_container_width=True)
        
    with col_bars:
        st.markdown(f"#### {il_a_name} ve {il_b_name} Gösterge Profili")
        metrics_df = pd.DataFrame({
            "Gösterge": ["PM2.5 Kirliliği (µg/m³)", "Solunum Ölümü (100k)", "Yeşil Skor"],
            il_a_name: [city_a["pm25"], city_a["solunum_olum_100k"], city_a["yesil_skor"]],
            il_b_name: [city_b["pm25"], city_b["solunum_olum_100k"], city_b["yesil_skor"]]
        })
        
        fig_grouped = px.bar(
            metrics_df,
            x="Gösterge",
            y=[il_a_name, il_b_name],
            barmode="group",
            color_discrete_sequence=["#38bdf8", "#10b981"]
        )
        fig_grouped.update_layout(height=360, margin=dict(t=20, l=10, r=10, b=10), legend_title_text="")
        st.plotly_chart(fig_grouped, use_container_width=True)
