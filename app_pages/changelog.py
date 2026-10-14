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
                    v2.2.0 (Mevcut Sürüm)
                </span>
                <strong style="color:#ffffff; font-size:16px;">İl Grupları Modülü, Metodolojik Doğrulama & Terminoloji Nötrleştirmesi</strong>
            </div>
            <span style="color:#94a3b8; font-size:12px;">13 Ekim 2026</span>
        </div>
        <ul style="color:#cbd5e1; font-size:13px; line-height:1.7; margin-left:18px;">
            <li><strong>İl Grupları Modülü:</strong> 81 ilin OSB sayısı ve PM2,5 kirlilik seviyeleri çeyreklik (Q1/Q3) eşiklerine göre gruplandırıldı (Kategori A: Düşük OSB, yüksek PM2,5; Kategori B: Yüksek OSB, yüksek PM2,5; Normal profil).</li>
            <li><strong>Doğrulanamayan Modellerin Kaldırılması:</strong> Hipotetik çarpanlar ve kaynaksız senaryo simülasyonları yürürlükten kaldırılarak veri tabanı saf resmi göstergelere dayandırıldı.</li>
            <li><strong>Menü ve Yönlendirme Mimarisi:</strong> Navigasyon 3 kategori (Keşfet, Analiz, Rehber) ve 12 aktif sayfa olarak standardize edildi; eski sayfa URL'lerine bilgilendirici yönlendirme eklendi.</li>
            <li><strong>Terminoloji Nötrleştirmesi:</strong> Değer yargısı ve kanıtlanmamış nedensellik içeren ifadeler yerine nötr veri tanımları benimsendi.</li>
        </ul>
    </div>

    <div style="background:#021422; border:1px solid #093452; border-radius:10px; padding:20px; margin-bottom:20px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <span style="background:rgba(100,116,139,0.2); color:#94a3b8; font-weight:700; font-size:12px; padding:3px 8px; border-radius:6px; border:1px solid rgba(100,116,139,0.4);">
                    v2.1.0
                </span>
                <strong style="color:#ffffff; font-size:15px;">Arayüz Sadeleştirme, Veri Doğruluğu & Gruplu Navigasyon</strong>
            </div>
            <span style="color:#64748b; font-size:12px;">11 Ekim 2026</span>
        </div>
        <ul style="color:#94a3b8; font-size:12.5px; line-height:1.6; margin-left:18px;">
            <li><strong>Gruplu Navigasyon Mimarisi:</strong> Sol menü mantıksal gruplara ayrıldı ve dinamik kategori motoruna bağlandı.</li>
            <li><strong>Arayüz Temizliği:</strong> Menü ve sayfa başlıklarındaki süs efektleri ve sahte kullanıcı profili arayüzden kaldırıldı.</li>
            <li><strong>Genel Bakış Sayfasının Sadeleştirilmesi:</strong> Hero alanı fotoğraf gürültüsünden arındırılarak kompakt tek satıra indirildi; 7 Bölge grafiği "Bölgeler" sayfasına bağlandı.</li>
            <li><strong>Veri ve Ortalama Doğruluğu:</strong> 4 özet karttaki neyi gösterdiği belirsiz yapay sparkline çizgileri kaldırıldı; "81 ilin ortalaması" başlığı düz aritmetik ortalama olarak netleştirildi. Sıralama sekmesi İlk 10 / En Düşük 10 / Tümü olarak düzenlendi.</li>
            <li><strong>Harita Görünüm ve Sınır İyileştirmesi:</strong> Türkiye haritası SVG sınırları ayarlanarak doğu ve güney illerindeki kırpılma giderildi.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Yöntem ve Kaynaklar"):
        st.markdown("""
        - HavaAtlası GitHub Sürüm Kontrol Sistemi ve Değişiklik Kayıtları.
        - Semantik Sürümleme (SemVer 2.0.0) standardı esas alınmıştır.
        """)
