"""
🤖 Yapay Zeka İçgörü & Tahmin Motoru
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

4 Aşamalı Dinamik Yapı:
1. Dinamik Anomali ve Neden-Sonuç Algoritması (Pandas quantile):
   - Kategori A (Coğrafi Kapan / Sessiz Tehlike): OSB sayısı alt %25, PM2.5 üst %25
   - Kategori B (Ağır Sanayi Baskısı): OSB sayısı üst %25, PM2.5 üst %25
   - Normal: Diğer dengeli iller
2. Dinamik İl Seçici ve 5 Yıllık Trend Projeksiyonu (2026-2031):
   - st.selectbox ile il seçimi
   - Kategori A: yıllık %3 artış
   - Kategori B: yıllık %5 artış
   - Normal: yıllık %1 artış
   - Plotly go.Scatter koyu temalı, ucu kesik çizgili (dashed) grafik
3. Dinamik Uyarılar ve Alınacak Önlemler (CSS pulsing glow):
   - Kategoriye özel Neden-Sonuç analizi ve Acil Eylem Planı reçetesi
4. Şık UI/UX Entegrasyonu:
   - background-color: #1e293b, border: 1px solid #334155
   - Hover efekti ile hafif zıplayan (translateY) bilgi balonları (info-bubble)
   - Neon mavi (#38bdf8) ve neon kırmızı (#ef4444) başlıklar
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any, Tuple, List


def calculate_quantiles_and_anomalies(df: pd.DataFrame) -> Tuple[float, float, float, float, pd.DataFrame, pd.DataFrame]:
    """
    Pandas ile 81 ilin pm25 ve osb_sayisi çeyrekliklerini (quantile) hesaplar,
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


def determine_city_category(
    row: pd.Series, 
    q1_osb: float, 
    q3_osb: float, 
    q1_pm25: float, 
    q3_pm25: float
) -> Tuple[str, float]:
    """
    Seçilen ilin hangi kategoriye (A, B veya Normal) girdiğini if-else ile tespit eder
    ve 5 yıllık projeksiyon için yıllık artış oranını döndürür.
    """
    osb = float(row["osb_sayisi"])
    pm25 = float(row["pm25"])

    if osb <= q1_osb and pm25 >= q3_pm25:
        # Kategori A (Coğrafi Kapan / Sessiz Tehlike): %3 yıllık artış
        return "Kategori A", 0.03
    elif osb >= q3_osb and pm25 >= q3_pm25:
        # Kategori B (Ağır Sanayi Baskısı): %5 yıllık artış
        return "Kategori B", 0.05
    else:
        # Normal / Dengeli: %1 yıllık artış
        return "Normal", 0.01


def build_projection_series(base_pm25: float, annual_growth_rate: float) -> Tuple[List[int], List[float]]:
    """
    2026-2031 (5 yıllık) projeksiyon değerlerini hesaplar.
    """
    years = [2026, 2027, 2028, 2029, 2030, 2031]
    values = []
    for i in range(len(years)):
        val = base_pm25 * ((1.0 + annual_growth_rate) ** i)
        values.append(round(val, 2))
    return years, values


def create_forecast_figure(
    city_name: str, 
    category: str, 
    years: List[int], 
    values: List[float], 
    growth_rate: float
) -> go.Figure:
    """
    Plotly go.Scatter ile koyu temalı, ucu kesik çizgili (dashed) şık 5 yıllık projeksiyon grafiği üretir.
    """
    if category == "Kategori A":
        theme_color = "#f59e0b"   # Amber / Uyarı
        badge_text = "Kategori A (Coğrafi Kapan — Yıllık +%3)"
    elif category == "Kategori B":
        theme_color = "#ef4444"   # Kırmızı / Kritik Sanayi
        badge_text = "Kategori B (Ağır Sanayi Baskısı — Yıllık +%5)"
    else:
        theme_color = "#00e5db"   # Neon Turkuaz / Normal
        badge_text = "Normal Profil (Dengeli — Yıllık +%1)"

    fig = go.Figure()

    # DSÖ 2021 Kılavuz Değeri (5 µg/m³)
    fig.add_hline(
        y=5.0,
        line_dash="dot",
        line_color="#10b981",
        line_width=1.5,
        annotation_text="DSÖ Yıllık Kılavuz Eşiği (5 µg/m³)",
        annotation_position="bottom right",
        annotation_font=dict(color="#10b981", size=11)
    )

    # DSÖ IT-1 Geçiş Hedefi (35 µg/m³)
    fig.add_hline(
        y=35.0,
        line_dash="dot",
        line_color="#f59e0b",
        line_width=1.5,
        annotation_text="DSÖ IT-1 Geçiş Eşiği (35 µg/m³)",
        annotation_position="top right",
        annotation_font=dict(color="#f59e0b", size=11)
    )

    # 5 Yıllık Trend Projeksiyonu Çizgisi (Dashed / Ucu Kesik Çizgili)
    fig.add_trace(go.Scatter(
        x=years,
        y=values,
        mode="lines+markers+text",
        name="5 Yıllık Trend Projeksiyonu",
        line=dict(
            color=theme_color,
            width=3.5,
            dash="dash"  # Kullanıcının talep ettiği kesik çizgi
        ),
        marker=dict(
            size=11,
            color="#ffffff",
            line=dict(color=theme_color, width=3.5)
        ),
        text=[f"{v:.1f}" for v in values],
        textposition="top center",
        textfont=dict(color="#f8fafc", size=12, family="Inter, Segoe UI, sans-serif"),
        hovertemplate=(
            "<b>Yıl:</b> %{x}<br>"
            "<b>Tahmini PM2.5:</b> %{y:.2f} µg/m³<br>"
            f"<b>Model:</b> {badge_text}<extra></extra>"
        )
    ))

    # Koyu Tema ve Glassmorphic Düzen
    fig.update_layout(
        title=dict(
            text=f"<b>{city_name}</b> — 5 Yıllık Trend Projeksiyonu (2026–2031) <span style='font-size:13px; color:{theme_color};'>[{badge_text}]</span>",
            font=dict(color="#f8fafc", size=16, family="Inter, Segoe UI, sans-serif")
        ),
        paper_bgcolor="#0b1324",
        plot_bgcolor="#070d17",
        xaxis=dict(
            title=dict(text="Projeksiyon Yılı", font=dict(color="#94a3b8", size=12)),
            tickmode="array",
            tickvals=years,
            ticktext=[str(y) for y in years],
            gridcolor="#1e293b",
            gridwidth=1,
            tickfont=dict(color="#cbd5e1", size=12),
            zeroline=False
        ),
        yaxis=dict(
            title=dict(text="PM2.5 Konsantrasyonu (µg/m³)", font=dict(color="#94a3b8", size=12)),
            gridcolor="#1e293b",
            gridwidth=1,
            tickfont=dict(color="#cbd5e1", size=12),
            zeroline=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#94a3b8", size=11)
        ),
        hoverlabel=dict(
            bgcolor="#0f172a",
            bordercolor=theme_color,
            font=dict(color="#f8fafc", family="Inter, sans-serif")
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        height=420
    )

    return fig


def render_ai_forecast_page(df: pd.DataFrame):
    """
    Yapay Zeka İçgörü & Tahmin Motoru sayfasını oluşturur.
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
        <div style='display:flex; align-items:center; gap:12px;'>
            <span style='font-size:32px;'>🤖</span>
            <div>
                <h2 style='color:#f8fafc; margin:0; font-size:24px; font-weight:700;'>
                    Yapay Zeka İçgörü & Tahmin Motoru
                </h2>
                <p style='color:#94a3b8; margin:4px 0 0 0; font-size:14px;'>
                    81 İl İçin Dinamik Çeyreklik (Quantile) Anomali Analizi, Kategori Sınıflandırması ve 5 Yıllık Trend Projeksiyonu (2026–2031)
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 1. AŞAMA: PANDAS İLE DİNAMİK ANOMALİ VE NEDEN-SONUÇ ALGORİTMASI
    q1_osb, q3_osb, q1_pm25, q3_pm25, kat_a_df, kat_b_df = calculate_quantiles_and_anomalies(df)

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
                Q1: {q1_pm25:.1f} | Q3: {q3_pm25:.1f}
            </div>
            <div style='color:#64748b; font-size:11px; margin-top:2px;'>Üst dilim eşiği ≥ {q3_pm25:.1f} µg/m³</div>
        </div>
        """, unsafe_allow_html=True)

    with col_q3:
        st.markdown(f"""
        <div class='info-bubble' style='padding:14px 18px;'>
            <div style='color:#94a3b8; font-size:12px;'>Kategori A (Coğrafi Kapan)</div>
            <div style='color:#f59e0b; font-size:18px; font-weight:700; margin-top:4px;'>
                {len(kat_a_df)} İl Tespit Edildi
            </div>
            <div style='color:#64748b; font-size:11px; margin-top:2px;'>Düşük OSB, Yüksek Kirlilik</div>
        </div>
        """, unsafe_allow_html=True)

    with col_q4:
        st.markdown(f"""
        <div class='info-bubble' style='padding:14px 18px;'>
            <div style='color:#94a3b8; font-size:12px;'>Kategori B (Ağır Sanayi)</div>
            <div style='color:#ef4444; font-size:18px; font-weight:700; margin-top:4px;'>
                {len(kat_b_df)} İl Tespit Edildi
            </div>
            <div style='color:#64748b; font-size:11px; margin-top:2px;'>Yüksek OSB, Yüksek Kirlilik</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # 2. AŞAMA: DİNAMİK İL SEÇİCİ (st.selectbox)
    iller = sorted(df["il"].unique().tolist())
    
    # URL veya öncelikli varsayılan il seçimi (örn. Iğdır Kategori A örneği, Bursa Kategori B örneği)
    q_il = st.query_params.get("il", "")
    if q_il in iller:
        default_index = iller.index(q_il)
    elif "Iğdır" in iller:
        default_index = iller.index("Iğdır")
    else:
        default_index = 0

    col_sel_left, col_sel_right = st.columns([1.5, 2.5])
    with col_sel_left:
        secilen_il = st.selectbox(
            "📍 Analiz Edilecek İli Seçin:",
            iller,
            index=default_index,
            help="81 il arasından dilediğinizi seçerek yapay zeka anomali sınıflandırmasını ve projeksiyon modelini inceleyin."
        )

    il_row = df[df["il"] == secilen_il].iloc[0]
    category, growth_rate = determine_city_category(il_row, q1_osb, q3_osb, q1_pm25, q3_pm25)

    with col_sel_right:
        # Seçilen ilin hızlı rozet durumu
        if category == "Kategori A":
            cat_badge_html = "<span style='background:rgba(245,158,11,0.15); border:1px solid #f59e0b; color:#fbbf24; padding:6px 14px; border-radius:20px; font-size:13px; font-weight:700;'>⚠️ Kategori A: Coğrafi Kapan / Sessiz Tehlike</span>"
        elif category == "Kategori B":
            cat_badge_html = "<span style='background:rgba(239,68,68,0.15); border:1px solid #ef4444; color:#f87171; padding:6px 14px; border-radius:20px; font-size:13px; font-weight:700;'>🚨 Kategori B: Ağır Sanayi Baskısı</span>"
        else:
            cat_badge_html = "<span style='background:rgba(0,229,219,0.15); border:1px solid #00e5db; color:#38bdf8; padding:6px 14px; border-radius:20px; font-size:13px; font-weight:700;'>✅ Normal / Dengeli Profil</span>"

        st.markdown(
            f"<div style='margin-top:28px; display:flex; align-items:center; gap:12px;'>"
            f"{cat_badge_html}"
            f"<span style='color:#94a3b8; font-size:13px;'>"
            f"Mevcut PM2.5: <strong style='color:#f8fafc;'>{il_row['pm25']:.1f} µg/m³</strong> &bull; "
            f"OSB Sayısı: <strong style='color:#f8fafc;'>{int(il_row['osb_sayisi'])}</strong>"
            f"</span></div>",
            unsafe_allow_html=True
        )

    st.write("")

    # 5 YILLIK TAHMİN MODELİ (2026-2031)
    years, proj_values = build_projection_series(float(il_row["pm25"]), growth_rate)

    # 3. VE 4. AŞAMA: PROJEKSİYON GRAFİĞİ + DİNAMİK UYARI VE ALINACAK ÖNLEMLER (REÇETE)
    col_chart, col_recipe = st.columns([1.6, 1.4])

    with col_chart:
        fig = create_forecast_figure(
            city_name=secilen_il,
            category=category,
            years=years,
            values=proj_values,
            growth_rate=growth_rate
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_recipe:
        # Kategoriye göre pulsing glow sınıfı ve başlık renkleri
        if category == "Kategori A":
            pulse_cls = "pulse-box-a"
            title_cls = "neon-amber-title"
            
            neden_sonuc_metni = (
                f"Yapay Zeka Analizi: {secilen_il} ilinde sanayi yoğunluğu düşük olmasına rağmen "
                f"hava kirliliği tehlikeli boyuttadır. Bu durumun ana nedeni coğrafi çanak yapısı (rüzgar hapsi) "
                f"ve kış aylarındaki kalitesiz yakıt kullanımıdır (Termal İnversiyon)."
            )
            onlem_metni = (
                "Acil Eylem Planı: Doğalgaz/temiz enerji altyapısı acilen teşvik edilmeli, "
                "rüzgar koridorlarını kesecek yüksek yapılaşma derhal durdurulmalıdır."
            )
            
        elif category == "Kategori B":
            pulse_cls = "pulse-box-b"
            title_cls = "neon-red-title"
            
            neden_sonuc_metni = (
                f"Yapay Zeka Analizi: {secilen_il} ilindeki kirlilik doğrudan yoğun OSB ve "
                f"endüstriyel faaliyetler kaynaklıdır."
            )
            onlem_metni = (
                "Acil Eylem Planı: Fabrika bacalarına akıllı (IoT) filtre zorunluluğu getirilmeli, "
                "yeni açılacak sanayi bölgeleri şehrin hakim rüzgar yönünün tersine planlanmalıdır."
            )
            
        else:
            pulse_cls = "pulse-box-normal"
            title_cls = "neon-blue-title"
            
            neden_sonuc_metni = (
                f"Yapay Zeka Analizi: {secilen_il} ilinde sanayi yoğunluğu ve hava kirliliği göstergeleri "
                f"dengeli/normal seyretmektedir. Aşırı uç bir jeolojik veya endüstriyel anomali saptanmamıştır."
            )
            onlem_metni = (
                "Koruyucu Eylem Planı: Mevcut emisyon denetimleri sürdürülmeli, sanayi atık kontrolleri "
                "ve yeşil enerji dönüşümü desteklenmelidir."
            )

        # 1. Bilgi Balonu: Neden-Sonuç Analizi
        st.markdown(f"""
        <div class='info-bubble'>
            <div class='neon-blue-title'>
                <span>🔬</span> Yapay Zeka Neden-Sonuç Analizi
            </div>
            <p class='bubble-text'>{neden_sonuc_metni}</p>
        </div>
        """, unsafe_allow_html=True)

        # 2. Bilgi Balonu: Alınacak Önlemler (Pulsing Glow ile Çerçevelenmiş Reçete)
        st.markdown(f"""
        <div class='info-bubble {pulse_cls}'>
            <div class='{title_cls}'>
                <span>🚨</span> Alınacak Önlemler (Acil Eylem Reçetesi)
            </div>
            <p class='bubble-text'><strong>{onlem_metni}</strong></p>
        </div>
        """, unsafe_allow_html=True)

        # 3. Bilgi Balonu: Projeksiyon Metrik Özeti
        growth_pct = round(((proj_values[-1] - proj_values[0]) / proj_values[0]) * 100, 1)
        sign = "+" if growth_pct > 0 else ""
        st.markdown(f"""
        <div class='info-bubble' style='margin-bottom:0;'>
            <div style='color:#94a3b8; font-size:12px; margin-bottom:6px;'>5 Yıllık Projeksiyon Değişimi (2026 ➔ 2031)</div>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <span style='font-size:12px; color:#64748b;'>2026:</span>
                    <strong style='font-size:15px; color:#f8fafc; margin-left:4px;'>{proj_values[0]:.1f} µg/m³</strong>
                </div>
                <div style='color:#38bdf8; font-size:16px;'>➔</div>
                <div>
                    <span style='font-size:12px; color:#64748b;'>2031:</span>
                    <strong style='font-size:15px; color:#f8fafc; margin-left:4px;'>{proj_values[-1]:.1f} µg/m³</strong>
                </div>
                <div style='background:rgba(239,68,68,0.15); border:1px solid rgba(239,68,68,0.3); color:#f87171; padding:3px 10px; border-radius:6px; font-size:12px; font-weight:700;'>
                    {sign}%{growth_pct} Kümülatif
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 4. AŞAMA ALT BÖLÜM: DİNAMİK OLARAK FİLTRELENEN TÜM KATEGORİ LİSTELERİ
    st.write("")
    st.markdown("<hr style='border-color:#1e293b; margin:20px 0;'>", unsafe_allow_html=True)
    st.markdown("#### 📋 81 İl Otomatik Anomali Grupları (Pandas Filtreleme)")

    col_list_a, col_list_b = st.columns(2)
    with col_list_a:
        st.markdown(f"""
        <div class='info-bubble'>
            <div class='neon-amber-title'>
                <span>⛰️</span> Kategori A: Coğrafi Kapan İlleri ({len(kat_a_df)} İl)
            </div>
            <p style='color:#94a3b8; font-size:12px; margin-bottom:10px;'>
                OSB Sayısı ≤ {q1_osb:.0f} (Alt %25) ve PM2.5 ≥ {q3_pm25:.1f} µg/m³ (Üst %25)
            </p>
            <div style='display:flex; flex-wrap:wrap; gap:6px;'>
                {"".join([f"<span class='kpi-chip' style='background:#2a1b0a; border:1px solid #f59e0b; color:#fbbf24;'>{r['il']} (PM2.5: {r['pm25']:.1f}, OSB: {int(r['osb_sayisi'])})</span>" for _, r in kat_a_df.sort_values(by="pm25", ascending=False).iterrows()])}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_list_b:
        st.markdown(f"""
        <div class='info-bubble'>
            <div class='neon-red-title'>
                <span>🏭</span> Kategori B: Ağır Sanayi Baskısı İlleri ({len(kat_b_df)} İl)
            </div>
            <p style='color:#94a3b8; font-size:12px; margin-bottom:10px;'>
                OSB Sayısı ≥ {q3_osb:.0f} (Üst %25) ve PM2.5 ≥ {q3_pm25:.1f} µg/m³ (Üst %25)
            </p>
            <div style='display:flex; flex-wrap:wrap; gap:6px;'>
                {"".join([f"<span class='kpi-chip' style='background:#2d1215; border:1px solid #ef4444; color:#f87171;'>{r['il']} (PM2.5: {r['pm25']:.1f}, OSB: {int(r['osb_sayisi'])})</span>" for _, r in kat_b_df.sort_values(by="pm25", ascending=False).iterrows()])}
            </div>
        </div>
        """, unsafe_allow_html=True)
