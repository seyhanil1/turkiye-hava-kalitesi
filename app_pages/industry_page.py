"""
Sanayi Profili Sayfası (Industrial Profile)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def strip_html(text: str) -> str:
    """Markdown HTML içeriklerindeki boş satırları ve 4+ boşluk girintilerini temizleyerek <pre><code> çökmesini önler."""
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def render_industry_page(df: pd.DataFrame):
    """
    OSB verileri: OSBÜK (indirme tarihi: GG.AA.2026) ve hava kirliliği kesişimini
    fütüristik neon cam arayüzle sunar.
    """
    # Veri hesaplamaları (Orijinal veriler ve değişkenler birebir korunur)
    if "toplam_osb" in df.columns:
        toplam_osb = int(df["toplam_osb"].sum())
    elif "osb_sayisi" in df.columns:
        toplam_osb = int(df["osb_sayisi"].sum())
    else:
        toplam_osb = 419

    if "osb_alani_hektar" in df.columns:
        toplam_hektar = float(df["osb_alani_hektar"].sum())
    else:
        toplam_hektar = 143267.5

    toplam_faal = int(df["faal_osb"].sum()) if "faal_osb" in df.columns else 296
    toplam_parsel = int(df["toplam_parsel"].sum()) if "toplam_parsel" in df.columns else 64220

    toplam_hektar_str = f"{toplam_hektar:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # Başlık
    st.markdown(strip_html("""
    <div style="margin-bottom: 22px;">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
            <div style="background:rgba(0, 242, 254, 0.15); color:#00f2fe; width:34px; height:34px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-weight:800; font-family:monospace; font-size:13px; border:1px solid rgba(0, 242, 254, 0.3);">OSB</div>
            <h2 style="margin:0; font-size:24px; font-weight:800; color:#ffffff; letter-spacing:-0.5px;">
                Sanayi Baskısı, OSB Kümeleri & Çevre Karnesi
            </h2>
        </div>
        <p style="margin:0; font-size:13px; color:#8faec9;">
            OSB verileri: OSBÜK (indirme tarihi: GG.AA.2026) kayıtlarına göre Organize Sanayi Bölgeleri (OSB), üretim havzaları ve emisyon odakları.
        </p>
    </div>
    """).strip(), unsafe_allow_html=True)

    # ========================================================
    # 1. ÜST KISIM - ÇİFT NEON KPI BLOKLARI (st.columns(2))
    # ========================================================
    kpi_col1, kpi_col2 = st.columns(2)

    with kpi_col1:
        st.markdown(strip_html(f"""
        <div style="background: linear-gradient(135deg, rgba(0, 242, 254, 0.12) 0%, rgba(11, 19, 43, 0.95) 100%);
                    border: 1px solid #00f2fe;
                    border-radius: 16px;
                    padding: 24px;
                    box-shadow: 0 10px 30px rgba(0, 242, 254, 0.2), inset 0 0 20px rgba(0, 242, 254, 0.08);
                    backdrop-filter: blur(12px);
                    position: relative;
                    overflow: hidden;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="background: rgba(0, 242, 254, 0.15); color: #00f2fe; border: 1px solid #00f2fe; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;">
                        SANAYİ SİCİLİ • BAKANLIK VERİSİ
                    </span>
                </div>
                <span style="background: rgba(2, 18, 32, 0.8); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); padding: 3px 8px; border-radius: 6px; font-size: 10.5px; font-weight: 600;">
                    BASKI ÖLÇER
                </span>
            </div>
            <div style="font-size: 13px; color: #8faec9; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                Türkiye Geneli Toplam OSB Sayısı
            </div>
            <div style="font-size: 38px; font-weight: 900; color: #ffffff; margin: 4px 0; text-shadow: 0 0 20px rgba(0, 242, 254, 0.4);">
                {toplam_osb} <span style="font-size:20px; color:#00f2fe; font-weight:700;">Adet OSB</span>
            </div>
            <div style="font-size: 12px; color: #cbd5e1; line-height: 1.5; margin-top: 6px;">
                Bakanlık siciline kayıtlı 81 ilde faal ({toplam_faal} aktif) ve tescilli organize sanayi bölgesi. Toplam {toplam_parsel:,} endüstriyel üretim parselini barındırmaktadır.
            </div>
        </div>
        """).strip(), unsafe_allow_html=True)

    with kpi_col2:
        st.markdown(strip_html(f"""
        <div style="background: linear-gradient(135deg, rgba(255, 159, 61, 0.12) 0%, rgba(11, 19, 43, 0.95) 100%);
                    border: 1px solid #ff9f3d;
                    border-radius: 16px;
                    padding: 24px;
                    box-shadow: 0 10px 30px rgba(255, 159, 61, 0.2), inset 0 0 20px rgba(255, 159, 61, 0.08);
                    backdrop-filter: blur(12px);
                    position: relative;
                    overflow: hidden;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="background: rgba(255, 159, 61, 0.15); color: #ff9f3d; border: 1px solid #ff9f3d; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;">
                        TAHSİSLİ ALAN • HARİTA ENVANTERİ
                    </span>
                </div>
                <span style="background: rgba(2, 18, 32, 0.8); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.4); padding: 3px 8px; border-radius: 6px; font-size: 10.5px; font-weight: 600;">
                    BASKI ÖLÇER
                </span>
            </div>
            <div style="font-size: 13px; color: #8faec9; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                Toplam OSB Sanayi Alanı
            </div>
            <div style="font-size: 38px; font-weight: 900; color: #ffffff; margin: 4px 0; text-shadow: 0 0 20px rgba(255, 159, 61, 0.4);">
                {toplam_hektar_str} <span style="font-size:20px; color:#ff9f3d; font-weight:700;">Hektar</span>
            </div>
            <div style="font-size: 12px; color: #cbd5e1; line-height: 1.5; margin-top: 6px;">
                Sanayi ve Teknoloji Bakanlığı onaylı organize sanayi bölgelerinin resmi yüzölçümü toplamı (OSBÜK verisi).
            </div>
        </div>
        """).strip(), unsafe_allow_html=True)

    st.write("")

    # ========================================================
    # 2. ORTA KISIM - BÖLGESEL OSB & KİRLİLİK KESİŞİMİ ANALİZİ (st.columns([3, 2]))
    # ========================================================
    col_chart, col_decisions = st.columns([3, 2])

    with col_chart:
        st.markdown(strip_html("""
        <div style="font-size:15px; font-weight:700; color:#ffffff; margin-bottom:8px; display:flex; align-items:center; gap:8px;">
            Bölgesel OSB Yoğunluğu ve Çevre Baskısı Sıralaması
        </div>
        """).strip(), unsafe_allow_html=True)

        # 7 Coğrafi Bölge Verileri (Talep edilen sıra: Marmara, İç Anadolu, Ege, Karadeniz, Güneydoğu, Akdeniz, Doğu Anadolu)
        regions_data = [
            {"bolge": "Marmara", "osb": 100, "pm25": 35.7, "hektar": 793310, "pay": "%23,9"},
            {"bolge": "İç Anadolu", "osb": 75, "pm25": 34.0, "hektar": 1088440, "pay": "%17,9"},
            {"bolge": "Ege", "osb": 66, "pm25": 36.3, "hektar": 453187, "pay": "%15,8"},
            {"bolge": "Karadeniz", "osb": 70, "pm25": 31.4, "hektar": 253054, "pay": "%16,7"},
            {"bolge": "Güneydoğu Anadolu", "osb": 35, "pm25": 38.7, "hektar": 1016342, "pay": "%8,4"},
            {"bolge": "Akdeniz", "osb": 44, "pm25": 35.1, "hektar": 412881, "pay": "%10,5"},
            {"bolge": "Doğu Anadolu", "osb": 29, "pm25": 44.2, "hektar": 113399, "pay": "%6,9"}
        ]
        
        # Horizontal bar için sıralı listeler
        b_names = [r["bolge"] for r in regions_data][::-1]
        b_osb = [r["osb"] for r in regions_data][::-1]
        b_texts = [f"{r['osb']} OSB | PM2.5: {r['pm25']} µg/m³ ({r['pay']} Baskı)" for r in regions_data][::-1]
        b_pm25 = [r["pm25"] for r in regions_data][::-1]

        fig_bar = go.Figure(go.Bar(
            x=b_osb,
            y=b_names,
            orientation="h",
            marker=dict(
                color=b_pm25,
                colorscale=[
                    [0.0, "#0284c7"],
                    [0.5, "#00f2fe"],
                    [0.8, "#f59e0b"],
                    [1.0, "#ef4444"]
                ],
                line=dict(color="rgba(255,255,255,0.15)", width=1)
            ),
            text=b_texts,
            textposition="inside",
            insidetextanchor="start",
            textfont=dict(color="#ffffff", size=11, family="sans-serif")
        ))

        fig_bar.update_layout(
            height=370,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(
                tickfont=dict(color="#ffffff", size=12, family="sans-serif"),
                gridcolor="rgba(255,255,255,0.05)"
            ),
            xaxis=dict(
                title=dict(text="OSB Sayısı (Adet)", font=dict(color="#8faec9", size=11)),
                tickfont=dict(color="#94a3b8"),
                gridcolor="rgba(255,255,255,0.06)",
                range=[0, 115]
            ),
            margin=dict(t=10, l=10, r=20, b=30)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_decisions:
        st.markdown(strip_html("""
        <div style="font-size:15px; font-weight:700; color:#ffffff; margin-bottom:8px; display:flex; align-items:center; gap:8px;">
            <span>📊</span> Yüksek OSB ve Kirlilik Göstergeleri
        </div>
        """).strip(), unsafe_allow_html=True)

        st.markdown(strip_html("""
        <div style="display:flex; flex-direction:column; gap:12px;">
            <!-- KART 1: MARMARA -->
            <div style="background: rgba(17, 26, 46, 0.92);
                        border: 1px solid rgba(239, 68, 68, 0.5);
                        border-radius: 12px;
                        padding: 16px;
                        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.15);
                        backdrop-filter: blur(10px);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <span style="font-size:14px; font-weight:800; color:#ffffff;">
                        Marmara Aksı (Kocaeli, Bursa, Tekirdağ)
                    </span>
                    <div style="display:flex; gap:6px;">
                        <span style="background: rgba(239, 68, 68, 0.2); color: #fca5a5; border: 1px solid #ef4444; padding: 2px 7px; border-radius: 4px; font-size: 10px; font-weight: 700;">
                            YÜKSEK OSB
                        </span>
                        <span style="background: rgba(0, 242, 254, 0.15); color: #00f2fe; border: 1px solid #00f2fe; padding: 2px 7px; border-radius: 4px; font-size: 10px; font-weight: 700;">
                            SANAYİ SİCİLİ
                        </span>
                    </div>
                </div>
                <div style="font-size: 12px; color: #cbd5e1; line-height: 1.5;">
                    Marmara bölgesi genelinde 100 OSB ve 12.434 parsel yer almakta olup yüksek OSB yoğunluğuna sahip iller bu koridorda bulunmaktadır.
                </div>
                <div style="margin-top:8px; font-size:11px; color:#f87171; font-weight:600; display:flex; align-items:center; gap:4px;">
                    <span>•</span> Gösterge Notu: OSB sayısı ve sanayi parseli bakımından en yoğun bölgedir.
                </div>
            </div>

            <!-- KART 2: GÜNEYDOĞU -->
            <div style="background: rgba(17, 26, 46, 0.92);
                        border: 1px solid rgba(245, 158, 11, 0.5);
                        border-radius: 12px;
                        padding: 16px;
                        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.15);
                        backdrop-filter: blur(10px);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <span style="font-size:14px; font-weight:800; color:#ffffff;">
                        Güneydoğu Aksı (Gaziantep)
                    </span>
                    <div style="display:flex; gap:6px;">
                        <span style="background: rgba(245, 158, 11, 0.2); color: #fde047; border: 1px solid #f59e0b; padding: 2px 7px; border-radius: 4px; font-size: 10px; font-weight: 700;">
                            YÜKSEK PM2,5
                        </span>
                        <span style="background: rgba(0, 242, 254, 0.15); color: #00f2fe; border: 1px solid #00f2fe; padding: 2px 7px; border-radius: 4px; font-size: 10px; font-weight: 700;">
                            SANAYİ SİCİLİ
                        </span>
                    </div>
                </div>
                <div style="font-size: 12px; color: #cbd5e1; line-height: 1.5;">
                    Gaziantep 8 OSB ve yüksek PM2.5 seviyesiyle bölgenin en yüksek sanayi altyapısına sahip ilidir.
                </div>
                <div style="margin-top:8px; font-size:11px; color:#fbbf24; font-weight:600; display:flex; align-items:center; gap:4px;">
                    <span>•</span> Gösterge Notu: Bölgede 35 OSB yer almakta olup ortalama PM2.5 38,7 µg/m³ seviyesindedir.
                </div>
            </div>
        </div>
        """).strip(), unsafe_allow_html=True)

    st.write("")

    # ========================================================
    # 3. İL BAZLI SANAYİ DETAY TABLOSU (EXPANDER)
    # ========================================================
    with st.expander("81 İl Sanayi ve OSB Sicil Tablosu"):
        st.markdown("##### 81 İl Sanayi ve Organize Sanayi Bölgeleri (OSB) Sicil Envanteri")
        st.dataframe(
            df[["il", "bolge", "toplam_osb", "faal_osb", "osb_alani_hektar", "toplam_parsel", "sanayi_tipi", "pm25"]].rename(columns={
                "il": "İl", "bolge": "Bölge", "toplam_osb": "Toplam OSB", "faal_osb": "Faal OSB",
                "osb_alani_hektar": "Alan (Hektar)", "toplam_parsel": "Parsel", "sanayi_tipi": "Kategori", "pm25": "PM2.5 (µg/m³)"
            }),
            use_container_width=True,
            hide_index=True
        )
