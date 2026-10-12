"""
Sağlık Rehberi Sayfası
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import streamlit as st
import pandas as pd


def render_health_guide_page(df: pd.DataFrame = None):
    """
    Dünya Sağlık Örgütü (DSÖ) ve T.C. Sağlık Bakanlığı ilkeleri doğrultusunda,
    hava kirliliği seviyelerine ve hassas gruplara yönelik genel sağlık rehberi.
    """
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="margin:0; font-size:24px; font-weight:800; color:#ffffff; letter-spacing:-0.5px;">
            Sağlık Rehberi ve Korunma Önerileri
        </h2>
        <p style="margin:4px 0 0 0; font-size:13px; color:#cbd5e1;">
            Partikül madde maruziyetine karşı seviye bazlı genel koruyucu sağlık yaklaşımları.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Yasal Uyarı Kutusu
    st.info(
        "**Yasal Bilgilendirme:** Bu sayfadaki içerikler Dünya Sağlık Örgütü (DSÖ) ve halk sağlığı kılavuzlarından "
        "derlenmiş genel bilgilendirme amaçlı metinlerdir. Kesinlikle tıbbi teşhis veya tedavi tavsiyesi niteliği taşımaz. "
        "Solunum veya dolaşım rahatsızlığı bulunan bireylerin hekimlerinin önerilerine uyması esastır."
    )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 1. Seviye Bazlı Davranış Rehberi
    st.markdown("### Hava Kalitesi Seviyesine Göre Davranış Kılavuzu")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style="background:#031b2e; border:1px solid #00e599; border-radius:10px; padding:16px; margin-bottom:14px;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                <span style="background:rgba(0,229,153,0.15); color:#00e599; font-weight:700; font-size:11px; padding:2px 8px; border-radius:4px;">
                    İYİ (≤15 µg/m³)
                </span>
                <strong style="color:#ffffff; font-size:14px;">Açık Hava İçin İdeal</strong>
            </div>
            <p style="font-size:12.5px; color:#cbd5e1; margin:0; line-height:1.5;">
                DSÖ 24 saatlik kılavuz eşiğinin altındaki seviyedir. Tüm nüfus grupları için açık hava fiziksel aktiviteleri ve havalandırma uygundur.
            </p>
        </div>

        <div style="background:#031b2e; border:1px solid #facc15; border-radius:10px; padding:16px; margin-bottom:14px;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                <span style="background:rgba(250,204,21,0.15); color:#facc15; font-weight:700; font-size:11px; padding:2px 8px; border-radius:4px;">
                    ORTA (15,1 - 30 µg/m³)
                </span>
                <strong style="color:#ffffff; font-size:14px;">Kabul Edilebilir Seviye</strong>
            </div>
            <p style="font-size:12.5px; color:#cbd5e1; margin:0; line-height:1.5;">
                Hava kalitesi genel nüfus için kabul edilebilir düzeydedir; ancak aşırı hassas bireylerde hafif solunum yolu rahatsızlıkları tetiklenebilir.
            </p>
        </div>

        <div style="background:#031b2e; border:1px solid #f97316; border-radius:10px; padding:16px; margin-bottom:14px;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                <span style="background:rgba(249,115,22,0.15); color:#f97316; font-weight:700; font-size:11px; padding:2px 8px; border-radius:4px;">
                    HASSAS (30,1 - 50 µg/m³)
                </span>
                <strong style="color:#ffffff; font-size:14px;">Hassas Gruplar İçin Uyarı</strong>
            </div>
            <p style="font-size:12.5px; color:#cbd5e1; margin:0; line-height:1.5;">
                DSÖ Ara Hedef-1 sınırını aşar. Çocuklar, yaşlılar ve astım/KOAH hastaları uzun süreli ağır açık hava egzersizlerini sınırlandırmalıdır.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background:#031b2e; border:1px solid #f87171; border-radius:10px; padding:16px; margin-bottom:14px;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                <span style="background:rgba(248,113,113,0.15); color:#f87171; font-weight:700; font-size:11px; padding:2px 8px; border-radius:4px;">
                    SAĞLIKSIZ (50,1 - 70 µg/m³)
                </span>
                <strong style="color:#ffffff; font-size:14px;">Genel Nüfus Riski</strong>
            </div>
            <p style="font-size:12.5px; color:#cbd5e1; margin:0; line-height:1.5;">
                Herkes için sağlık etkileri gözlenebilir. Açık havada yoğun efor sarf etmekten kaçınılmalı, pencereler yoğun trafik saatlerinde kapalı tutulmalıdır.
            </p>
        </div>

        <div style="background:#031b2e; border:1px solid #ef4444; border-radius:10px; padding:16px; margin-bottom:14px;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                <span style="background:rgba(239,68,68,0.15); color:#ef4444; font-weight:700; font-size:11px; padding:2px 8px; border-radius:4px;">
                    KRİTİK (>70 µg/m³)
                </span>
                <strong style="color:#ffffff; font-size:14px;">Yüksek Maruziyet Alarmı</strong>
            </div>
            <p style="font-size:12.5px; color:#cbd5e1; margin:0; line-height:1.5;">
                Ciddi hava kalitesi baskısı. Açık hava aktiviteleri ertelenmeli, iç mekanda hava temizleme çözümleri tercih edilmeli ve zorunlu hallerde uygun filtreli maske (FFP2/N95) değerlendirilmelidir.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # 2. Risk Gruplarına Göre Özel Önlemler
    st.markdown("### Risk Gruplarına Özel Tavsiyeler")

    g1, g2, g3 = st.columns(3)

    with g1:
        st.markdown("""
        <div style="background:#031b2e; border:1px solid #093452; border-radius:10px; padding:18px; height:100%;">
            <div style="font-size:14.5px; font-weight:700; color:#ffffff; margin-bottom:8px;">
                Çocuklar ve Yaşlılar
            </div>
            <p style="font-size:12.5px; color:#cbd5e1; line-height:1.5; margin:0;">
                Akciğer gelişimleri devam eden çocuklar ve bağışıklık rezervi azalan yaşlı bireyler maruziyete karşı daha kırılgandır. Kirlilik seviyelerinin yükseldiği günlerde park ve bahçe aktiviteleri hava kalitesinin daha iyi olduğu saatlere kaydırılmalıdır.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with g2:
        st.markdown("""
        <div style="background:#031b2e; border:1px solid #093452; border-radius:10px; padding:18px; height:100%;">
            <div style="font-size:14.5px; font-weight:700; color:#ffffff; margin-bottom:8px;">
                Kronik Solunum ve Kalp Hastaları
            </div>
            <p style="font-size:12.5px; color:#cbd5e1; line-height:1.5; margin:0;">
                Astım, KOAH ve koroner arter hastaları ani PM maruziyetinde bronş daralması ve tansiyon dengesizliği yaşayabilir. Rutin ilaçların düzenli kullanımı aksatılmamalı ve hekimin acil eylem planı hazır bulundurulmalıdır.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with g3:
        st.markdown("""
        <div style="background:#031b2e; border:1px solid #093452; border-radius:10px; padding:18px; height:100%;">
            <div style="font-size:14.5px; font-weight:700; color:#ffffff; margin-bottom:8px;">
                Açık Havada Çalışanlar ve Sporcular
            </div>
            <p style="font-size:12.5px; color:#cbd5e1; line-height:1.5; margin:0;">
                Ağır fiziksel efor esnasında solunan hava hacmi dakikada 5-10 katına çıkar ve ağız solunumu nedeniyle partiküller doğrudan bronşlara iner. Hassas ve sağlıksız günlerde antrenmanlar kapalı alanlara taşınmalıdır.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # 3. Yöntem ve Kaynak Expander'ı
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    with st.expander("Yöntem ve Kaynaklar"):
        st.markdown("""
        - **Dünya Sağlık Örgütü (WHO):** *Global Air Quality Guidelines (2021)*, Particulate Matter (PM2.5 and PM10), Ozone, Nitrogen Dioxide.
        - **T.C. Sağlık Bakanlığı Halk Sağlığı Genel Müdürlüğü:** *Çevre Sağlığı ve Hava Kirliliğinin Sağlık Etkileri Rehberi*.
        - **Avrupa Çevre Ajansı (EEA):** *Air Quality in Europe & Health Risk Assessments*.
        """)
