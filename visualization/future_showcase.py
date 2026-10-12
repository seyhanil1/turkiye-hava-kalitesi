"""
🔮 2035 Gelecek Yol Ayrımı Vitrini (Ana Sayfa / Genel Bakış Entegrasyonu)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import streamlit as st


CLEAN_MINI_SVG = """<svg width="64" height="64" viewBox="0 0 140 140" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="70" cy="70" r="64" fill="#052433" stroke="#00f2fe" stroke-width="3"/>
  <circle cx="102" cy="38" r="14" fill="#00f2fe" opacity="0.85"/>
  <rect x="30" y="58" width="22" height="46" rx="2" fill="#0c4a6e" stroke="#38bdf8" stroke-width="1.5"/>
  <rect x="56" y="46" width="26" height="58" rx="2" fill="#064e3b" stroke="#10b981" stroke-width="2"/>
  <line x1="96" y1="50" x2="96" y2="104" stroke="#e0f2fe" stroke-width="3" stroke-linecap="round"/>
  <circle cx="96" cy="50" r="4" fill="#00f2fe"/>
  <path d="M96 50 L96 26 L98 50 Z" fill="#e0f2fe"/>
  <path d="M96 50 L116 62 L96 52 Z" fill="#e0f2fe"/>
  <path d="M96 50 L76 62 L95 48 Z" fill="#e0f2fe"/>
  <rect x="38" y="104" width="36" height="14" rx="3" fill="#0284c7" stroke="#00f2fe" stroke-width="1.5"/>
</svg>"""

GRAY_MINI_SVG = """<svg width="64" height="64" viewBox="0 0 140 140" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="70" cy="70" r="64" fill="#2d0b10" stroke="#ff4b4b" stroke-width="3"/>
  <ellipse cx="50" cy="30" rx="22" ry="12" fill="#475569" opacity="0.7"/>
  <ellipse cx="75" cy="22" rx="24" ry="14" fill="#334155" opacity="0.8"/>
  <polygon points="34,54 44,54 42,106 32,106" fill="#334155" stroke="#ff4b4b" stroke-width="1.5"/>
  <polygon points="56,44 68,44 66,106 54,106" fill="#1e293b" stroke="#f87171" stroke-width="2"/>
  <rect x="74" y="68" width="36" height="38" rx="2" fill="#0f172a" stroke="#64748b" stroke-width="1.5"/>
  <circle cx="106" cy="38" r="6" fill="#ef4444"/>
  <polygon points="70,110 60,126 80,126" fill="#f59e0b"/>
</svg>"""


def render_future_showcase_section():
    """
    Genel Bakış ana sayfasında haritanın hemen altına yerleştirilen
    tam genişlikte 2035 Gelecek Yol Ayrımı vitrinini render eder.
    """
    # 1. Stil Tanımları
    st.markdown("""
    <style>
    .future-showcase-wrap {
        background: linear-gradient(135deg, rgba(11, 19, 43, 0.95) 0%, rgba(3, 22, 38, 0.98) 100%);
        border: 1px solid rgba(0, 242, 254, 0.3);
        border-radius: 18px;
        padding: 24px 28px;
        margin-top: 24px;
        margin-bottom: 24px;
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.5);
    }
    .showcase-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 20px;
        padding-bottom: 14px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    .showcase-title-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .showcase-title {
        font-size: 20px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.3px;
        margin: 0;
    }
    .showcase-subtitle {
        font-size: 13px;
        color: #94a3b8;
        margin: 3px 0 0 0;
    }
    .showcase-card {
        border-radius: 14px;
        padding: 22px;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .showcase-card:hover {
        transform: translateY(-3px);
    }
    .showcase-clean {
        background: linear-gradient(145deg, rgba(11, 28, 44, 0.88) 0%, rgba(6, 38, 48, 0.92) 100%);
        border: 1px solid rgba(0, 242, 254, 0.45);
        box-shadow: 0 8px 28px rgba(0, 242, 254, 0.14);
    }
    .showcase-clean:hover {
        border-color: #00f2fe;
        box-shadow: 0 12px 36px rgba(0, 242, 254, 0.25);
    }
    .showcase-gray {
        background: linear-gradient(145deg, rgba(28, 14, 18, 0.88) 0%, rgba(40, 16, 22, 0.92) 100%);
        border: 1px solid rgba(255, 75, 75, 0.45);
        box-shadow: 0 8px 28px rgba(255, 75, 75, 0.14);
    }
    .showcase-gray:hover {
        border-color: #ff4b4b;
        box-shadow: 0 12px 36px rgba(255, 75, 75, 0.25);
    }
    .showcase-badge-clean {
        background: rgba(0, 242, 254, 0.15);
        color: #00f2fe;
        border: 1px solid #00f2fe;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.5px;
    }
    .showcase-badge-gray {
        background: rgba(255, 75, 75, 0.15);
        color: #ff4b4b;
        border: 1px solid #ff4b4b;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.5px;
    }
    </style>
    """, unsafe_allow_html=True)

    # 2. Vitrin Başlık Alanı
    st.markdown("""
    <div class="future-showcase-wrap">
        <div class="showcase-header">
            <div class="showcase-title-left">
                <span style="font-size:32px;">🔮</span>
                <div>
                    <h3 class="showcase-title">2035: Türkiye'nin Gelecek Yol Ayrımı (Politika Simülatörü)</h3>
                    <p class="showcase-subtitle">Hava kalitesi politikalarının 10 yıllık sağlık ve bütçe bilançosu.</p>
                </div>
            </div>
            <div>
                <span style="background:rgba(0, 242, 254, 0.12); border:1px solid #00f2fe; color:#00f2fe; padding:6px 14px; border-radius:20px; font-size:12px; font-weight:700;">
                    ⏳ 10 Yıllık Karar Projeksiyonu
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 3. İki Büyük Cam Kart (st.columns(2))
    col_clean, col_gray = st.columns(2)

    with col_clean:
        st.markdown(f"""
        <div class="showcase-card showcase-clean">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <span class="showcase-badge-clean">🌱 1. YOL: EKOLOJİK BİLİNÇ & YEŞİL DÖNÜŞÜM</span>
                    {CLEAN_MINI_SVG}
                </div>
                <div style="font-size:17px; font-weight:800; color:#ffffff; margin-bottom:8px;">
                    🌱 Ekolojik Politika Senaryosu (2035 Projeksiyonu)
                </div>
                <div style="background:rgba(0, 242, 254, 0.1); border-left:3px solid #00f2fe; border-radius:6px; padding:12px; margin-bottom:12px;">
                    <div style="font-size:14px; font-weight:800; color:#00f2fe;">
                        2035 Senaryosu: ~15.000 – 21.000 Önlenebilir Tahmini Ölüm | 70 – 95 Milyar TL Sağlık Tasarrufu
                    </div>
                </div>
                <p style="font-size:12.5px; color:#cbd5e1; line-height:1.55; margin:0;">
                    81 ilde DSÖ hava kalitesi standartlarına uyum, sanayide SEÖS filtre zorunluluğu, toplu taşımada elektrikli dönüşüm ve +3,2 yıl ortalama beklenen yaşam süresi artışı.
                </p>
            </div>
            <div style="margin-top:14px; font-size:11.5px; color:#38bdf8; font-weight:700;">
                ✓ PM2.5 Seviyesinde %72 İyileşme Hedefi (~10,2 µg/m³ / DSÖ Ara Hedef-4)
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_gray:
        st.markdown(f"""
        <div class="showcase-card showcase-gray">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <span class="showcase-badge-gray">🌫️ 2. YOL: EYLEMSİZLİK & İHMAL</span>
                    {GRAY_MINI_SVG}
                </div>
                <div style="font-size:17px; font-weight:800; color:#ffffff; margin-bottom:8px;">
                    🌫️ Eylemsizlik Senaryosu (2035 Projeksiyonu)
                </div>
                <div style="background:rgba(255, 75, 75, 0.1); border-left:3px solid #ff4b4b; border-radius:6px; padding:12px; margin-bottom:12px;">
                    <div style="font-size:14px; font-weight:800; color:#ff4b4b;">
                        Eylemsizlik Riski: 10 Yıllık Kümülatif ~120.000 – 160.000 Ek Önlenebilir Vefat Riski | 180 – 240 Milyar TL Ek Sağlık Maliyeti
                    </div>
                </div>
                <p style="font-size:12.5px; color:#cbd5e1; line-height:1.55; margin:0;">
                    Kalitesiz linyit ve denetimsiz sanayi emisyonları, çanak havzalarda solunum baskısı, genç nüfusta kronik astım riski ve -3,8 yıl beklenen ömür kaybı projeksiyonu.
                </p>
            </div>
            <div style="margin-top:14px; font-size:11.5px; color:#f87171; font-weight:700;">
                ⚠️ PM2.5 Seviyesinde >75 µg/m³ Ağır Kirlilik Riski
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 4. Kapanış ve Detaylı Keşif Butonu
    st.markdown("""
    <div style="font-size:11px; color:#64748b; margin-top:14px; margin-bottom:8px; text-align:right;">
        * 2035 projeksiyonları varsayımsal politika simülasyonudur; kesin resmi taahhüt veya garanti niteliği taşımaz.
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    if st.button("🔮 Gelecek Simülasyonunu Detaylı Keşfet ➔", key="btn_goto_future_showcase", use_container_width=True):
        st.session_state["nav_radio"] = "🔮 2035: Gelecek Yol Ayrımı"
        st.query_params["page"] = "future_2035"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
