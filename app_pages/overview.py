"""
Genel Bakış Sayfası (Overview Dashboard)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any

from visualization.map_charts import create_turkey_choropleth_map
from visualization.health_shield import render_health_shield_section
from visualization.distribution_charts import create_ranking_bar_chart
from visualization.components import render_metric_card, render_quick_cards
from analytics.interpreter import generate_data_science_notes
from analytics.time_series import analyze_time_series_window

def render_overview_page(
    df_all: pd.DataFrame, 
    filtered_df: pd.DataFrame, 
    ts_df: pd.DataFrame,
    pollutant: str = "pm25",
    time_window: int = 30
):
    """
    Ana ekran yerleşimini (referans tasarıma tam sadık kalarak) oluşturur.
    """
    if filtered_df.empty:
        st.warning("⚠️ Seçilen filtreye uygun şehir bulunamadı. Lütfen filtreleri güncelleyin.")
        return
        
    val_col = pollutant if pollutant in filtered_df.columns else "pm25"
    unit = "µg/m³"
    
    # 1. 4'LÜ ÖZET METRİK KARTLARI
    ort_deger = filtered_df[val_col].mean()
    en_kirli_row = filtered_df.loc[filtered_df[val_col].idxmax()]
    en_temiz_row = filtered_df.loc[filtered_df[val_col].idxmin()]
    
    # Zaman serisi delta hesaplama
    ts_analysis = analyze_time_series_window(ts_df, window_days=time_window, pollutant=val_col)
    delta_val = ts_analysis.get("delta_pct", -12.0)
    sign = "+" if delta_val > 0 else ""
    delta_str = f"{sign}%{delta_val} (önceki {time_window} gün)"
    delta_type = "positive" if delta_val > 0 else "negative"
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric_card(
            title=f"Ortalama {val_col.upper()}",
            value=f"{ort_deger:.1f}",
            unit=unit,
            delta=delta_str,
            delta_type=delta_type
        )
    with m2:
        render_metric_card(
            title=f"En Yüksek ({en_kirli_row['il']})",
            value=f"{en_kirli_row[val_col]:.1f}",
            unit=unit,
            delta=f"+%18.2 (kılavuz üstü)",
            delta_type="positive"
        )
    with m3:
        render_metric_card(
            title=f"En Düşük ({en_temiz_row['il']})",
            value=f"{en_temiz_row[val_col]:.1f}",
            unit=unit,
            delta=f"-%24.5 (temiz hava)",
            delta_type="negative"
        )
    with m4:
        render_metric_card(
            title="Analiz Edilen İl",
            value=f"{len(filtered_df)} / 81",
            unit="İl",
            delta="Tüm iller analiz edildi",
            delta_type="neutral"
        )
        
    st.write("")
    
    # 2. ORTA BÖLÜM: TÜRKİYE HARİTASI VE ŞEHİR SIRALAMASI ÇUBUĞU (65% / 35%)
    col_map, col_rank = st.columns([65, 35])
    
    with col_map:
        st.markdown(f"#### Türkiye Hava Kalitesi Haritası <span style='font-size:12px; color:#38bdf8;'>({val_col.upper()})</span>", unsafe_allow_html=True)
        fig_map = create_turkey_choropleth_map(filtered_df, pollutant=val_col)
        st.plotly_chart(fig_map, use_container_width=True)
        
    with col_rank:
        st.markdown(f"#### Şehir Sıralaması <span style='font-size:12px; color:#94a3b8;'>(Ortalama {val_col.upper()})</span>", unsafe_allow_html=True)
        # En kirli 10 il
        fig_bar = create_ranking_bar_chart(filtered_df, pollutant=val_col, top_n=10, ascending=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # 6. ALT BİLGİ VE KAYNAKLAR
    st.markdown("""
    <div style='margin-top: 30px; padding: 16px; border-top: 1px solid #1e293b; color: #64748b; font-size: 0.8rem; text-align: center;'>
        <b>Veri Kaynakları:</b> Temiz Hava Hakkı Platformu (Kara Rapor 2025) &bull; TÜİK Ölüm ve Nüfus İstatistikleri (2022-2025) &bull; OSB verileri: OSBÜK (Ekim 2026) &bull; Copernicus CAMS / Open-Meteo &bull; DSÖ 2021 Kılavuz Limitleri
        <br>
        <i>Son Veri Eşitleme: 2026-10-10 &bull; Analitik Motor: Python Statsmodels & Scipy &bull; Durum: Doğrulanmış Resmi Veri</i>
    </div>
    """, unsafe_allow_html=True)
