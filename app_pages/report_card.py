"""
Şehir Karnesi Sayfası (City Report Card)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from typing import Optional
from visualization.components import render_metric_card
from visualization.time_charts import create_timeseries_chart
from data_sources.openmeteo_connector import OpenMeteoAirQualityConnector, get_national_timeseries

def render_report_card_page(df: pd.DataFrame, ts_df: Optional[pd.DataFrame] = None):
    """
    Her il için ayrıntılı hava kalitesi, sanayi ve sağlık karnesini görüntüler.
    """
    st.markdown("### Şehir Karnesi & İl Çevre Profili")
    st.markdown(
        "<p style='color:#94a3b8;'>Türkiye'nin 81 ilinin hava kalitesi, sanayi baskısı ve solunum sağlığı profili karnesi.</p>",
        unsafe_allow_html=True
    )
    
    col_sel1, col_sel2 = st.columns([2, 1])
    with col_sel1:
        iller = sorted(df["il"].unique().tolist())
        q_il = st.query_params.get("il")
        current_session_city = st.session_state.get("selected_city")
        if q_il and q_il in iller:
            default_index = iller.index(q_il)
        elif current_session_city and current_session_city in iller:
            default_index = iller.index(current_session_city)
        else:
            default_index = iller.index("İstanbul") if "İstanbul" in iller else 0
        secilen_il = st.selectbox("İl Seçimi:", iller, index=default_index, key="_report_card_city_select")
        if secilen_il != st.session_state.get("selected_city"):
            st.session_state["selected_city"] = secilen_il
        
        if ts_df is None:
            ts_df = get_national_timeseries(90)

    il_row = df[df["il"] == secilen_il].iloc[0]
    bolge = il_row["bolge"]
    bolge_df = df[df["bolge"] == bolge]
    bolge_ort_pm25 = bolge_df["pm25"].mean()
    turkiye_ort_pm25 = df["pm25"].mean()
    
    with col_sel2:
        st.markdown(f"""
        <div style='background:#0f172a; border:1px solid #1e293b; border-radius:10px; padding:12px; margin-top:12px;'>
            <div style='font-size:12px; color:#94a3b8;'>Coğrafi Bölge & Plaka</div>
            <div style='font-size:16px; font-weight:700; color:#38bdf8;'>{bolge} &bull; Plaka: {int(il_row['plaka']):02d}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    
    # 1. TEMEL GÖSTERGELER (4 Kart)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        delta_bolge = round(il_row["pm25"] - bolge_ort_pm25, 1)
        sign = "+" if delta_bolge > 0 else ""
        render_metric_card(
            title="PM2.5 Konsantrasyonu",
            value=f"{il_row['pm25']:.1f}",
            unit="µg/m³",
            delta=f"{sign}{delta_bolge} µg/m³ (Bölge Ort.)",
            delta_type="positive" if delta_bolge > 0 else "negative"
        )
    with c2:
        render_metric_card(
            title="DSÖ Risk Sınıfı",
            value=il_row["dso_risk"],
            unit="",
            delta=f"DSÖ Eşiğinin {il_row['dso_limit_kat']:.1f} Katı",
            delta_type="positive" if il_row['pm25'] > 15 else "neutral"
        )
    with c3:
        render_metric_card(
            title="Solunum Ölüm Oranı",
            value=f"{il_row['solunum_olum_100k']:.1f}",
            unit="/ 100k",
            delta="TÜİK 2024 (Kaba Hız)",
            delta_type="neutral"
        )
    with c4:
        render_metric_card(
            title="Yeşil Dönüşüm Skoru",
            value=f"{il_row['yesil_skor']:.1f}",
            unit="/ 100",
            delta="Çevresel Başarı Endeksi",
            delta_type="negative" if il_row['yesil_skor'] >= 75 else "positive"
        )
        
    st.write("")
    
    # 2. ORTA BÖLÜM: BÖLGESEL VE TÜRKİYE KARŞILAŞTIRMASI & SANAYİ BİLGİLERİ
    col_chart, col_details = st.columns([1.3, 1.0])
    
    with col_chart:
        st.markdown("#### Bölge ve Türkiye Ortalamasının Karşılaştırması")
        comp_df = pd.DataFrame({
            "Kategori": [f"{secilen_il}", f"{bolge} Bölgesi", "Türkiye Geneli"],
            "PM2.5 (µg/m³)": [il_row["pm25"], bolge_ort_pm25, turkiye_ort_pm25],
            "Renk": ["#38bdf8", "#818cf8", "#94a3b8"]
        })
        fig_comp = px.bar(
            comp_df,
            x="Kategori",
            y="PM2.5 (µg/m³)",
            color="Kategori",
            color_discrete_map={
                f"{secilen_il}": "#38bdf8",
                f"{bolge} Bölgesi": "#818cf8",
                "Türkiye Geneli": "#64748b"
            },
            text="PM2.5 (µg/m³)"
        )
        fig_comp.update_traces(texttemplate="%{text:.1f} µg/m³", textposition="outside")
        fig_comp.add_hline(y=5.0, line_dash="dash", line_color="#ef4444", annotation_text="DSÖ Yıllık Limit (5 µg/m³)")
        fig_comp.update_layout(height=320, showlegend=False, margin=dict(t=20, l=10, r=10, b=10))
        st.plotly_chart(fig_comp, use_container_width=True)
        
    with col_details:
        st.markdown("#### Sanayi ve Demografi Detayları")
        st.markdown(f"""
        <div style='background:#0d1527; border:1px solid #1e293b; border-radius:12px; padding:18px;'>
            <table style='width:100%; border-collapse:collapse; font-size:13px; color:#cbd5e1;'>
                <tr style='border-bottom:1px solid #1e293b; height:32px;'>
                    <td><b>Resmi Nüfus (ADNKS):</b></td>
                    <td style='text-align:right; color:#f8fafc; font-weight:700;'>{il_row['nufus']:,}</td>
                </tr>
                <tr style='border-bottom:1px solid #1e293b; height:32px;'>
                    <td><b>Toplam OSB Sayısı:</b></td>
                    <td style='text-align:right; color:#f8fafc; font-weight:700;'>{il_row['toplam_osb']} ({il_row['faal_osb']} Faal)</td>
                </tr>
                <tr style='border-bottom:1px solid #1e293b; height:32px;'>
                    <td><b>Toplam OSB Alanı:</b></td>
                    <td style='text-align:right; color:#f8fafc; font-weight:700;'>{il_row['osb_alani_hektar'] / 10.0:,.1f} Hektar</td>
                </tr>
                <tr style='border-bottom:1px solid #1e293b; height:32px;'>
                    <td><b>Sanayi Parsel Sayısı:</b></td>
                    <td style='text-align:right; color:#f8fafc; font-weight:700;'>{il_row['toplam_parsel']:,} Parsel</td>
                </tr>
                <tr style='height:32px;'>
                    <td><b>TÜİK 2024 Solunum Ölümü:</b></td>
                    <td style='text-align:right; color:#ef4444; font-weight:700;'>{int(il_row['solunum_olum']):,} Kişi</td>
                </tr>
            </table>
            <div style='font-size:10.5px; color:#64748b; margin-top:10px; line-height:1.4;'>
                * Solunum ölümleri tüm solunum sistemi hastalıklarını kapsar; doğrudan hava kirliliğine atfedilen pay değildir. Yaşa göre standardize edilmemiş kaba hızdır.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    
    # 3. İL İÇİN ZAMAN SERİSİ TRENDİ
    st.markdown(f"#### {secilen_il} İçin Hava Kalitesi Eğilimi")
    # Seçilen ilin koordinatlarına göre zaman serisi ölçekleme
    il_ratio = il_row["pm25"] / max(turkiye_ort_pm25, 1.0)
    il_ts = ts_df.copy()
    il_ts["pm25"] = (il_ts["pm25"] * il_ratio).round(2)
    il_ts["pm10"] = (il_ts["pm10"] * il_ratio).round(2)
    
    fig_il_ts = create_timeseries_chart(
        il_ts,
        window_days=30,
        pollutant="pm25",
        title=f"{secilen_il} Son 30 Günlük PM2.5 Seyri (Tahmini CAMS Reanaliz)"
    )
    st.plotly_chart(fig_il_ts, use_container_width=True)
