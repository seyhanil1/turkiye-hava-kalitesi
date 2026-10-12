"""
🌍 DSÖ Kılavuz Standartları & Halk Sağlığı Koruma Kalkanı
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

Özellikler:
1. Üst Kısım - DSÖ Kılavuz Rozetleri (Hap Bilgi Baloncukları):
   - 🟢 DSÖ Yıllık Kılavuz Değeri: 5 µg/m³
   - 🟡 DSÖ 24 Saatlik Kılavuz Değeri: 15 µg/m³
   - 🔴 Türkiye Ölçüm Ortalaması (Kara Rapor): 36,3 µg/m³ (Kılavuz Değerin ~7,3 Katı)
   - 🚨 Kritik Alarm Seviyesi: >50 µg/m³
2. Alt Kısım - 4 Tematik Sağlık & Korunma Baloncuğu (st.columns(4)):
   - 🫁 1. Kart: Hassas Gruplar (Kronik/Çocuk/Yaşlı)
   - 😷 2. Kart: Bireysel Maske & Filtre
   - 🏠 3. Kart: Ev İçi & Kapalı Alan İzolasyonu
   - 🚶‍♂️ 4. Kart: Egzersiz ve Ulaşım Stratejisi
3. Koyu lacivert/neon tasarım (#0b132b, #111a2e, #00f2fe).
"""

import streamlit as st


def render_health_shield_section():
    """
    DSÖ Kılavuz Standartları & Halk Sağlığı Koruma Kalkanı bileşenini render eder.
    """
    # 1. Özel Stil Tanımları
    st.markdown("""
    <style>
    .health-shield-container {
        margin-top: 24px;
        margin-bottom: 20px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .health-shield-header {
        background: linear-gradient(135deg, #091830 0%, #0d2242 100%);
        border: 1px solid rgba(0, 242, 254, 0.3);
        border-radius: 16px;
        padding: 22px 26px;
        margin-bottom: 18px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    .badge-pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 14px;
    }
    .badge-pill {
        border-radius: 30px;
        padding: 8px 18px;
        font-size: 13px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        backdrop-filter: blur(8px);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .badge-pill:hover {
        transform: translateY(-2px);
    }
    .badge-green {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.5);
        color: #34d399;
    }
    .badge-yellow {
        background: rgba(250, 204, 21, 0.12);
        border: 1px solid rgba(250, 204, 21, 0.5);
        color: #facc15;
    }
    .badge-red {
        background: rgba(239, 68, 68, 0.12);
        border: 1px solid rgba(239, 68, 68, 0.55);
        color: #f87171;
    }
    .badge-alarm {
        background: rgba(225, 29, 72, 0.15);
        border: 1px solid rgba(225, 29, 72, 0.6);
        color: #fb7185;
    }
    .shield-card {
        background: linear-gradient(145deg, #0d1b32 0%, #081324 100%);
        border: 1px solid rgba(0, 242, 254, 0.22);
        border-radius: 14px;
        padding: 22px 20px;
        height: 100%;
        min-height: 235px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
        transition: all 0.25s ease-in-out;
    }
    .shield-card:hover {
        transform: translateY(-4px);
        border-color: #00f2fe;
        box-shadow: 0 10px 28px rgba(0, 242, 254, 0.22);
    }
    .shield-card-title {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(20, 55, 99, 0.7);
    }
    .shield-card-title h4 {
        margin: 0;
        font-size: 15px;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: 0.2px;
    }
    .shield-card-body {
        color: #cbd5e1;
        font-size: 13.5px;
        line-height: 1.65;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # 2. Üst Kısım: Başlık & DSÖ Kılavuz Rozetleri (Hap Bilgi Baloncukları)
    st.markdown("""
    <div id='healthShieldSection' class='health-shield-container'>
        <div class='health-shield-header'>
            <div style='display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px;'>
                <div style='display: flex; align-items: center; gap: 14px;'>
                    <span style='font-size: 32px;'>🌍</span>
                    <div>
                        <h3 style='margin: 0; color: #ffffff; font-size: 20px; font-weight: 800; letter-spacing: 0.3px;'>
                            DSÖ Kılavuz Standartları &amp; Halk Sağlığı Koruma Kalkanı
                        </h3>
                        <p style='margin: 4px 0 0 0; color: #94a3b8; font-size: 12.5px;'>
                            Dünya Sağlık Örgütü (WHO 2021) Eşikleri &amp; Risk Altındaki Gruplar İçin Kanıta Dayalı Koruyucu Sağlık Protokolü
                        </p>
                    </div>
                </div>
                <div>
                    <span style='background: rgba(0, 242, 254, 0.12); border: 1px solid #00f2fe; color: #00f2fe; padding: 6px 16px; border-radius: 20px; font-size: 12px; font-weight: 700; display: inline-flex; align-items: center; gap: 6px;'>
                        🛡️ Aktif Sağlık Kalkanı
                    </span>
                </div>
            </div>
            <div class='badge-pill-row'>
                <div class='badge-pill badge-green'>
                    <span>🟢</span> DSÖ Yıllık Kılavuz Değeri: <strong style='color:#ffffff; margin-left:3px;'>5 µg/m³</strong>
                </div>
                <div class='badge-pill badge-yellow'>
                    <span>🟡</span> DSÖ 24 Saatlik Kılavuz Değeri: <strong style='color:#ffffff; margin-left:3px;'>15 µg/m³</strong>
                </div>
                <div class='badge-pill badge-red'>
                    <span>🔴</span> Türkiye Ölçüm Ortalaması (Kara Rapor): <strong style='color:#ffffff; margin-left:3px;'>36,3 µg/m³</strong> <span style='font-size:11.5px; opacity:0.9;'>(Kılavuz Değerin ~7,3 Katı)</span>
                </div>
                <div class='badge-pill badge-alarm'>
                    <span>🚨</span> Kritik Alarm Seviyesi: <strong style='color:#ffffff; margin-left:3px;'>&gt;50 µg/m³</strong>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Alt Kısım: 4 Tematik Sağlık & Korunma Baloncuğu (st.columns(4))
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class='shield-card'>
            <div class='shield-card-title'>
                <span style='font-size: 24px;'>🫁</span>
                <h4>Hassas Gruplar (Kronik/Çocuk/Yaşlı)</h4>
            </div>
            <p class='shield-card-body'>
                PM2.5 seviyesi 30 µg/m³ üzerindeki günlerde KOAH, astım ve kalp hastaları açık hava sporlarını kısıtlamalı, ilaçlarını düzenli bulundurmalıdır.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='shield-card'>
            <div class='shield-card-title'>
                <span style='font-size: 24px;'>😷</span>
                <h4>Bireysel Maske &amp; Filtre</h4>
            </div>
            <p class='shield-card-body'>
                Yoğun sanayi veya çöküntü havzalarında (örn: Iğdır, Osmaniye) standart cerrahi maskeler yetersizdir; partikül tutucu <b>N95 / FFP2</b> filtreli maskeler tercih edilmelidir.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class='shield-card'>
            <div class='shield-card-title'>
                <span style='font-size: 24px;'>🏠</span>
                <h4>Ev İçi &amp; Kapalı Alan İzolasyonu</h4>
            </div>
            <p class='shield-card-body'>
                Trafiğin ve sanayinin yoğun olduğu sabah/akşam saatlerinde pencereleri kapalı tutun. İmkan varsa <b>HEPA filtreli</b> hava temizleme cihazları kullanın.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class='shield-card'>
            <div class='shield-card-title'>
                <span style='font-size: 24px;'>🚶‍♂️</span>
                <h4>Egzersiz ve Ulaşım Stratejisi</h4>
            </div>
            <p class='shield-card-body'>
                Kirliliğin yüksek olduğu saatlerde ana arterlerden ve yoğun kavşaklardan uzakta yürüyün; egzersiz için yeşil alan ve park rotalarını seçin.
            </p>
        </div>
        """, unsafe_allow_html=True)
