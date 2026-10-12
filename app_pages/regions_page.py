"""
Bölgeler Analiz Sayfası (Regional Analysis & ANOVA)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from visualization.distribution_charts import create_regional_boxplot
from data_processing.aggregator import aggregate_by_region
from analytics.hypothesis_tests import run_regional_anova


def create_regional_benchmark_bar(df: pd.DataFrame, pollutant: str = "pm25") -> go.Figure:
    """7 Coğrafi Bölge Benchmark & DSÖ Aşım Analizi Yatay Bar Grafiği."""
    # Kirletici sütununu esnek ve büyük/küçük harf duyarsız belirle
    candidates = [pollutant, pollutant.lower(), pollutant.lower().replace(".", ""), "pm25", "PM2.5", "PM_Degeri_ug_m3"]
    pol_col = "pm25"
    for c in candidates:
        if c in df.columns:
            pol_col = c
            break

    # Veri bütünlüğü ve tip temizliği:
    # 1. String virgül/nokta temizliği ve numeric'e zorlama
    # 2. NaN / null / geçersiz kayıtların güvenli biçimde elenmesi
    clean_df = df.copy()
    clean_df[pol_col] = pd.to_numeric(
        clean_df[pol_col].astype(str).str.strip().str.replace(",", "."),
        errors="coerce"
    )
    if "bolge" in clean_df.columns:
        clean_df["bolge"] = clean_df["bolge"].astype(str).str.strip()
    if "il" in clean_df.columns:
        clean_df["il"] = clean_df["il"].astype(str).str.strip()

    clean_df = clean_df.dropna(subset=[pol_col, "bolge", "il"])

    regions_order = ["Doğu Anadolu", "Güneydoğu Anadolu", "Ege", "Marmara", "Akdeniz", "İç Anadolu", "Karadeniz"]
    benchmarks = []

    for b_name in regions_order:
        b_df = clean_df[clean_df["bolge"] == b_name]
        if not b_df.empty:
            mean_val = round(float(b_df[pol_col].mean()), 1)
            # Güvenli en yüksek il tespiti: İndeks uyuşmazlığı ve NaN riskine karşı
            # sort_values(ascending=False).iloc[0] kullanımı
            b_df_sorted = b_df.sort_values(by=pol_col, ascending=False)
            mx_row = b_df_sorted.iloc[0]
            mx_il = str(mx_row["il"]).strip()
            mx_val = round(float(mx_row[pol_col]), 1)
            benchmarks.append({
                "bolge": b_name,
                "mean": mean_val,
                "max_il": mx_il,
                "max_val": mx_val,
                "bar_text": f"{mean_val:.1f} µg/m³ | En Yüksek: {mx_il} ({mx_val:.1f} µg/m³)"
            })

    benchmarks.sort(key=lambda x: x["mean"], reverse=True)

    y_labels = [b["bolge"] for b in benchmarks]
    x_values = [b["mean"] for b in benchmarks]
    text_labels = [b["bar_text"] for b in benchmarks]

    fig = go.Figure(go.Bar(
        x=x_values,
        y=y_labels,
        orientation="h",
        text=text_labels,
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="#ffffff", size=11, family="Plus Jakarta Sans", weight="bold"),
        marker=dict(
            color=x_values,
            colorscale=[
                [0.0, "#0c4a6e"],
                [0.35, "#0284c7"],
                [0.70, "#f97316"],
                [1.0, "#ef4444"]
            ],
            line=dict(color="rgba(255, 255, 255, 0.25)", width=1)
        ),
        hoverinfo="none"
    ))

    # DSÖ 5 µg/m³ yıllık eşik çizgisi
    fig.add_vline(
        x=5,
        line_width=2,
        line_dash="dash",
        line_color="#ef4444",
        annotation_text="DSÖ Yıllık Kılavuz Değeri (5 µg/m³)",
        annotation_position="top right",
        annotation_font=dict(color="#ef4444", size=11, family="Plus Jakarta Sans", weight="bold")
    )

    fig.update_layout(
        margin=dict(l=140, r=20, t=30, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=340,
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.07)",
            tickfont=dict(color="#8faec9", size=11),
            title=dict(text="Bölgesel Ortalama PM2.5 Seviyesi (µg/m³)", font=dict(color="#8faec9", size=11)),
            zeroline=False
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(color="#f8fafc", size=12, family="Plus Jakarta Sans", weight="bold")
        )
    )
    return fig


def render_regions_page(df: pd.DataFrame):
    """
    Türkiye'nin 7 coğrafi bölgesinin hava kalitesi, sanayi ve sağlık profillerini karşılaştırır,
    tek yönlü ANOVA ve Kruskal-Wallis varyans analizini sunar.
    """
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="margin:0; font-size:24px; font-weight:800; color:#ffffff; letter-spacing:-0.5px;">
            Bölgesel Hava Kalitesi &amp; Coğrafi Karşılaştırma
        </h2>
        <p style="margin:4px 0 0 0; font-size:13px; color:#cbd5e1;">
            Türkiye'nin 7 coğrafi bölgesi genelinde hava kirliliği varyansı, sanayi dağılımı ve bölgesel ANOVA analizi.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 1. BÖLÜM: 7 COĞRAFİ BÖLGE BENCHMARK & DSÖ AŞIM ANALİZİ (Genel Bakış'tan taşınan analitik bileşen)
    st.markdown("### 7 Coğrafi Bölge Benchmark &amp; DSÖ Aşım Analizi", unsafe_allow_html=True)
    fig_bench = create_regional_benchmark_bar(df, pollutant="pm25")
    st.plotly_chart(fig_bench, use_container_width=True)
    st.caption("* Kesikli kırmızı çizgi DSÖ güvenli yıllık kılavuz eşiğidir (5 µg/m³). Tüm bölgeler bu eşiğin 6 ila 9 katı üzerindedir.")
    st.caption("Not: Gösterilen bölgesel veriler yıllık konsolidasyon (son 12 ay) ölçümlerini yansıtmakta olup DSÖ yıllık referans kılavuz çizgisi ile karşılaştırılmıştır.")

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 2. BÖLÜM: BÖLGESEL AGREGASYON TABLOSU
    region_summary = aggregate_by_region(df, pollutant="pm25")
    st.markdown("### 7 Coğrafi Bölge Özet Tablosu")

    display_df = region_summary[[
        "bolge", "il_sayisi", "ortalama", "medyan", "std", 
        "toplam_osb", "bolgesel_solunum_olum_100k", "ort_yesil_skor"
    ]].rename(columns={
        "bolge": "Bölge",
        "il_sayisi": "İl Sayısı",
        "ortalama": "Ort. PM2.5 (µg/m³)",
        "medyan": "Medyan PM2.5",
        "std": "Standart Sapma",
        "toplam_osb": "Toplam OSB",
        "bolgesel_solunum_olum_100k": "Solunum Ölümü (100k)",
        "ort_yesil_skor": "Ort. Yeşil Skor"
    })

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 3. BÖLÜM: DAĞILIM VE OSB GRAFİKLERİ
    col_box, col_bar = st.columns([1.2, 1.0])
    with col_box:
        st.markdown("### Bölgesel PM2.5 Dağılımı (Kutu Grafiği)")
        fig_box = create_regional_boxplot(df, pollutant="pm25")
        st.plotly_chart(fig_box, use_container_width=True)

    with col_bar:
        st.markdown("### Bölgesel Toplam OSB Dağılımı")
        fig_osb = px.bar(
            region_summary,
            x="bolge",
            y="toplam_osb",
            color="bolge",
            text="toplam_osb",
            labels={"bolge": "Bölge", "toplam_osb": "OSB Sayısı"}
        )
        fig_osb.update_traces(textposition="outside")
        fig_osb.update_layout(
            height=380, 
            showlegend=False, 
            margin=dict(t=30, l=10, r=10, b=30),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_osb, use_container_width=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 4. BÖLÜM: BÖLGESEL ANOVA VE KRUSKAL-WALLIS
    st.markdown("### Bölgeler Arası Varyans Analizi (ANOVA &amp; Kruskal-Wallis)", unsafe_allow_html=True)
    anova_res = run_regional_anova(df, group_col="bolge", val_col="pm25")

    if anova_res.get("success"):
        st.markdown(f"""
        <div style='background:#031b2e; border:1px solid #093452; border-radius:12px; padding:20px;'>
            <div style='font-size:14px; font-weight:700; color:#00d2ee; margin-bottom:8px;'>
                {anova_res['h0']}
            </div>
            <div style='font-size:13px; color:#cbd5e1; margin-bottom:14px;'>
                {anova_res['h1']}
            </div>
            <div style='display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:12px; margin-bottom:14px;'>
                <div style='background:#021220; padding:12px; border-radius:8px; border:1px solid #07253d;'>
                    <div style='font-size:11px; color:#8faec9;'>Tek Yönlü ANOVA (F)</div>
                    <div style='font-size:18px; font-weight:700; color:#f8fafc;'>F = {anova_res['anova_f']}</div>
                    <div style='font-size:11px; color:{"#00e599" if anova_res["anova_significant"] else "#facc15"};'>p = {anova_res['anova_p']:.4f}</div>
                </div>
                <div style='background:#021220; padding:12px; border-radius:8px; border:1px solid #07253d;'>
                    <div style='font-size:11px; color:#8faec9;'>Kruskal-Wallis (H)</div>
                    <div style='font-size:18px; font-weight:700; color:#f8fafc;'>H = {anova_res['kruskal_h']}</div>
                    <div style='font-size:11px; color:{"#00e599" if anova_res["kruskal_significant"] else "#facc15"};'>p = {anova_res['kruskal_p']:.4f}</div>
                </div>
                <div style='background:#021220; padding:12px; border-radius:8px; border:1px solid #07253d;'>
                    <div style='font-size:11px; color:#8faec9;'>Levene Varyans Homojenliği</div>
                    <div style='font-size:16px; font-weight:700; color:#f8fafc;'>p = {anova_res['levene_p']}</div>
                    <div style='font-size:11px; color:#8faec9;'>{'Varyanslar Eşit' if anova_res['equal_variance'] else 'Heterojen Varyans'}</div>
                </div>
            </div>
            <div style='background:#021220; border-left:4px solid #00e599; padding:12px; border-radius:6px; font-size:13px; color:#cbd5e1;'>
                <b>İstatistiki Sonuç:</b> {anova_res['interpretation']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    with st.expander("Yöntem ve Kaynaklar"):
        st.markdown("""
        - **Bölgesel Agregasyon:** 81 ilin resmi coğrafi bölgelere göre eşleştirilmesi (`data_sources/constants.py`).
        - **ANOVA (F) & Kruskal-Wallis (H):** `scipy.stats` parametrik ve parametrik olmayan varyans analizleri.
        - **Levene Testi:** Varyansların homojenliği testi (p > 0.05 ise homojen, aksi halde heterojen kabul edilir).
        """)
