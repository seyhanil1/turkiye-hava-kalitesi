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
        il_a_name = st.selectbox("1. İl:", iller, index=default_a)
    with col2:
        default_b = iller.index("Ankara") if "Ankara" in iller else 1
        il_b_name = st.selectbox("2. İl:", iller, index=default_b)
        
    if il_a_name == il_b_name:
        st.info("Lütfen karşılaştırma için iki farklı şehir seçiniz.")
        return
        
    city_a = df[df["il"] == il_a_name].iloc[0]
    city_b = df[df["il"] == il_b_name].iloc[0]
    
    # 1. KAFA KAFAYA METRİK KARTLARI
    st.markdown("#### Kafa Kafaya Metrik Karşılaştırması")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        pm_a = f"{float(city_a['pm25']):.1f}".replace(".", ",")
        pm_b = f"{float(city_b['pm25']):.1f}".replace(".", ",")
        diff_pm = float(city_a["pm25"]) - float(city_b["pm25"])
        diff_pm_str = f"{abs(diff_pm):.1f}".replace(".", ",")
        sign_pm = "+" if diff_pm > 0 else ("-" if diff_pm < 0 else "")
        render_metric_card(
            title="PM2.5 Kirliliği",
            value=f"{pm_a} vs {pm_b}",
            unit=" µg/m³",
            delta=f"{sign_pm}{diff_pm_str} µg/m³ fark",
            delta_type="positive" if diff_pm > 0 else ("negative" if diff_pm < 0 else "neutral")
        )
    with m2:
        sol_a = f"{float(city_a['solunum_olum_100k']):.1f}".replace(".", ",")
        sol_b = f"{float(city_b['solunum_olum_100k']):.1f}".replace(".", ",")
        diff_sol = float(city_a["solunum_olum_100k"]) - float(city_b["solunum_olum_100k"])
        diff_sol_str = f"{abs(diff_sol):.1f}".replace(".", ",")
        sign_sol = "+" if diff_sol > 0 else ("-" if diff_sol < 0 else "")
        render_metric_card(
            title="TÜİK Solunum Ölüm Hızı",
            value=f"{sol_a} vs {sol_b}",
            unit=" / 100k",
            delta=f"{sign_sol}{diff_sol_str} / 100k fark",
            delta_type="positive" if diff_sol > 0 else ("negative" if diff_sol < 0 else "neutral")
        )
    with m3:
        osb_a = int(round(city_a.get("toplam_osb", 0))) if pd.notnull(city_a.get("toplam_osb")) else 0
        osb_b = int(round(city_b.get("toplam_osb", 0))) if pd.notnull(city_b.get("toplam_osb")) else 0
        faal_a = int(round(city_a.get("faal_osb", 0))) if pd.notnull(city_a.get("faal_osb")) else 0
        faal_b = int(round(city_b.get("faal_osb", 0))) if pd.notnull(city_b.get("faal_osb")) else 0
        render_metric_card(
            title="Toplam OSB Sayısı",
            value=f"{osb_a} vs {osb_b}",
            unit=" OSB",
            delta=f"{faal_a} vs {faal_b} Faal OSB",
            delta_type="neutral"
        )
    with m4:
        yesil_a = f"{float(city_a['yesil_skor']):.1f}".replace(".", ",")
        yesil_b = f"{float(city_b['yesil_skor']):.1f}".replace(".", ",")
        render_metric_card(
            title="Yeşil Dönüşüm Skoru",
            value=f"{yesil_a} vs {yesil_b}",
            unit=" / 100 Puan",
            delta="Yüksek skor = Daha temiz",
            delta_type="negative" if float(city_a["yesil_skor"]) > float(city_b["yesil_skor"]) else "positive"
        )
        
    st.write("")
    
    # 2. RADAR VE ÇUBUK GRAFİK
    col_radar, col_bars = st.columns([1.1, 1.0])
    with col_radar:
        fig_radar = create_duel_radar_chart(city_a, city_b)
        st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})
        
    with col_bars:
        st.markdown(f"#### {il_a_name} ve {il_b_name} Gösterge Profili")
        
        categories = ["PM2.5 Kirliliği", "Solunum Ölüm Hızı", "Yeşil Dönüşüm Skoru"]
        
        # 0-100 normalize ölçeği (ölçek çakışmasını önlemek için)
        norm_a = [
            min(100.0, max(0.0, float(city_a["pm25"]) / 85.0 * 100.0)),
            min(100.0, max(0.0, float(city_a["solunum_olum_100k"]) / 100.0 * 100.0)),
            min(100.0, max(0.0, float(city_a["yesil_skor"])))
        ]
        norm_b = [
            min(100.0, max(0.0, float(city_b["pm25"]) / 85.0 * 100.0)),
            min(100.0, max(0.0, float(city_b["solunum_olum_100k"]) / 100.0 * 100.0)),
            min(100.0, max(0.0, float(city_b["yesil_skor"])))
        ]
        
        text_a = [
            f"{float(city_a['pm25']):.1f} µg/m³".replace(".", ","),
            f"{float(city_a['solunum_olum_100k']):.1f} / 100k".replace(".", ","),
            f"{float(city_a['yesil_skor']):.1f} Puan".replace(".", ",")
        ]
        text_b = [
            f"{float(city_b['pm25']):.1f} µg/m³".replace(".", ","),
            f"{float(city_b['solunum_olum_100k']):.1f} / 100k".replace(".", ","),
            f"{float(city_b['yesil_skor']):.1f} Puan".replace(".", ",")
        ]
        
        fig_grouped = go.Figure()
        fig_grouped.add_trace(go.Bar(
            name=il_a_name,
            x=categories,
            y=norm_a,
            text=text_a,
            textposition="outside",
            textfont=dict(color="#f8fafc", size=10),
            marker_color="#38bdf8",
            hovertemplate=f"<b>{il_a_name}</b><br>%{{x}}: %{{text}}<extra></extra>"
        ))
        fig_grouped.add_trace(go.Bar(
            name=il_b_name,
            x=categories,
            y=norm_b,
            text=text_b,
            textposition="outside",
            textfont=dict(color="#f8fafc", size=10),
            marker_color="#10b981",
            hovertemplate=f"<b>{il_b_name}</b><br>%{{x}}: %{{text}}<extra></extra>"
        ))
        
        fig_grouped.update_layout(
            barmode="group",
            height=360,
            margin=dict(t=30, l=15, r=15, b=20),
            yaxis=dict(
                title="",  # İngilizce 'value' etiketi kaldırıldı
                range=[0, 115],
                gridcolor="#1e293b",
                showticklabels=False
            ),
            xaxis=dict(
                tickfont=dict(color="#f8fafc", size=10),
                gridcolor="#1e293b"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.22,
                xanchor="center",
                x=0.5,
                font=dict(color="#f8fafc", size=10)
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        
        st.plotly_chart(fig_grouped, use_container_width=True, config={"displayModeBar": False})
