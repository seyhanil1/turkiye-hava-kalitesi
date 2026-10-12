"""
Sözlük Sayfası (Kavramlar ve Kısaltmalar)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import html
import streamlit as st
import pandas as pd


def render_glossary_page(df: pd.DataFrame = None):
    """
    Hava kalitesi, epidemiyoloji ve atmosfer modellemesinde kullanılan temel kavramlar,
    birimler ve kurum kısaltmaları için sade, kurumsal ve tarafsız referans sözlüğü.
    """
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <span style="background: rgba(0, 210, 238, 0.15); color: #00d2ee; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; border: 1px solid rgba(0, 210, 238, 0.3);">
                METODOLOJİ & REFERANS
            </span>
            <span style="font-size: 12px; color: #8faec9;">Uluslararası Standartlar</span>
        </div>
        <h2 style="margin:0; font-size:24px; font-weight:800; color:#ffffff; letter-spacing:-0.5px;">
            Hava Kalitesi ve Çevre Sözlüğü
        </h2>
        <p style="margin:4px 0 0 0; font-size:13px; color:#cbd5e1;">
            Platformda kullanılan teknik terimler, kirletici tanımları ve DSÖ hava kalitesi standartları kılavuzu.
        </p>
    </div>
    """, unsafe_allow_html=True)

    terms = [
        {
            "term": "PM2.5 (İnce Partikül Madde)",
            "cat": "Kirletici",
            "desc": "Çapı 2,5 mikrometre veya daha küçük ince partikül maddelerdir (saç telinin yaklaşık 30'da biri). Akciğer alveollerine ve doğrudan kan dolaşımına nüfuz edebildiği için halk sağlığı açısından en tehlikeli hava kirleticisidir."
        },
        {
            "term": "SO₂ (Kükürt Dioksit)",
            "cat": "Gaz Kirletici",
            "desc": "Yüksek kükürtlü kömür ve fuel-oil yakılması sonucu oluşan, asit yağmurlarına yol açan boğucu gazdır."
        },
        {
            "term": "O₃ (Yer Seviyesi Ozon / Troposferik Ozon)",
            "cat": "İkincil Kirletici",
            "desc": "Doğrudan bacadan veya egzozdan salınmaz; güneş ışığı altında azot oksitler (NOx) ve uçucu organik bileşiklerin (VOC) fotokimyasal tepkimesiyle oluşur. Şiddetli akciğer tahrişine ve solunum fonksiyon kaybına neden olur."
        },
        {
            "term": "CO (Karbon Monoksit)",
            "cat": "Gaz Kirletici",
            "desc": "Fosil yakıtların ve biyokütlenin yetersiz oksijenle eksik yanması sonucu açığa çıkan renksiz, kokusuz ve tatsız zehirli bir gazdır. Kandaki hemoglobine bağlanarak dokulara oksijen taşınmasını engeller."
        },
        {
            "term": "µg/m³ (Mikrogram / Metreküp)",
            "cat": "Ölçü Birimi",
            "desc": "Bir metreküp havadaki kirletici kütlesini gösteren standart konsantrasyon birimidir. 1 mikrogram, bir gramın 10⁻⁶ katına (1/1.000.000 g) eşittir."
        },
        {
            "term": "DSÖ Kılavuz Değeri (WHO Guideline Value)",
            "cat": "Standart",
            "desc": "Dünya Sağlık Örgütü'nün (WHO 2021) geniş epidemiyolojik kanıtlara dayanarak belirlediği ve sağlık risklerini minimize etmeyi hedefleyen eşik değerdir. PM2.5 için yıllık kılavuz 5 µg/m³, 24 saatlik kılavuz 15 µg/m³'tür. DSÖ, PM2.5 için risksiz bir güvenli alt sınır bulunmadığını belirtir."
        },
        {
            "term": "DSÖ Ara Hedefleri (Interim Targets 1 - 4)",
            "cat": "Standart",
            "desc": "Mevcut hava kalitesi kılavuz değerlerine hemen ulaşamayan ülkelerin kademeli iyileşme sağlamaları amacıyla DSÖ tarafından tanımlanan geçiş hedefleridir. Örneğin PM2.5 için Ara Hedef-1 yıllık 35 µg/m³, Ara Hedef-2 25 µg/m³, Ara Hedef-3 15 µg/m³, Ara Hedef-4 10 µg/m³'tür."
        },
        {
            "term": "24 Saatlik vs. Yıllık Ortalama",
            "cat": "İstatistik",
            "desc": "24 saatlik ortalama, gün içindeki akut maruziyeti ve kısa vadeli kirlilik piklerini değerlendirmek için kullanılır (kılavuz: 15 µg/m³). Yıllık ortalama ise uzun vadeli kronik maruziyetin kalp ve akciğer sağlığı üzerindeki kümülatif etkisini değerlendirir (kılavuz: 5 µg/m³)."
        },
        {
            "term": "Sıcaklık İnversiyonu (Sıcaklık Terselmesi)",
            "cat": "Meteoroloji",
            "desc": "Normalde yükseklikle azalan hava sıcaklığının, soğuk hava kütlesinin çanak topografyaya çökmesiyle yükseldikçe artması durumudur. Tavan vazifesi gören sıcak hava tabakası kirleticilerin dikey dağılımını engelleyerek şehir merkezinde hapsolmasına yol açar."
        },
        {
            "term": "CAMS (Copernicus Atmosphere Monitoring Service)",
            "cat": "Veri Kaynağı",
            "desc": "Avrupa Birliği Copernicus programı kapsamında Avrupa Orta Vadeli Hava Tahminleri Merkezi (ECMWF) tarafından işletilen küresel atmosfer gözlem ve modelleme sistemidir. Uydu ölçümleri, yer istasyonları ve atmosferik kimya modellerini birleştirerek 0.1° (~11 km) çözünürlükte reanaliz ve tahmin verisi üretir."
        },
        {
            "term": "ÇŞİDB (T.C. Çevre, Şehircilik ve İklim Değişikliği Bakanlığı)",
            "cat": "Kurum",
            "desc": "Türkiye'de Ulusal Hava Kalitesi İzleme Ağı'nı (UHKİM) işleten, yer ölçüm istasyonları kuran ve emisyon izinlerini düzenleyen resmi kamu otoritesidir."
        },
        {
            "term": "HavaAtlası Operasyonel Kademeleri (5 Düzey)",
            "cat": "Sınıflandırma",
            "desc": "Platformda kullanılan 5 düzeyli karşılaştırmalı ölçek: İyi (≤15 µg/m³), Orta (15,1 - 30 µg/m³), Hassas (30,1 - 50 µg/m³), Sağlıksız (50,1 - 70 µg/m³), Kritik (>70 µg/m³). DSÖ 24 saatlik kılavuz değeri ve ara hedefleri referans alınarak 81 ilin tamamını kapsayacak şekilde yapılandırılmıştır."
        }
    ]

    # Arama kutusu - tekil key verilerek kararlı tutulur
    search = st.text_input(
        "Sözlükte Terim Ara:",
        placeholder="Örn: PM2.5, SO2, DSÖ, CAMS, birim...",
        label_visibility="collapsed",
        key="glossary_search_query"
    )

    filtered = terms
    if search:
        s_lower = search.strip().lower()
        filtered = [
            t for t in terms
            if s_lower in t["term"].lower() or s_lower in t["desc"].lower() or s_lower in t["cat"].lower()
        ]

    # React DOM Reconciliation çökmesini (insertBefore hatası) önlemek için:
    # Birden çok döngüsel st.markdown yerine tek bir HTML bloğu halinde render edilir
    cards_container = st.container()
    with cards_container:
        if not filtered:
            st.info("Aranan terim bulunamadı.")
        else:
            cards_html = []
            for item in filtered:
                esc_term = html.escape(item["term"])
                esc_cat = html.escape(item["cat"])
                esc_desc = html.escape(item["desc"])
                card_markup = (
                    f'<div style="background: rgba(3, 27, 46, 0.7); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); '
                    f'border: 1px solid rgba(0, 210, 238, 0.22); border-radius: 10px; padding: 16px 20px; margin-bottom: 14px; '
                    f'box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);">'
                    f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">'
                    f'<strong style="color: #ffffff; font-size: 15px; font-weight: 700;">{esc_term}</strong>'
                    f'<span style="background: rgba(0, 210, 238, 0.12); color: #00d2ee; font-size: 11px; font-weight: 700; '
                    f'padding: 3px 10px; border-radius: 6px; border: 1px solid rgba(0, 210, 238, 0.3);">{esc_cat}</span>'
                    f'</div>'
                    f'<p style="font-size: 13.5px; color: #cbd5e1; margin: 0; line-height: 1.6;">{esc_desc}</p>'
                    f'</div>'
                )
                cards_html.append(card_markup)

            st.markdown(f'<div id="glossary-items">{"".join(cards_html)}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    with st.expander("Yöntem ve Kaynaklar"):
        st.markdown("""
        - **WHO (2021):** *WHO Global Air Quality Guidelines: Particulate matter (PM2.5 and PM10), ozone, nitrogen dioxide, sulfur dioxide and carbon monoxide.*
        - **Copernicus Atmosphere Monitoring Service (CAMS):** *ECMWF Global Atmospheric Composition Reanalysis Documentation.*
        - **T.C. Çevre, Şehircilik ve İklim Değişikliği Bakanlığı:** *Hava Kalitesi Değerlendirme ve Yönetimi Yönetmeliği (HKDYY).*
        """)
