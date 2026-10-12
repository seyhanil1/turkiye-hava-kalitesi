"""
Şehir Düellosu Sayfası (City Duel)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from visualization.components import render_metric_card
from visualization.distribution_charts import (
    create_duel_radar_chart,
    create_duel_dumbbell_chart,
    create_single_metric_comparison_bar
)


from decimal import Decimal, ROUND_HALF_UP

def to_tr_num(val: float, decimals: int = 1) -> str:
    """Sayıları matematiksel doğru yuvarlamayla (ROUND_HALF_UP) Türkçe formatlar."""
    if pd.isnull(val):
        return "—"
    dec_fmt = "1" if decimals == 0 else f"0.{'0'*(decimals-1)}1"
    dec = Decimal(f"{float(val):.4f}").quantize(Decimal(dec_fmt), rounding=ROUND_HALF_UP)
    if decimals == 0:
        return f"{int(dec):,}".replace(",", ".")
    parts = f"{dec:.{decimals}f}".split(".")
    int_part = f"{int(parts[0]):,}".replace(",", ".")
    return f"{int_part},{parts[1]}"


def render_duel_page(df: pd.DataFrame):
    """
    İki ili nesnel kamu ve model verileriyle kafa kafaya karşılaştıran analitik profil sayfası.
    """
    st.markdown("### İki İl Kafa Kafaya Karşılaştırma & Gösterge Profili")
    st.markdown(
        "<p style='color:#94a3b8; font-size:13px;'>Resmi kamu ve model verileriyle iki ilin çevre, solunum sağlığı ve sanayi altyapısı göstergelerini nesnel olarak karşılaştırın.</p>",
        unsafe_allow_html=True
    )

    iller = sorted(df["il"].unique().tolist())

    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        default_a = iller.index("İstanbul") if "İstanbul" in iller else 0
        il_a_name = st.selectbox("1. İl (Mavi Profil):", iller, index=default_a)
    with col_sel2:
        default_b = iller.index("Ankara") if "Ankara" in iller else 1
        il_b_name = st.selectbox("2. İl (Yeşil Profil):", iller, index=default_b)

    # H. Aynı il seçilirse uyarı
    if il_a_name == il_b_name:
        st.warning("⚠️ Lütfen karşılaştırma için iki farklı il seçiniz.")
        return

    city_a = df[df["il"] == il_a_name].iloc[0]
    city_b = df[df["il"] == il_b_name].iloc[0]

    # A. ÜSTTE İKİ ŞEHİR KARTI (Şehir A mavi, Şehir B yeşil, mobilde responsive alt alta)
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        nufus_a_str = to_tr_num(city_a['nufus'], 0)
        st.markdown(f"""
        <div style="background:linear-gradient(180deg, #0e1e38 0%, #081122 100%); border:1px solid #38bdf8; border-radius:12px; padding:16px 20px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="font-size:20px; font-weight:800; color:#38bdf8;">{city_a['il']}</div>
                <div style="background:rgba(56, 189, 248, 0.15); border:1px solid #38bdf8; color:#38bdf8; padding:2px 10px; border-radius:20px; font-size:12px; font-weight:700;">Plaka {int(city_a['plaka']):02d}</div>
            </div>
            <div style="display:flex; flex-wrap:wrap; gap:16px; margin-top:8px; font-size:13px; color:#cbd5e1;">
                <div>Bölge: <strong style="color:#f8fafc;">{city_a['bolge']}</strong></div>
                <div>•</div>
                <div>Nüfus: <strong style="color:#f8fafc;">{nufus_a_str}</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_c2:
        nufus_b_str = to_tr_num(city_b['nufus'], 0)
        st.markdown(f"""
        <div style="background:linear-gradient(180deg, #0d2822 0%, #061713 100%); border:1px solid #10b981; border-radius:12px; padding:16px 20px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="font-size:20px; font-weight:800; color:#10b981;">{city_b['il']}</div>
                <div style="background:rgba(16, 185, 129, 0.15); border:1px solid #10b981; color:#10b981; padding:2px 10px; border-radius:20px; font-size:12px; font-weight:700;">Plaka {int(city_b['plaka']):02d}</div>
            </div>
            <div style="display:flex; flex-wrap:wrap; gap:16px; margin-top:8px; font-size:13px; color:#cbd5e1;">
                <div>Bölge: <strong style="color:#f8fafc;">{city_b['bolge']}</strong></div>
                <div>•</div>
                <div>Nüfus: <strong style="color:#f8fafc;">{nufus_b_str}</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # B. KARŞILAŞTIRMA TABLOSU METRİKLERİ VE HESAPLAMALARI
    # Metrik 1: PM2.5
    pm_a = float(city_a["pm25"])
    pm_b = float(city_b["pm25"])
    pm_a_str = to_tr_num(pm_a, 1)
    pm_b_str = to_tr_num(pm_b, 1)
    dso_kat_a_str = to_tr_num(pm_a / 5.0, 1)
    dso_kat_b_str = to_tr_num(pm_b / 5.0, 1)

    # Metrik 2: TÜİK Solunum Ölüm Hızı
    sol_a = float(city_a["solunum_olum_100k"])
    sol_b = float(city_b["solunum_olum_100k"])
    sol_a_str = to_tr_num(sol_a, 1)
    sol_b_str = to_tr_num(sol_b, 1)

    # Metrik 3: Toplam OSB Sayısı
    osb_a = int(round(city_a.get("toplam_osb", 0)))
    osb_b = int(round(city_b.get("toplam_osb", 0)))

    # Metrik 4: Milyon Kişi Başına OSB
    osb_per_m_a = osb_a / (float(city_a["nufus"]) / 1_000_000.0)
    osb_per_m_b = osb_b / (float(city_b["nufus"]) / 1_000_000.0)
    osb_m_a_str = to_tr_num(osb_per_m_a, 1)
    osb_m_b_str = to_tr_num(osb_per_m_b, 1)

    # Metrik 5: Toplam OSB Alanı (Hektar)
    ha_a = float(city_a.get("osb_alani_hektar", 0.0))
    ha_b = float(city_b.get("osb_alani_hektar", 0.0))
    ha_a_str = to_tr_num(ha_a, 1)
    ha_b_str = to_tr_num(ha_b, 1)

    # Yardımcı Fark Çipi Fonksiyonu (kazandı/kaybetti ifadesi ASLA kullanılmaz)
    def format_diff_chip(val_1: float, val_2: float, unit_s: str, name_1: str, name_2: str) -> str:
        diff_val = val_1 - val_2
        denom_val = max(val_1, val_2)
        pct_rel = (abs(diff_val) / denom_val * 100.0) if denom_val > 0 else 0.0

        if pct_rel < 5.0:
            pct_s = to_tr_num(pct_rel, 1)
            return f"<span style='background:#1e293b; color:#94a3b8; padding:3px 8px; border-radius:6px; font-size:12px; font-weight:600;'>≈ Benzer (%{pct_s})</span>"

        diff_abs_s = to_tr_num(abs(diff_val), 1)
        pct_s = to_tr_num(pct_rel, 1)
        if diff_val > 0:
            return f"<span style='background:rgba(56, 189, 248, 0.12); color:#38bdf8; border:1px solid rgba(56, 189, 248, 0.3); padding:3px 8px; border-radius:6px; font-size:12px; font-weight:600;'>▲ {name_1} +{diff_abs_s} {unit_s} (+%{pct_s})</span>"
        else:
            return f"<span style='background:rgba(16, 185, 129, 0.12); color:#10b981; border:1px solid rgba(16, 185, 129, 0.3); padding:3px 8px; border-radius:6px; font-size:12px; font-weight:600;'>▲ {name_2} +{diff_abs_s} {unit_s} (+%{pct_s})</span>"

    chip_pm = format_diff_chip(pm_a, pm_b, "µg/m³", il_a_name, il_b_name)
    chip_sol = format_diff_chip(sol_a, sol_b, "/ 100k", il_a_name, il_b_name)
    chip_osb = format_diff_chip(float(osb_a), float(osb_b), "OSB", il_a_name, il_b_name)
    chip_osb_m = format_diff_chip(osb_per_m_a, osb_per_m_b, "OSB/M", il_a_name, il_b_name)
    chip_ha = format_diff_chip(ha_a, ha_b, "ha", il_a_name, il_b_name)

    # HTML Tablosu (Glassmorphic lüks koyu tasarım)
    st.markdown("#### Kafa Kafaya Gösterge Karşılaştırma Tablosu")
    st.markdown(f"""
    <div style="overflow-x:auto; background:#0b1326; border:1px solid #1e293b; border-radius:12px; margin-bottom:16px;">
        <table style="width:100%; border-collapse:collapse; text-align:left; font-size:13px; color:#e2e8f0;">
            <thead>
                <tr style="border-bottom:1px solid #1e293b; background:#0f1a33; color:#94a3b8;">
                    <th style="padding:12px 16px;">Gösterge</th>
                    <th style="padding:12px 16px; color:#38bdf8;">{il_a_name}</th>
                    <th style="padding:12px 16px; color:#10b981;">{il_b_name}</th>
                    <th style="padding:12px 16px;">Mutlak ve Göreli Fark</th>
                    <th style="padding:12px 16px;">DSÖ Kılavuz Katı</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
                    <td style="padding:12px 16px; font-weight:600;">PM2.5 Kirliliği (µg/m³)</td>
                    <td style="padding:12px 16px; font-weight:700; color:#38bdf8;">{pm_a_str} µg/m³</td>
                    <td style="padding:12px 16px; font-weight:700; color:#10b981;">{pm_b_str} µg/m³</td>
                    <td style="padding:12px 16px;">{chip_pm}</td>
                    <td style="padding:12px 16px; color:#cbd5e1;">{dso_kat_a_str}x vs {dso_kat_b_str}x</td>
                </tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
                    <td style="padding:12px 16px; font-weight:600;">TÜİK Solunum Ölüm Hızı (100k)</td>
                    <td style="padding:12px 16px; font-weight:700; color:#38bdf8;">{sol_a_str} / 100k</td>
                    <td style="padding:12px 16px; font-weight:700; color:#10b981;">{sol_b_str} / 100k</td>
                    <td style="padding:12px 16px;">{chip_sol}</td>
                    <td style="padding:12px 16px; color:#64748b;">—</td>
                </tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
                    <td style="padding:12px 16px; font-weight:600;">Toplam OSB Sayısı</td>
                    <td style="padding:12px 16px; font-weight:700; color:#38bdf8;">{osb_a} Adet</td>
                    <td style="padding:12px 16px; font-weight:700; color:#10b981;">{osb_b} Adet</td>
                    <td style="padding:12px 16px;">{chip_osb}</td>
                    <td style="padding:12px 16px; color:#64748b;">—</td>
                </tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
                    <td style="padding:12px 16px; font-weight:600;">Milyon Kişi Başına OSB</td>
                    <td style="padding:12px 16px; font-weight:700; color:#38bdf8;">{osb_m_a_str} Adet/Milyon</td>
                    <td style="padding:12px 16px; font-weight:700; color:#10b981;">{osb_m_b_str} Adet/Milyon</td>
                    <td style="padding:12px 16px;">{chip_osb_m}</td>
                    <td style="padding:12px 16px; color:#64748b;">—</td>
                </tr>
                <tr>
                    <td style="padding:12px 16px; font-weight:600;">Toplam OSB Alanı (Hektar)</td>
                    <td style="padding:12px 16px; font-weight:700; color:#38bdf8;">{ha_a_str} ha</td>
                    <td style="padding:12px 16px; font-weight:700; color:#10b981;">{ha_b_str} ha</td>
                    <td style="padding:12px 16px;">{chip_ha}</td>
                    <td style="padding:12px 16px; color:#64748b;">—</td>
                </tr>
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

    # E. VERİDEN ÜRETİLEN NÖTR ÖZET CÜMLE (Nedensellik ve yorum içermez)
    diff_pm = pm_a - pm_b
    pm_dir = "daha düşük" if diff_pm < 0 else ("daha yüksek" if diff_pm > 0 else "eşit")
    pm_abs_str = to_tr_num(abs(diff_pm), 1)
    denom_pm = max(pm_a, pm_b)
    pm_rel = (abs(diff_pm) / denom_pm * 100.0) if denom_pm > 0 else 0.0
    pm_rel_note = "benzer düzeyde" if pm_rel < 5.0 else f"%{to_tr_num(pm_rel, 1)} farkla"

    diff_sol = sol_a - sol_b
    sol_dir = "daha düşük" if diff_sol < 0 else ("daha yüksek" if diff_sol > 0 else "eşit")
    sol_abs_str = to_tr_num(abs(diff_sol), 1)

    st.markdown(f"""
    <div style="background:#091220; border-left:4px solid #38bdf8; border-radius:6px; padding:12px 16px; margin-bottom:20px; font-size:13px; color:#cbd5e1; line-height:1.6;">
        <strong>İstatistiksel Özet:</strong> {il_a_name} ilinde yıllık ortalama PM2.5 konsantrasyonu {il_b_name} iline göre <strong>{pm_abs_str} µg/m³ {pm_dir}</strong> seviyededir ({pm_rel_note}). TÜİK solunum yolu ölüm hızında ise {il_a_name}, {il_b_name} iline kıyasla <strong>{sol_abs_str} / 100k {sol_dir}</strong> düzeyde ölçülmektedir.
    </div>
    """, unsafe_allow_html=True)

    # C. DUMBBELL GRAFİĞİ (Radar Yerine 81 İl Yüzdelik Konumu / Percentile Rank)
    fig_dumbbell = create_duel_dumbbell_chart(df, city_a, city_b)
    st.plotly_chart(fig_dumbbell, use_container_width=True, config={"displayModeBar": False})

    st.write("")

    # D. HER BİRİM İÇİN AYRI KÜÇÜK ÇUBUK GRAFİK (Small Multiples)
    st.markdown("#### Temel Göstergeler Karşılaştırma Panelleri")
    col_b1, col_b2, col_b3 = st.columns(3)

    with col_b1:
        fig_pm = create_single_metric_comparison_bar(
            metric_title="PM2.5 Kirliliği",
            unit_label="µg/m³",
            val_a=pm_a,
            val_b=pm_b,
            name_a=il_a_name,
            name_b=il_b_name,
            text_a=f"{pm_a_str} µg/m³",
            text_b=f"{pm_b_str} µg/m³"
        )
        st.plotly_chart(fig_pm, use_container_width=True, config={"displayModeBar": False})

    with col_b2:
        fig_sol = create_single_metric_comparison_bar(
            metric_title="TÜİK Solunum Ölüm Hızı",
            unit_label="/ 100k",
            val_a=sol_a,
            val_b=sol_b,
            name_a=il_a_name,
            name_b=il_b_name,
            text_a=f"{sol_a_str} / 100k",
            text_b=f"{sol_b_str} / 100k"
        )
        st.plotly_chart(fig_sol, use_container_width=True, config={"displayModeBar": False})

    with col_b3:
        fig_osb = create_single_metric_comparison_bar(
            metric_title="Toplam OSB Sayısı",
            unit_label="Adet",
            val_a=float(osb_a),
            val_b=float(osb_b),
            name_a=il_a_name,
            name_b=il_b_name,
            text_a=f"{osb_a} Adet",
            text_b=f"{osb_b} Adet"
        )
        st.plotly_chart(fig_osb, use_container_width=True, config={"displayModeBar": False})

    # F. METODOLOJİK DİPNOTLAR
    st.markdown("""
    <div style="background:#091220; border:1px solid #1e293b; border-radius:10px; padding:14px 18px; margin-top:16px; font-size:12px; color:#94a3b8; line-height:1.6;">
        <div style="font-weight:700; color:#cbd5e1; margin-bottom:4px;">📌 Metodolojik Notlar ve Kaynakça:</div>
        • <strong>PM2.5 Kirlilik Verisi:</strong> Copernicus Atmosfer İzleme Servisi (CAMS) atmosferik modelleme ve uydu konsolidasyonudur (tekil zemin istasyonu anlık ölçümü değildir).<br>
        • <strong>Solunum Ölüm Hızı:</strong> TÜİK resmi ölüm nedeni istatistikleri ve ADNKS nüfus verileri üzerinden hesaplanan kaba ölüm hızıdır (Crude Death Rate, 100.000 kişide); yaş ve cinsiyete göre standardize edilmemiştir.<br>
        • <strong>Organize Sanayi Bölgesi (OSB):</strong> Organize Sanayi Bölgeleri Üst Kuruluşu (OSBÜK) resmi kayıtlarından derlenmiştir.<br>
        • <strong>Yorumlama Sınırı:</strong> İl düzeyindeki makro istatistiki agregasyonlar genel durum karşılaştırması içindir; bireysel sağlık riskleri veya tekil endüstriyel tesisler için doğrudan nedensellik çıkarımı yapılamaz.
    </div>
    """, unsafe_allow_html=True)
