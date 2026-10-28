"""
Şehir Karnesi Sayfası (City Report Card)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from visualization.components import render_metric_card
from data_sources.constants import pm25_kademe_etiketi


def to_tr_num(val: float, decimals: int = 1) -> str:
    """Sayıları matematiksel doğru yuvarlamayla (ROUND_HALF_UP) Türkçe formatlar."""
    if pd.isnull(val):
        return "—"
    dec_fmt = "1" if decimals == 0 else f"0.{'0'*(decimals-1)}1"
    dec = Decimal(f"{float(val):.4f}").quantize(Decimal(dec_fmt), rounding=ROUND_HALF_UP)
    if decimals == 0:
        return f"{int(dec):,}".replace(",", ".")
    sign = "-" if dec < 0 else ""
    parts = f"{abs(dec):.{decimals}f}".split(".")
    int_part = f"{int(parts[0]):,}".replace(",", ".")
    return f"{sign}{int_part},{parts[1]}"


def to_tr_sign(val: float, decimals: int = 1) -> str:
    sign = "+" if val > 0 else ""
    return f"{sign}{to_tr_num(val, decimals)}"


def get_disp_val(val: float, decimals: int = 1) -> float:
    """Ekranda gösterilen yuvarlanmış sayısal değeri (ROUND_HALF_UP) döndürür."""
    if pd.isnull(val):
        return 0.0
    dec_fmt = "1" if decimals == 0 else f"0.{'0'*(decimals-1)}1"
    dec = Decimal(f"{float(val):.4f}").quantize(Decimal(dec_fmt), rounding=ROUND_HALF_UP)
    return float(dec)


def get_dso_risk_tier(val: float) -> str:
    """Yıllık PM2.5 için platform kademesini döndürür (eşikler DSÖ 2021 yıllık ara hedefleri)."""
    return pm25_kademe_etiketi(val)


def generate_city_summary(df: pd.DataFrame, city_name: str) -> dict:
    """
    Seçilen il için yalnızca veriden hesaplanan nesnel f-string özet cümleleri ve künye verilerini üretir.
    Değer yargısı, nedensellik ve sübjektif ifadeler içermez.
    """
    il_row = df[df["il"] == city_name].iloc[0]
    bolge = il_row["bolge"]

    # 1. PM2.5 Sırası (1 = en düşük)
    pm_rank = int(df["pm25"].rank(ascending=True, method="min")[df["il"] == city_name].iloc[0])
    sentence_pm_rank = f"81 il içinde PM2,5'te {pm_rank}. sırada (1 = en düşük)."

    # 2. DSÖ Kıyası
    dso_kat = il_row["pm25"] / 5.0
    sentence_dso = f"PM2,5 değeri DSÖ yıllık kılavuzunun (5 µg/m³) {to_tr_num(dso_kat, 1)} katı."

    # 3. Ortalama Farkı (Ekranda görünen yuvarlanmış değerler üzerinden fark)
    tr_ort = float(df["pm25"].mean())
    bolge_ort = float(df[df["bolge"] == bolge]["pm25"].mean())
    il_pm_disp = get_disp_val(il_row["pm25"], 1)
    tr_pm_disp = get_disp_val(tr_ort, 1)
    bolge_pm_disp = get_disp_val(bolge_ort, 1)
    diff_tr = round(il_pm_disp - tr_pm_disp, 1)
    diff_bolge = round(il_pm_disp - bolge_pm_disp, 1)
    diff_tr_str = to_tr_sign(diff_tr, 1)
    diff_bolge_str = to_tr_sign(diff_bolge, 1)
    sentence_ort_fark = (
        f"Türkiye düz il ortalamasına ({to_tr_num(tr_ort, 1)} µg/m³) göre {diff_tr_str} µg/m³, "
        f"{bolge} Bölgesi ortalamasına ({to_tr_num(bolge_ort, 1)} µg/m³) göre {diff_bolge_str} µg/m³ fark göstermektedir."
    )

    # 4. OSB Yoğunluğu & Uç Durum
    q1_osb = float(df["toplam_osb"].quantile(0.25))
    q3_osb = float(df["toplam_osb"].quantile(0.75))
    q1_pm = float(df["pm25"].quantile(0.25))
    q3_pm = float(df["pm25"].quantile(0.75))

    osb_val = float(il_row["toplam_osb"])
    pm_val = float(il_row["pm25"])

    if osb_val <= q1_osb:
        osb_group = "düşük grup"
    elif osb_val >= q3_osb:
        osb_group = "yüksek grup"
    else:
        osb_group = "orta grup"

    if pm_val <= q1_pm:
        pm_group = "düşük grup"
    elif pm_val >= q3_pm:
        pm_group = "yüksek grup"
    else:
        pm_group = "orta grup"

    if osb_group == "düşük grup" and pm_group == "yüksek grup":
        sentence_osb = "OSB sayısı düşük gruptayken PM2,5 yüksek gruptadır."
    elif osb_group == "yüksek grup" and pm_group == "düşük grup":
        sentence_osb = "OSB sayısı yüksek gruptayken PM2,5 düşük gruptadır."
    else:
        sentence_osb = f"OSB sayısı {osb_group}ta, PM2,5 değeri {pm_group}tadır."

    # 5. Solunum Ölüm Hızı Sırası ve Nüfus Sırası
    sol_rank = int(df["solunum_olum_100k"].rank(ascending=True, method="min")[df["il"] == city_name].iloc[0])
    nufus_rank = int(df["nufus"].rank(ascending=False, method="min")[df["il"] == city_name].iloc[0])

    sentence_sol_rank = f"81 il içinde solunum hastalıkları kaba ölüm hızında {sol_rank}. sırada (1 = en düşük, kaba hız)."
    sentence_nufus_rank = f"81 il içinde nüfus büyüklüğünde {nufus_rank}. sırada (1 = en yüksek)."

    sentences = [
        sentence_pm_rank,
        sentence_dso,
        sentence_ort_fark,
        sentence_osb,
        sentence_sol_rank,
        sentence_nufus_rank
    ]

    kunye = {
        "nufus": int(il_row["nufus"]),
        "bolge": bolge,
        "plaka": int(il_row["plaka"]),
        "toplam_osb": int(il_row["toplam_osb"]),
        "faal_osb": int(il_row.get("faal_osb", 0))
    }

    return {
        "sentences": sentences,
        "kunye": kunye,
        "footnote": "Not: PM2.5 verileri Copernicus CAMS atmosferik model reanalizine dayanmaktadır; kaba ölüm hızı yaş standardizasyonu içermez."
    }

def render_report_card_page(df: pd.DataFrame, ts_df: Optional[pd.DataFrame] = None):
    """
    Her il için ayrıntılı hava kalitesi, sanayi ve sağlık karnesini görüntüler.
    """
    st.markdown("### Şehir Karnesi & İl Çevre Profili")
    st.markdown(
        "<p style='color:#94a3b8;'>Türkiye'nin 81 ilinin hava kalitesi, sanayi baskısı ve solunum sağlığı profili karnesi.</p>",
        unsafe_allow_html=True
    )
    
    # Dinamik Şehir Seçici ve State/URL Senkronizasyonu
    iller = sorted(df["il"].unique().tolist())
    if "city" in st.query_params:
        del st.query_params["city"]
    q_il = st.query_params.get("il")

    if q_il and q_il in iller:
        active_city = q_il
    elif st.session_state.get("selected_city") in iller:
        active_city = st.session_state["selected_city"]
    elif "İstanbul" in iller:
        active_city = "İstanbul"
    else:
        active_city = iller[0] if iller else ""

    st.session_state["selected_city"] = active_city
    st.query_params["il"] = active_city

    if st.session_state.get("_report_card_city_select") != active_city:
        st.session_state["_report_card_city_select"] = active_city

    col_sel1, col_sel2 = st.columns([2, 1])
    with col_sel1:
        def on_city_change():
            chosen = st.session_state.get("_report_card_city_select")
            if chosen and chosen in iller:
                st.session_state["selected_city"] = chosen
                st.query_params["il"] = chosen

        secilen_il = st.selectbox(
            "İl Seçimi:",
            iller,
            key="_report_card_city_select",
            on_change=on_city_change,
            help="Detaylı karnesini görüntülemek istediğiniz ili seçiniz."
        )
        if secilen_il and secilen_il != st.session_state.get("selected_city"):
            st.session_state["selected_city"] = secilen_il
            st.query_params["il"] = secilen_il
        
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
    
    # 1. TEMEL GÖSTERGELER (3 Kart)
    c1, c2, c3 = st.columns(3)
    with c1:
        il_pm_disp = get_disp_val(il_row["pm25"], 1)
        bolge_pm_disp = get_disp_val(bolge_ort_pm25, 1)
        delta_bolge = round(il_pm_disp - bolge_pm_disp, 1)
        render_metric_card(
            title="PM2.5 Yıllık Ort. (CAMS 2025 model)",
            value=to_tr_num(il_row["pm25"], 1),
            unit=" µg/m³",
            delta=f"{to_tr_sign(delta_bolge, 1)} µg/m³ (Bölge Ort.)",
            delta_type="positive" if delta_bolge > 0 else "negative"
        )
    with c2:
        dso_risk_tier = get_dso_risk_tier(float(il_row["pm25"]))
        render_metric_card(
            title="Kirlilik Kademesi",
            value=dso_risk_tier,
            unit="",
            delta=f"DSÖ Kılavuzunun (5 µg/m³) {to_tr_num(il_row['dso_limit_kat'], 1)} Katı",
            delta_type="positive" if il_row["pm25"] > 10 else "neutral"
        )
    with c3:
        render_metric_card(
            title="Solunum Ölüm Oranı",
            value=to_tr_num(il_row["solunum_olum_100k"], 1),
            unit=" (Yüz Binde)",
            delta="TÜİK 2024 · Kaba hız, yaşa göre düzeltilmemiş",
            delta_type="neutral"
        )

    # Ek göstergeler: yaş yapısını kısmen dengeleyen pay, AirQ+ atfedilebilir ölüm ve istasyon karşılaştırması
    ek_parcalar = []
    if pd.notna(il_row.get("solunum_olum_payi")):
        ek_parcalar.append(
            f"Solunum ölümlerinin tüm ölümler içindeki payı: <strong>%{to_tr_num(il_row['solunum_olum_payi'], 1)}</strong>"
        )
    if pd.notna(il_row.get("atfedilen_olum_tahmini")):
        atf_sayi = f"{int(il_row['atfedilen_olum_tahmini']):,}".replace(",", ".")
        ek_parcalar.append(
            f"PM2.5'e atfedilebilir ölüm (AirQ+ yaklaşık tahmin): <strong>~{atf_sayi}</strong> "
            f"(tüm ölümler içindeki pay: %{to_tr_num(il_row['atfedilen_olum_payi'], 1)})"
        )
    if pd.notna(il_row.get("pm25_istasyon_max_2024")):
        ek_parcalar.append(
            f"Kara Rapor 2025 en yüksek istasyon (2024): <strong>{to_tr_num(il_row['pm25_istasyon_max_2024'], 1)} µg/m³</strong> "
            f"— CAMS modeli bu ilde istasyon ölçümünün altında kalıyor"
        )
    if ek_parcalar:
        st.markdown(
            "<div style='margin-top:10px; padding:10px 14px; background:#031b2e; border:1px solid #093452; "
            "border-radius:8px; font-size:12.5px; color:#cbd5e1; line-height:1.7;'>"
            + " &bull; ".join(ek_parcalar)
            + "</div>",
            unsafe_allow_html=True,
        )

    st.write("")
    
    # 2. ORTA BÖLÜM: BÖLGESEL VE TÜRKİYE KARŞILAŞTIRMASI & İL KÜNYESİ
    col_chart, col_details = st.columns([1.3, 1.0])
    
    with col_chart:
        st.markdown("#### Bölge ve Türkiye Ortalamasının Karşılaştırması")
        comp_df = pd.DataFrame({
            "Kategori": [f"{secilen_il}", f"{bolge} Bölgesi", "Türkiye Geneli (Düz İl Ortalaması)"],
            "PM2.5 (µg/m³)": [il_row["pm25"], bolge_ort_pm25, turkiye_ort_pm25],
            "PM2.5_Metin": [
                f"{to_tr_num(il_row['pm25'], 1)} µg/m³",
                f"{to_tr_num(bolge_ort_pm25, 1)} µg/m³",
                f"{to_tr_num(turkiye_ort_pm25, 1)} µg/m³"
            ]
        })
        fig_comp = px.bar(
            comp_df,
            x="Kategori",
            y="PM2.5 (µg/m³)",
            color="Kategori",
            color_discrete_map={
                f"{secilen_il}": "#38bdf8",
                f"{bolge} Bölgesi": "#818cf8",
                "Türkiye Geneli (Düz İl Ortalaması)": "#64748b"
            },
            text="PM2.5_Metin"
        )
        fig_comp.update_traces(textposition="outside")
        fig_comp.add_hline(y=5.0, line_dash="dash", line_color="#ef4444", annotation_text="DSÖ Yıllık Limit (5 µg/m³)")
        fig_comp.update_layout(
            height=280,
            showlegend=False,
            xaxis_title=None,
            margin=dict(t=20, l=10, r=10, b=10)
        )
        st.plotly_chart(fig_comp, use_container_width=True)
        
    with col_details:
        st.markdown("#### İl Künyesi")
        toplam_osb_val = int(il_row["toplam_osb"])
        faal_osb_val = int(il_row.get("faal_osb", 0))
        if toplam_osb_val > 0:
            faal_pct = (faal_osb_val / toplam_osb_val) * 100.0
            faal_pct_str = to_tr_num(faal_pct, 1)
        else:
            faal_pct_str = "0,0"
        faal_osb_display = f"{faal_osb_val} Adet (%{faal_pct_str})"

        st.markdown(f"""
        <div style='background:#0d1527; border:1px solid #1e293b; border-radius:12px; padding:18px;'>
            <table style='width:100%; border-collapse:collapse; font-size:13px; color:#cbd5e1;'>
                <tr style='border-bottom:1px solid #1e293b; height:36px;'>
                    <td><b>Resmi Nüfus (ADNKS):</b></td>
                    <td style='text-align:right; color:#f8fafc; font-weight:700;'>{to_tr_num(il_row['nufus'], 0)} Kişi</td>
                </tr>
                <tr style='border-bottom:1px solid #1e293b; height:36px;'>
                    <td><b>Coğrafi Bölge:</b></td>
                    <td style='text-align:right; color:#38bdf8; font-weight:700;'>{bolge}</td>
                </tr>
                <tr style='border-bottom:1px solid #1e293b; height:36px;'>
                    <td><b>Plaka Kodu:</b></td>
                    <td style='text-align:right; color:#f8fafc; font-weight:700;'>{int(il_row['plaka']):02d}</td>
                </tr>
                <tr style='border-bottom:1px solid #1e293b; height:36px;'>
                    <td><b>Toplam OSB:</b></td>
                    <td style='text-align:right; color:#f8fafc; font-weight:700;'>{toplam_osb_val} Adet</td>
                </tr>
                <tr style='height:36px;'>
                    <td><b>Faal OSB:</b></td>
                    <td style='text-align:right; color:#f8fafc; font-weight:700;'>{faal_osb_display}</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    
    # 3. İL ÖZETİ (HESAPLANAN VERİ CÜMLELERİ)
    st.markdown(f"#### {secilen_il} İl Özeti")
    summary = generate_city_summary(df, secilen_il)
    
    bullets_html = "".join([
        f"<li style='margin-bottom:8px; line-height:1.6;'>{s}</li>"
        for s in summary["sentences"]
    ])
    
    st.markdown(f"""
    <div style='background:#0d1527; border:1px solid #1e293b; border-radius:12px; padding:20px; margin-bottom:16px;'>
        <ul style='color:#e2e8f0; font-size:13.5px; padding-left:20px; margin:0;'>
            {bullets_html}
        </ul>
        <div style='font-size:11.5px; color:#64748b; margin-top:14px; border-top:1px solid #1e293b; padding-top:10px;'>
            {summary["footnote"]}
        </div>
    </div>
    """, unsafe_allow_html=True)
