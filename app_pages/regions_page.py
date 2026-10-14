"""
Bölgeler Analiz Sayfası (Regional Analysis & ANOVA)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

from decimal import Decimal, ROUND_HALF_UP
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
            mean_raw = float(b_df[pol_col].mean())
            # Matematiksel doğru yuvarlama (Round half up): Marmara 35.65 -> 35.7
            mean_val = float(Decimal(f"{mean_raw:.4f}").quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
            # Güvenli en yüksek il tespiti: İndeks uyuşmazlığı ve NaN riskine karşı
            # sort_values(ascending=False).iloc[0] kullanımı
            b_df_sorted = b_df.sort_values(by=pol_col, ascending=False)
            mx_row = b_df_sorted.iloc[0]
            mx_il = str(mx_row["il"]).strip()
            mx_raw = float(mx_row[pol_col])
            mx_val = float(Decimal(f"{mx_raw:.4f}").quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
            
            mean_str = f"{mean_val:.1f}".replace(".", ",")
            mx_str = f"{mx_val:.1f}".replace(".", ",")
            benchmarks.append({
                "bolge": b_name,
                "mean": mean_val,
                "max_il": mx_il,
                "max_val": mx_val,
                "bar_text": f"{mean_str} µg/m³ | En Yüksek: {mx_il} ({mx_str} µg/m³)"
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
                [0.0, "#083358"],
                [0.5, "#0284c7"],
                [1.0, "#38bdf8"]
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
    st.plotly_chart(fig_bench, use_container_width=True, config={'displayModeBar': False})
    st.caption("* Kesikli kırmızı çizgi DSÖ yıllık kılavuz sınırıdır (5 µg/m³). Tüm bölge ortalamaları bu eşiğin 6 ila 9 katı üzerindedir.")
    st.caption("Not: Gösterilen bölgesel veriler Doğrulanmış 12 Aylık Konsolidasyon Dönemi ölçümlerini yansıtmakta olup DSÖ yıllık referans kılavuz çizgisi ile karşılaştırılmıştır.")

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 2. BÖLÜM: BÖLGESEL AGREGASYON TABLOSU
    region_summary = aggregate_by_region(df, pollutant="pm25")
    st.markdown("### 7 Coğrafi Bölge Özet Tablosu")

    display_df = region_summary[[
        "bolge", "il_sayisi", "ortalama", "medyan", "std", 
        "toplam_osb", "bolgesel_solunum_olum_100k"
    ]].copy()

    formatted_df = pd.DataFrame()
    formatted_df["Bölge"] = display_df["bolge"]
    formatted_df["İl Sayısı"] = display_df["il_sayisi"].astype(int)
    formatted_df["Ort. PM2.5 (µg/m³)"] = display_df["ortalama"].apply(lambda x: f"{x:.2f}".replace(".", ","))
    formatted_df["Medyan PM2.5 (µg/m³)"] = display_df["medyan"].apply(lambda x: f"{x:.2f}".replace(".", ","))
    formatted_df["Standart Sapma"] = display_df["std"].apply(lambda x: f"{x:.2f}".replace(".", ","))
    formatted_df["Toplam OSB"] = display_df["toplam_osb"].astype(int)
    formatted_df["Solunum Ölüm Hızı (Yüz Binde)"] = display_df["bolgesel_solunum_olum_100k"].apply(lambda x: f"{x:.1f}".replace(".", ","))

    st.dataframe(
        formatted_df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 3. BÖLÜM: DAĞILIM VE OSB GRAFİKLERİ
    col_box, col_bar = st.columns([1.2, 1.0])
    with col_box:
        st.markdown("### Bölgesel PM2.5 Dağılımı (Kutu Grafiği)")
        fig_box = create_regional_boxplot(df, pollutant="pm25")
        fig_box.update_traces(
            boxpoints="outliers",
            marker=dict(color="#00d2ee", size=5),
            line=dict(color="#00d2ee", width=1.5),
            fillcolor="rgba(0, 210, 238, 0.2)"
        )
        fig_box.update_layout(
            height=400,
            margin=dict(b=70, t=40, l=50, r=20),
            xaxis=dict(title=None, tickangle=-45, tickfont=dict(color="#94a3b8", size=11)),
            yaxis=dict(gridcolor="#1e293b", tickfont=dict(color="#94a3b8", size=10))
        )
        st.plotly_chart(fig_box, use_container_width=True, config={'displayModeBar': False})

    with col_bar:
        st.markdown("### Bölgesel Toplam OSB Dağılımı")
        fig_osb = px.bar(
            region_summary,
            x="bolge",
            y="toplam_osb",
            text="toplam_osb",
            labels={"toplam_osb": "OSB Sayısı"}
        )
        fig_osb.update_traces(
            marker=dict(
                color="rgba(0, 210, 238, 0.65)",
                line=dict(color="#00d2ee", width=1.5)
            ),
            textposition="outside",
            textfont=dict(color="#f8fafc", size=11)
        )
        fig_osb.update_layout(
            height=400, 
            showlegend=False, 
            margin=dict(b=70, t=40, l=50, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title=None, tickfont=dict(color="#94a3b8", size=11), tickangle=-45),
            yaxis=dict(
                title=dict(text="OSB Sayısı", font=dict(color="#94a3b8", size=11)),
                gridcolor="#1e293b", 
                tickfont=dict(color="#94a3b8", size=10)
            )
        )
        st.plotly_chart(fig_osb, use_container_width=True, config={'displayModeBar': False})

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 4. BÖLÜM: BÖLGESEL ANOVA VE KRUSKAL-WALLIS
    st.markdown("### Bölgeler Arası Varyans Analizi (ANOVA &amp; Kruskal-Wallis)", unsafe_allow_html=True)
    anova_res = run_regional_anova(df, group_col="bolge", val_col="pm25")

    if anova_res.get("success"):
        f_val_str = f"{anova_res['anova_f']:.2f}".replace(".", ",")
        f_p_str = f"{anova_res['anova_p']:.3f}".replace(".", ",")
        h_val_str = f"{anova_res['kruskal_h']:.2f}".replace(".", ",")
        h_p_str = f"{anova_res['kruskal_p']:.3f}".replace(".", ",")
        levene_p_str = f"{anova_res['levene_p']:.3f}".replace(".", ",")

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
                    <div style='font-size:18px; font-weight:700; color:#f8fafc;'>F = {f_val_str}</div>
                    <div style='font-size:11px; color:{"#00e599" if anova_res["anova_significant"] else "#facc15"};'>p = {f_p_str}</div>
                </div>
                <div style='background:#021220; padding:12px; border-radius:8px; border:1px solid #07253d;'>
                    <div style='font-size:11px; color:#8faec9;'>Kruskal-Wallis (H)</div>
                    <div style='font-size:18px; font-weight:700; color:#f8fafc;'>H = {h_val_str}</div>
                    <div style='font-size:11px; color:{"#00e599" if anova_res["kruskal_significant"] else "#facc15"};'>p = {h_p_str}</div>
                </div>
                <div style='background:#021220; padding:12px; border-radius:8px; border:1px solid #07253d;'>
                    <div style='font-size:11px; color:#8faec9;'>Levene Varyans Homojenliği</div>
                    <div style='font-size:16px; font-weight:700; color:#f8fafc;'>p = {levene_p_str}</div>
                    <div style='font-size:11px; color:#8faec9;'>{'Varyanslar Eşit' if anova_res['equal_variance'] else 'Heterojen Varyans'}</div>
                </div>
            </div>
            <div style='background:#021220; border-left:4px solid #00e599; padding:12px; border-radius:6px; font-size:13px; color:#cbd5e1;'>
                <b>İstatistiksel Değerlendirme:</b> {anova_res['interpretation']}
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
