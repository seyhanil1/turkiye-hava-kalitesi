"""
İl Grupları Modülü
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

81 İl İçin Çeyreklik (Quantile) Dağılımı ve OSB-Kirlilik Grup Sınıflandırması:
1. Kategori A (Düşük OSB, yüksek PM2.5): OSB sayısı alt %25, PM2.5 üst %25
2. Kategori B (Yüksek OSB, yüksek PM2.5): OSB sayısı üst %25, PM2.5 üst %25
3. Normal: Diğer dengeli iller
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Tuple, List


def calculate_quantiles_and_anomalies(df: pd.DataFrame) -> Tuple[float, float, float, float, pd.DataFrame, pd.DataFrame]:
    """
    81 ilin pm25 ve osb_sayisi çeyrekliklerini (quantile) hesaplar,
    Kategori A ve Kategori B illerini filtreler.
    """
    q1_osb = float(df["osb_sayisi"].quantile(0.25))
    q3_osb = float(df["osb_sayisi"].quantile(0.75))
    q1_pm25 = float(df["pm25"].quantile(0.25))
    q3_pm25 = float(df["pm25"].quantile(0.75))

    # Kategori A: OSB alt %25 ve PM2.5 üst %25
    kat_a_df = df[(df["osb_sayisi"] <= q1_osb) & (df["pm25"] >= q3_pm25)].copy()

    # Kategori B: OSB üst %25 ve PM2.5 üst %25
    kat_b_df = df[(df["osb_sayisi"] >= q3_osb) & (df["pm25"] >= q3_pm25)].copy()

    return q1_osb, q3_osb, q1_pm25, q3_pm25, kat_a_df, kat_b_df


class CategoryStr(str):
    """Hem tam rozet metni hem de kısa kategori ismiyle eşitlik kontrolü sağlayan string sınıfı."""
    def __eq__(self, other):
        if not isinstance(other, str):
            return False
        if super().__eq__(other):
            return True
        if self.startswith("Kategori A") and other == "Kategori A":
            return True
        if self.startswith("Kategori B") and other == "Kategori B":
            return True
        if ("Orta Segment" in self or "Dengeli" in self) and other == "Normal":
            return True
        return False


def determine_city_category(
    row: pd.Series, 
    q1_osb: float, 
    q3_osb: float, 
    q1_pm25: float, 
    q3_pm25: float
) -> str:
    """
    Seçilen ilin çeyreklik (Q1/Q3) eşiklerine göre hangi gruba girdiğini döndürür.
    Bu yalnızca betimleyici bir gruplamadır; nedensellik veya gelecek tahmini içermez.

    Koşullar:
    - OSB <= Q1 ve PM2.5 >= Q3: "Kategori A: Düşük OSB, Yüksek Kirlilik"
    - OSB >= Q3 ve PM2.5 >= Q3: "Kategori B: Yüksek OSB, Yüksek Kirlilik"
    - PM2.5 >= Q3, OSB orta segmentte: "Kategori Dışı (Yüksek Kirlilik / Orta Sanayi)"
    - Diğerleri: "Kategori Dışı (Orta Segment / Dengeli)"
    """
    osb = float(row["osb_sayisi"])
    pm25 = float(row["pm25"])

    if osb <= q1_osb and pm25 >= q3_pm25:
        return CategoryStr("Kategori A: Düşük OSB, Yüksek Kirlilik")
    elif osb >= q3_osb and pm25 >= q3_pm25:
        return CategoryStr("Kategori B: Yüksek OSB, Yüksek Kirlilik")
    elif pm25 >= q3_pm25:
        return CategoryStr("Kategori Dışı (Yüksek Kirlilik / Orta Sanayi)")
    else:
        return CategoryStr("Kategori Dışı (Orta Segment / Dengeli)")


def render_ai_forecast_page(df: pd.DataFrame):
    """
    İl Grupları sayfasını oluşturur (OSB ve PM2.5 çeyreklik gruplaması).
    """
    # 1. CSS & ANİMASYON ENJEKSİYONU
    st.markdown("""
    <style>
    /* CSS Animasyonlu Pulsing Glow Efektleri */
    @keyframes pulseGlowA {
        0% { box-shadow: 0 0 10px rgba(245, 158, 11, 0.35), inset 0 0 10px rgba(245, 158, 11, 0.1); border-color: #f59e0b; }
        50% { box-shadow: 0 0 28px rgba(245, 158, 11, 0.8), inset 0 0 22px rgba(245, 158, 11, 0.25); border-color: #fbbf24; }
        100% { box-shadow: 0 0 10px rgba(245, 158, 11, 0.35), inset 0 0 10px rgba(245, 158, 11, 0.1); border-color: #f59e0b; }
    }
    
    @keyframes pulseGlowB {
        0% { box-shadow: 0 0 12px rgba(239, 68, 68, 0.4), inset 0 0 12px rgba(239, 68, 68, 0.12); border-color: #ef4444; }
        50% { box-shadow: 0 0 32px rgba(239, 68, 68, 0.9), inset 0 0 28px rgba(239, 68, 68, 0.3); border-color: #f87171; }
        100% { box-shadow: 0 0 12px rgba(239, 68, 68, 0.4), inset 0 0 12px rgba(239, 68, 68, 0.12); border-color: #ef4444; }
    }
    
    @keyframes pulseGlowNormal {
        0% { box-shadow: 0 0 8px rgba(0, 229, 219, 0.25); border-color: #00e5db; }
        50% { box-shadow: 0 0 22px rgba(0, 229, 219, 0.65); border-color: #38bdf8; }
        100% { box-shadow: 0 0 8px rgba(0, 229, 219, 0.25); border-color: #00e5db; }
    }

    /* Şık UI/UX Bilgi Balonları (info-bubble) */
    .info-bubble {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 20px 24px !important;
        margin-bottom: 16px !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    /* Üzerine gelince hafif zıplayan hover efekti */
    .info-bubble:hover {
        transform: translateY(-5px) !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 14px 30px rgba(0, 0, 0, 0.55), 0 0 20px rgba(56, 189, 248, 0.25) !important;
    }

    .pulse-box-a {
        animation: pulseGlowA 2.5s infinite ease-in-out !important;
    }
    .pulse-box-b {
        animation: pulseGlowB 2s infinite ease-in-out !important;
    }
    .pulse-box-normal {
        animation: pulseGlowNormal 3s infinite ease-in-out !important;
    }

    /* Neon Başlık Renkleri */
    .neon-blue-title {
        color: #38bdf8 !important;
        text-shadow: 0 0 12px rgba(56, 189, 248, 0.7);
        font-size: 17px;
        font-weight: 700;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .neon-red-title {
        color: #ef4444 !important;
        text-shadow: 0 0 12px rgba(239, 68, 68, 0.7);
        font-size: 17px;
        font-weight: 700;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .neon-amber-title {
        color: #f59e0b !important;
        text-shadow: 0 0 12px rgba(245, 158, 11, 0.7);
        font-size: 17px;
        font-weight: 700;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .bubble-text {
        color: #e2e8f0;
        font-size: 14.5px;
        line-height: 1.65;
        margin: 0;
    }

    .kpi-chip {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Başlık ve Üst Açıklama
    st.markdown("""
    <div style='margin-bottom: 24px;'>
        <h2 style='color:#f8fafc; margin:0; font-size:24px; font-weight:700;'>
            İl Grupları
        </h2>
        <p style='color:#94a3b8; margin:4px 0 0 0; font-size:14px;'>
            81 İl İçin Çeyreklik (Quantile) Dağılımı ve OSB-Kirlilik Grup Sınıflandırması
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 1. AŞAMA: DİNAMİK ANOMALİ VE ÇEYREKLİK ANALİZİ
    q1_osb, q3_osb, q1_pm25, q3_pm25, kat_a_df, kat_b_df = calculate_quantiles_and_anomalies(df)

    q1_pm_str = f"{q1_pm25:.1f}".replace(".", ",")
    q3_pm_str = f"{q3_pm25:.1f}".replace(".", ",")

    # Üst İstatistik Özet Kartları
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    with col_q1:
        st.markdown(f"""
        <div class='info-bubble' style='padding:14px 18px;'>
            <div style='color:#94a3b8; font-size:12px;'>OSB Sayısı Eşikleri (81 İl)</div>
            <div style='color:#38bdf8; font-size:18px; font-weight:700; margin-top:4px;'>
                Q1: {q1_osb:.0f} | Q3: {q3_osb:.0f}
            </div>
            <div style='color:#64748b; font-size:11px; margin-top:2px;'>Alt %25 ≤ {q1_osb:.0f} &bull; Üst %25 ≥ {q3_osb:.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_q2:
        st.markdown(f"""
        <div class='info-bubble' style='padding:14px 18px;'>
            <div style='color:#94a3b8; font-size:12px;'>PM2.5 Kirlilik Eşikleri</div>
            <div style='color:#00e5db; font-size:18px; font-weight:700; margin-top:4px;'>
                Q1: {q1_pm_str} | Q3: {q3_pm_str}
            </div>
            <div style='color:#64748b; font-size:11px; margin-top:2px;'>Alt %25 ≤ {q1_pm_str} µg/m³ &bull; Üst %25 ≥ {q3_pm_str} µg/m³</div>
        </div>
        """, unsafe_allow_html=True)

    with col_q3:
        st.markdown(f"""
        <div class='info-bubble' style='padding:14px 18px;'>
            <div style='color:#94a3b8; font-size:12px;'>Kategori A (Düşük OSB, Yüksek PM2.5)</div>
            <div style='color:#f59e0b; font-size:18px; font-weight:700; margin-top:4px;'>
                {len(kat_a_df)} İl Tespit Edildi
            </div>
            <div style='color:#64748b; font-size:11px; margin-top:2px;'>Düşük OSB, Yüksek Kirlilik</div>
        </div>
        """, unsafe_allow_html=True)

    with col_q4:
        st.markdown(f"""
        <div class='info-bubble' style='padding:14px 18px;'>
            <div style='color:#94a3b8; font-size:12px;'>Kategori B (Yüksek OSB, Yüksek PM2.5)</div>
            <div style='color:#ef4444; font-size:18px; font-weight:700; margin-top:4px;'>
                {len(kat_b_df)} İl Tespit Edildi
            </div>
            <div style='color:#64748b; font-size:11px; margin-top:2px;'>Yüksek OSB, Yüksek Kirlilik</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # 2. AŞAMA: DİNAMİK İL SEÇİCİ (st.selectbox) & STATE SENKRONİZASYONU
    iller = sorted(df["il"].unique().tolist())
    
    # URL veya st.session_state üzerinden aktif şehir senkronizasyonu
    if "city" in st.query_params:
        del st.query_params["city"]
    q_il = st.query_params.get("il")
    
    if q_il and q_il in iller:
        active_city = q_il
    elif st.session_state.get("selected_city") in iller:
        active_city = st.session_state["selected_city"]
    elif "Iğdır" in iller:
        active_city = "Iğdır"
    else:
        active_city = iller[0] if iller else ""

    # Global state ve URL senkronizasyonu
    st.session_state["selected_city"] = active_city
    st.query_params["il"] = active_city

    if st.session_state.get("province_groups_city_select") != active_city:
        st.session_state["province_groups_city_select"] = active_city

    col_sel_left, col_sel_right = st.columns([1.5, 2.5])
    with col_sel_left:
        def on_city_change():
            chosen = st.session_state.get("province_groups_city_select")
            if chosen and chosen in iller:
                st.session_state["selected_city"] = chosen
                st.query_params["il"] = chosen

        secilen_il = st.selectbox(
            "Analiz Edilecek İli Seçin:",
            iller,
            key="province_groups_city_select",
            on_change=on_city_change,
            help="81 il arasından dilediğinizi seçerek ilin OSB ve PM2.5 çeyreklik grubunu inceleyin."
        )
        if secilen_il and secilen_il != st.session_state.get("selected_city"):
            st.session_state["selected_city"] = secilen_il
            st.query_params["il"] = secilen_il

    il_row = df[df["il"] == secilen_il].iloc[0]
    category = determine_city_category(il_row, q1_osb, q3_osb, q1_pm25, q3_pm25)

    with col_sel_right:
        # Seçilen ilin hızlı rozet durumu
        if category == "Kategori A" or category.startswith("Kategori A"):
            cat_badge_html = "<span style='background:rgba(245,158,11,0.15); border:1px solid #f59e0b; color:#fbbf24; padding:6px 14px; border-radius:20px; font-size:13px; font-weight:700;'>Kategori A: Düşük OSB, Yüksek Kirlilik</span>"
        elif category == "Kategori B" or category.startswith("Kategori B"):
            cat_badge_html = "<span style='background:rgba(239,68,68,0.15); border:1px solid #ef4444; color:#f87171; padding:6px 14px; border-radius:20px; font-size:13px; font-weight:700;'>Kategori B: Yüksek OSB, Yüksek Kirlilik</span>"
        elif "Yüksek Kirlilik" in category:
            cat_badge_html = "<span style='background:rgba(249,115,22,0.15); border:1px solid #f97316; color:#fb923c; padding:6px 14px; border-radius:20px; font-size:13px; font-weight:700;'>Kategori Dışı (Yüksek Kirlilik / Orta Sanayi)</span>"
        else:
            cat_badge_html = "<span style='background:rgba(0,229,219,0.15); border:1px solid #00e5db; color:#38bdf8; padding:6px 14px; border-radius:20px; font-size:13px; font-weight:700;'>Kategori Dışı (Orta Segment / Dengeli)</span>"

        pm_val_now_str = f"{float(il_row['pm25']):.1f}".replace(".", ",")
        dso_kat_val = round(float(il_row["pm25"]) / 5.0, 1)
        dso_kat_str = f"{dso_kat_val:.1f}".replace(".", ",")
        st.markdown(
            f"<div style='margin-top:28px; display:flex; align-items:center; gap:12px; flex-wrap:wrap;'>"
            f"{cat_badge_html}"
            f"<span style='color:#94a3b8; font-size:13px;'>"
            f"Mevcut PM2.5: <strong style='color:#f8fafc;'>{pm_val_now_str} µg/m³</strong> ({dso_kat_str}× DSÖ) &bull; "
            f"OSB Sayısı: <strong style='color:#f8fafc;'>{int(il_row['osb_sayisi'])} Adet</strong>"
            f"</span></div>",
            unsafe_allow_html=True
        )

    # 4. AŞAMA ALT BÖLÜM: DİNAMİK OLARAK FİLTRELENEN TÜM KATEGORİ LİSTELERİ
    st.write("")
    st.markdown("<hr style='border-color:#1e293b; margin:20px 0;'>", unsafe_allow_html=True)
    st.markdown("#### 81 İl Dağılım Grupları")

    chips_a = []
    for _, r in kat_a_df.sort_values(by="pm25", ascending=False).iterrows():
        p_str = f"{float(r['pm25']):.1f}".replace(".", ",")
        o_str = f"{int(r['osb_sayisi'])} Adet"
        chips_a.append(
            f"<span class='kpi-chip' style='background:#2a1b0a; border:1px solid #f59e0b; color:#fbbf24;'>"
            f"{r['il']} (PM2.5: {p_str} µg/m³, OSB: {o_str})</span>"
        )
    chips_a_html = "".join(chips_a)

    chips_b = []
    for _, r in kat_b_df.sort_values(by="pm25", ascending=False).iterrows():
        p_str = f"{float(r['pm25']):.1f}".replace(".", ",")
        o_str = f"{int(r['osb_sayisi'])} Adet"
        chips_b.append(
            f"<span class='kpi-chip' style='background:#2d1215; border:1px solid #ef4444; color:#f87171;'>"
            f"{r['il']} (PM2.5: {p_str} µg/m³, OSB: {o_str})</span>"
        )
    chips_b_html = "".join(chips_b)

    col_list_a, col_list_b = st.columns(2)
    with col_list_a:
        st.markdown(f"""
        <div class='info-bubble'>
            <div style='color:#fbbf24; font-size:15px; font-weight:700; margin-bottom:6px;'>
                Kategori A: Düşük OSB, Yüksek PM2.5 İlleri ({len(kat_a_df)} İl)
            </div>
            <p style='color:#94a3b8; font-size:12px; margin-bottom:10px;'>
                OSB Sayısı ≤ {q1_osb:.0f} (Alt %25) ve PM2.5 ≥ {q3_pm_str} µg/m³ (Üst %25)
            </p>
            <div style='display:flex; flex-wrap:wrap; gap:6px;'>
                {chips_a_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_list_b:
        st.markdown(f"""
        <div class='info-bubble'>
            <div style='color:#f87171; font-size:15px; font-weight:700; margin-bottom:6px;'>
                Kategori B: Yüksek OSB, Yüksek PM2.5 İlleri ({len(kat_b_df)} İl)
            </div>
            <p style='color:#94a3b8; font-size:12px; margin-bottom:10px;'>
                OSB Sayısı ≥ {q3_osb:.0f} (Üst %25) ve PM2.5 ≥ {q3_pm_str} µg/m³ (Üst %25)
            </p>
            <div style='display:flex; flex-wrap:wrap; gap:6px;'>
                {chips_b_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background:rgba(2,18,32,0.6); border:1px solid #1e293b; border-left:3px solid #38bdf8; padding:10px 14px; border-radius:6px; margin-top:14px; font-size:12.5px; color:#94a3b8;'>
        <strong>Bilgi Notu:</strong> Listelenmeyen {len(df) - len(kat_a_df) - len(kat_b_df)} il, belirlenen uç çeyreklik eşiklerinin dışında kalarak orta segmentte yer alan 'Dengeli Profil' grubundadır. PM2.5 değerleri CAMS 2025 yıllık model ortalamasıdır; gruplama nedensellik göstermez.
    </div>
    """, unsafe_allow_html=True)
