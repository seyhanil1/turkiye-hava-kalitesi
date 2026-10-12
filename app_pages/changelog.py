"""
Sürüm Notları Sayfası (Changelog)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import streamlit as st
import pandas as pd


def render_changelog_page(df: pd.DataFrame = None):
    """
    Platformun sürüm geçmişi ve yapılan geliştirmelerin şeffaf kayıt günlüğü.
    """
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="margin:0; font-size:24px; font-weight:800; color:#ffffff; letter-spacing:-0.5px;">
            Sürüm Notları ve Değişiklik Günlüğü
        </h2>
        <p style="margin:4px 0 0 0; font-size:13px; color:#cbd5e1;">
            HavaAtlası platformunda gerçekleştirilen arayüz, veri doğruluğu ve mimari güncellemeler.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#031b2e; border:1px solid #00d2ee; border-radius:10px; padding:20px; margin-bottom:20px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <span style="background:rgba(0,210,238,0.15); color:#00d2ee; font-weight:800; font-size:13px; padding:3px 10px; border-radius:6px; border:1px solid rgba(0,210,238,0.4);">
                    v2.1.0 (Mevcut Sürüm)
                </span>
                <strong style="color:#ffffff; font-size:16px;">Arayüz Sadeleştirme, Veri Doğruluğu & Gruplu Navigasyon</strong>
            </div>
            <span style="color:#94a3b8; font-size:12px;">11 Ekim 2026</span>
        </div>
        <ul style="color:#cbd5e1; font-size:13px; line-height:1.7; margin-left:18px;">
            <li><strong>Gruplu Navigasyon Mimarisi:</strong> Sol menü düz listeden çıkarılarak 5 mantıksal gruba (Keşfet, Analiz, Gelecek, Rehber, Güven) ayrıldı ve modern <code>st.navigation</code> motoruna bağlandı.</li>
            <li><strong>Emojilerin ve Süs Efektlerinin Kaldırılması:</strong> Menü ve sayfa başlıklarındaki renkli emojiler kaldırılarak tutarlı tek tip çizgi ikon standardına geçildi. Sol menü altındaki çakışan orman çizimi ve slogan kaldırıldı.</li>
            <li><strong>Sahte Arayüz Öğelerinin Temizlenmesi:</strong> Gerçek bir arkauç sistemi bulunmayan sahte kullanıcı profili hapı ("Ali Altın / HA-81...") ve bildirim zili açılır menüsü arayüzden kaldırıldı.</li>
            <li><strong>Senaryolar Sayfasının Birleştirilmesi:</strong> Yeşil Dönüşüm politika simülatörü ile 2035 Gelecek Yol Ayrımı projeksiyonu tek bir "Senaryolar" sayfasında toplandı.</li>
            <li><strong>Genel Bakış Sayfasının Sadeleştirilmesi:</strong> Hero alanı fotoğraf gürültüsünden arındırılarak kompakt tek satıra indirildi; 7 Bölge grafiği "Bölgeler" sayfasına, gelecek vitrini "Senaryolar" sayfasına taşındı.</li>
            <li><strong>Veri ve Ortalama Doğruluğu:</strong> 4 özet karttaki neyi gösterdiği belirsiz yapay sparkline çizgileri kaldırıldı; "81 ilin ortalaması" başlığı düz aritmetik ortalama olarak netleştirildi. Sıralama tablosundaki anlamsız ok işaretleri kaldırıldı ve sekmeler İlk 10 / En Temiz 10 / Tümü olarak düzenlendi.</li>
            <li><strong>Harita Görünüm ve Sınır İyileştirmesi:</strong> Türkiye haritası SVG sınırları ayarlanarak doğu ve güney illerindeki kırpılma giderildi; 7 referans il etiketi yarı saydam okunabilir arka planla sabitlendi.</li>
            <li><strong>Referans ve Şeffaflık Sayfaları:</strong> Sağlık Rehberi, Sözlük, Veri ve Yöntem ile Sürüm Notları sayfaları yayına alındı.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Yöntem ve Kaynaklar"):
        st.markdown("""
        - HavaAtlası GitHub Sürüm Kontrol Sistemi ve Değişiklik Kayıtları.
        - Semantik Sürümleme (SemVer 2.0.0) standardı esas alınmıştır.
        """)
