"""
UI Bileşenleri, Özel CSS ve Kart Render Yardımcıları
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import streamlit as st
from typing import Optional

def render_custom_css():
    """
    Ekran görüntüsündeki lüks karanlık analitik dashboard hissini
    sağlayan modern CSS stillerini ekler.
    """
    st.markdown("""
    <style>
    /* Ana Font ve Gövde */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #070c18 !important;
        color: #e2e8f0;
    }
    
    /* Yan Menü (Sidebar) */
    section[data-testid="stSidebar"] {
        background-color: #09101f !important;
        border-right: 1px solid #1e293b !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.3);
    }
    
    /* Metrik Kartları */
    .metric-card {
        background: linear-gradient(180deg, #101c38 0%, #0b1326 100%);
        border: 1px solid rgba(56, 189, 248, 0.22);
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.05);
        transition: transform 0.2s ease, border-color 0.2s ease;
        margin-bottom: 12px;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.5);
        box-shadow: 0 8px 24px -2px rgba(56, 189, 248, 0.15);
    }
    
    .metric-label {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    
    .metric-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.2;
    }
    
    .metric-unit {
        font-size: 0.95rem;
        font-weight: 500;
        color: #64748b;
        margin-left: 4px;
    }
    
    .metric-delta {
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 6px;
        display: inline-block;
        padding: 2px 8px;
        border-radius: 6px;
    }
    
    .delta-positive {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
    }
    
    .delta-negative {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
    }
    
    .delta-neutral {
        background: rgba(148, 163, 184, 0.15);
        color: #cbd5e1;
    }
    
    /* Veri Bilimi Yorum Kutusu */
    .insight-box {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.08) 0%, rgba(16, 185, 129, 0.05) 100%);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-left: 4px solid #38bdf8;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 16px 0;
    }
    
    .insight-title {
        font-size: 1rem;
        font-weight: 700;
        color: #38bdf8;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .insight-content {
        font-size: 0.9rem;
        color: #cbd5e1;
        line-height: 1.6;
    }
    
    /* Hızlı Erişim Kartları */
    .quick-card {
        background: #0f192e;
        border: 1px solid #1e2e4a;
        border-radius: 12px;
        padding: 16px;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .quick-card:hover {
        background: #152342;
        border-color: #38bdf8;
        transform: translateY(-2px);
    }
    
    .quick-title {
        font-weight: 700;
        font-size: 0.95rem;
        color: #f8fafc;
        margin-bottom: 4px;
    }
    
    .quick-desc {
        font-size: 0.8rem;
        color: #94a3b8;
    }
    
    /* Üst Bar Rozeti */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    /* Başlık Vurguları */
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #f8fafc;
        margin-bottom: 4px;
    }
    
    .hero-title span {
        color: #38bdf8;
        text-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
    }
    
    .hero-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

def render_metric_card(
    title: str, 
    value: str, 
    unit: str = "", 
    delta: Optional[str] = None, 
    delta_type: str = "neutral"
):
    """
    Şık, neon kenarlıklı analitik metrik kartı render eder.
    """
    delta_html = ""
    if delta:
        delta_class = f"delta-{delta_type}"
        delta_html = f'<div class="metric-delta {delta_class}">{delta}</div>'
        
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{title}</div>
        <div class="metric-value">{value}<span class="metric-unit">{unit}</span></div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def render_quick_cards():
    """
    Ana ekrandaki Şehir Karnesi, Korelasyon, DSÖ Sınırları ve Yeşil Dönüşüm
    hızlı erişim kartlarını 4 sütunda gösterir.
    """
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div class="quick-card">
            <div class="quick-title">🏙️ Şehir Karnesi</div>
            <div class="quick-desc">81 ilin detaylı hava, sanayi ve solunum karnesi</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="quick-card">
            <div class="quick-title">🧮 Korelasyon</div>
            <div class="quick-desc">Sanayi, nüfus, araç ve sağlık ilişkileri matrisi</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="quick-card">
            <div class="quick-title">🛡️ DSÖ Sınırları</div>
            <div class="quick-desc">WHO 2021 kılavuz değerleri ve aşım analizleri</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class="quick-card">
            <div class="quick-title">🌱 Yeşil Dönüşüm</div>
            <div class="quick-desc">Bölgesel temiz hava endeksi ve yeşil skorlar</div>
        </div>
        """, unsafe_allow_html=True)
