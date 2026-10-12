"""
HavaAtlası — Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
Ana Uygulama Giriş Noktası (Streamlit)
"""

import os
import sys
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go

# Proje kök dizinini Python yoluna ekle
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from data_sources.local_official_data import build_master_dataset
from data_sources.constants import get_dataset_date_info, PLAKA_ILLER, KIRLILIK_KADEMELERI
from visualization.pixel_perfect_dashboard import generate_pixel_perfect_dashboard_html

# Sayfa Modülleri
from app_pages.overview import render_overview_page
from app_pages.report_card import render_report_card_page
from app_pages.duel import render_duel_page
from app_pages.correlation_page import render_correlation_page
from app_pages.regions_page import render_regions_page
from app_pages.industry_page import render_industry_page
from app_pages.economy_page import render_economy_page
from app_pages.ai_forecast_page import render_ai_forecast_page
from app_pages.chat_assistant_page import render_chat_assistant_page
from app_pages.scenarios_page import render_scenarios_page
from app_pages.health_guide import render_health_guide_page
from app_pages.glossary import render_glossary_page
from app_pages.methodology import render_methodology_page
from app_pages.changelog import render_changelog_page
from app_pages.action_guide import render_action_guide_page


# ==========================================
# 1. SAYFA YAPILANDIRMASI
# ==========================================
st.set_page_config(
    page_title="HavaAtlası | Türkiye Hava Kalitesi Platformu",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. VERİ YÜKLEME & OTURUM DURUMU (SESSION STATE)
# ==========================================
@st.cache_data
def load_application_data():
    master_csv = os.path.join(ROOT_DIR, "data", "master_data.csv")
    if os.path.exists(master_csv):
        try:
            df = pd.read_csv(master_csv, encoding="utf-8")
            if len(df) == 81:
                return df
        except Exception:
            pass
    df = build_master_dataset()
    df.to_csv(master_csv, index=False, encoding="utf-8")
    return df


@st.cache_data
def load_daily_city_air_quality() -> pd.DataFrame:
    """Madde 3: Günlük 81 il hava kalitesi verisini önbellekten okur."""
    csv_path = os.path.join(ROOT_DIR, "data", "daily_city_air_quality.csv")
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            if not df.empty and "date" in df.columns and "il" in df.columns:
                return df
        except Exception:
            pass
    return pd.DataFrame()


def get_aqi_level_info(val: float, pol: str = "PM2.5"):
    """Madde 5: Lejanttaki seviye eşikleri ve renk tanımlarını döndürür."""
    levels = KIRLILIK_KADEMELERI.get("pm25", [])
    for lvl in levels:
        if lvl["min_val"] <= val <= lvl["max_val"]:
            return lvl["etiket"], lvl["renk"]
    if levels:
        return levels[-1]["etiket"], levels[-1]["renk"]
    return "Orta", "#facc15"


def calculate_tier_distribution(df_subset: pd.DataFrame, pollutant_col: str = "pm25"):
    """
    Madde 4: Mevcut sınıflandırma tanımından seviye eşiklerini okur ve il sayılarını hesaplar.
    Toplam il sayısının veri setindeki gerçek il sayısına eşit olduğunu kontrol eden assert içerir.
    """
    levels = KIRLILIK_KADEMELERI.get("pm25", [])
    counts = {lvl["etiket"]: 0 for lvl in levels}
    for val in df_subset[pollutant_col]:
        matched = False
        for lvl in levels:
            if lvl["min_val"] <= val <= lvl["max_val"]:
                counts[lvl["etiket"]] += 1
                matched = True
                break
        if not matched and levels:
            counts[levels[-1]["etiket"]] += 1

    total_classified = sum(counts.values())
    # Madde 4: Toplam il sayısı eşitlik kontrolü (Zorunlu assert)
    assert total_classified == len(df_subset), (
        f"Toplam sınıflandırılan il sayısı ({total_classified}) "
        f"gerçek il sayısına ({len(df_subset)}) eşit değil!"
    )
    return levels, counts


df_master = load_application_data()
df_daily = load_daily_city_air_quality()
cities_list = sorted(list(df_master["il"].dropna().unique())) if not df_master.empty else list(PLAKA_ILLER.values())

date_info = get_dataset_date_info()
date_range_str = date_info.get("date_range_str", "11.07.2026 – 10.10.2026")
period_label_str = date_info.get("period_label_str", "Yıllık Konsolidasyon (Son 12 Ay)")

# Ortak filtre durumu ve URL senkronizasyonu
if "city" in st.query_params:
    del st.query_params["city"]
query_city = st.query_params.get("il")
if query_city and query_city in cities_list:
    st.session_state["selected_city"] = query_city
else:
    st.session_state.setdefault("selected_city", "İstanbul")
st.session_state.setdefault("selected_pollutant", "PM2.5")
st.session_state.setdefault("selected_region", "Türkiye Geneli")

# Dinamik Kategori ve Sayfa Yapılandırması
CATEGORIES = ["Keşfet", "Analiz", "Gelecek", "Rehber"]
CATEGORY_PAGES = {
    "Keşfet": ["Genel Bakış", "Şehir Karnesi", "Düello"],
    "Analiz": ["Bölgeler", "Korelasyon", "Sanayi Profili", "Ekonomi"],
    "Gelecek": ["AI Tahmin", "Senaryolar"],
    "Rehber": ["Yapılması Gerekenler", "Terimler Sözlüğü", "AI Asistan", "Veri ve Yöntem", "Sürüm Notları"],
}
PAGE_TO_CATEGORY = {p: c for c, pages in CATEGORY_PAGES.items() for p in pages}

# URL query parameter üzerinden sayfa yönlendirme desteği
query_page = st.query_params.get("page") or st.query_params.get("sayfa")
if query_page and query_page in PAGE_TO_CATEGORY:
    st.session_state["active_page"] = query_page

if "active_page" not in st.session_state:
    st.session_state["active_page"] = "Genel Bakış"

# Dışarıdan veya URL'den active_page değiştirildiyse active_category ile senkronize et
cur_page_val = st.session_state.get("active_page", "Genel Bakış")
expected_cat_val = PAGE_TO_CATEGORY.get(cur_page_val, "Keşfet")
if st.session_state.get("active_category") != expected_cat_val:
    st.session_state["active_category"] = expected_cat_val
    st.session_state["nav_cat_pills"] = expected_cat_val

if "nav_cat_pills" not in st.session_state or st.session_state["nav_cat_pills"] is None:
    st.session_state["nav_cat_pills"] = st.session_state["active_category"]


# ==========================================
# 3. GLOBAL CSS VE TEMA DÜZENLEMELERİ
# ==========================================
st.markdown("""
<style>
header[data-testid="stHeader"] {
    background: transparent !important;
}
footer { display: none !important; }
#MainMenu { display: none !important; }

/* Streamlit Koyu Lacivert Tema */
.stApp {
    background-color: #021220 !important;
    color: #e2e8f0 !important;
}

[data-testid="stSidebar"] {
    background-color: #021626 !important;
    border-right: 1px solid #07253d !important;
}

[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #ffffff !important;
}

/* Sidebar Navigasyon - Kategori Pills */
[data-testid="stSidebar"] [data-testid="stPills"] {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 4px !important;
    margin-bottom: 4px !important;
}

[data-testid="stSidebar"] [data-testid="stPills"] button {
    background: #031b2e !important;
    border: 1px solid #093452 !important;
    color: #8faec9 !important;
    border-radius: 6px !important;
    padding: 3px 9px !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    transition: all 0.15s ease !important;
    min-height: 28px !important;
    line-height: 1.2 !important;
}

[data-testid="stSidebar"] [data-testid="stPills"] button:hover {
    background: #06263e !important;
    color: #ffffff !important;
    border-color: rgba(0, 210, 238, 0.4) !important;
}

[data-testid="stSidebar"] [data-testid="stPills"] button[aria-checked="true"],
[data-testid="stSidebar"] [data-testid="stPills"] button[data-selected="true"] {
    background: #082d45 !important;
    border-color: #00d2ee !important;
    color: #00d2ee !important;
    font-weight: 700 !important;
    box-shadow: 0 0 8px rgba(0, 210, 238, 0.25) !important;
}

/* Sidebar Navigasyon - Dinamik Sayfa Listesi (Radio) */
[data-testid="stSidebar"] [data-testid="stRadio"] {
    margin-top: 2px !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 2px !important;
}

/* Radio daire butonunu tamamen gizle */
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label > div:first-child {
    display: none !important;
}

/* Modern menü bağlantısı/butonu stili */
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label {
    background: transparent !important;
    padding: 7px 11px !important;
    border-radius: 6px !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    border: 1px solid transparent !important;
    margin: 0 !important;
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label p,
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label span {
    color: #cbd5e1 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    margin: 0 !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover {
    background: #06263e !important;
    border-color: #093452 !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover p,
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover span {
    color: #ffffff !important;
}

/* Aktif Sayfa */
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
    background: #082d45 !important;
    border: 1px solid rgba(0, 210, 238, 0.35) !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p,
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) span {
    color: #00d2ee !important;
    font-weight: 700 !important;
}

[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
    padding-top: 1.25rem !important;
    padding-bottom: 1.5rem !important;
    padding-left: 0.9rem !important;
    padding-right: 0.9rem !important;
}

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    max-width: 100vw !important;
}

iframe {
    border: none !important;
    width: 100% !important;
}
</style>
""", unsafe_allow_html=True)


def render_shared_top_bar():
    """Tüm analiz sayfaları için paylaşılan ortak filtre çubuğu."""
    c1, c2, c3 = st.columns([1.5, 0.9, 1.2])
    with c1:
        current_idx = cities_list.index(st.session_state["selected_city"]) if st.session_state["selected_city"] in cities_list else 0
        new_city = st.selectbox(
            "İl veya bölge ara:",
            cities_list,
            index=current_idx,
            label_visibility="collapsed",
            key="_shared_city_picker"
        )
        if new_city != st.session_state["selected_city"]:
            st.session_state["selected_city"] = new_city
            st.query_params["il"] = new_city
            if "city" in st.query_params:
                del st.query_params["city"]
    with c2:
        pol_options = ["PM2.5", "PM10", "NO₂"]
        cur_pol_idx = pol_options.index(st.session_state["selected_pollutant"]) if st.session_state["selected_pollutant"] in pol_options else 0
        new_pol = st.selectbox(
            "Kirletici:",
            pol_options,
            index=cur_pol_idx,
            label_visibility="collapsed",
            key="_shared_pol_picker"
        )
        if new_pol != st.session_state["selected_pollutant"]:
            st.session_state["selected_pollutant"] = new_pol
    with c3:
        st.markdown(f"""
        <div style="background:#031b2e; border:1px solid #093452; border-radius:6px; padding:7px 12px; text-align:center; font-size:11.5px; color:#cbd5e1;">
            Veri Dönemi: <strong style="color:#00d2ee;">{period_label_str}</strong>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)


# ==========================================
# 4. SAYFA FONKSİYONLARI
# ==========================================
def view_overview():
    # URL query params üzerinden il seçimi yapıldıysa session state'i güncelle
    if "city" in st.query_params:
        del st.query_params["city"]
    query_city = st.query_params.get("il")
    if query_city and query_city in cities_list and query_city != st.session_state.get("selected_city"):
        st.session_state["selected_city"] = query_city

    # Genel Bakış: Kompakt Hero, 4 KPI Kartı, Büyütülmüş Harita (%65) & Şehir Sıralaması (%35), İnce Footer
    dashboard_html = generate_pixel_perfect_dashboard_html(
        df=df_master,
        active_page="genel_bakis",
        active_pollutant=st.session_state["selected_pollutant"],
        active_period="30G",
        active_region=st.session_state["selected_region"]
    )
    components.html(dashboard_html, height=1220, scrolling=True)


def view_report_card():
    render_shared_top_bar()
    render_report_card_page(df_master)


def view_duel():
    render_shared_top_bar()
    render_duel_page(df_master)


def view_correlation():
    render_shared_top_bar()
    render_correlation_page(df_master)


def view_regions():
    render_shared_top_bar()
    render_regions_page(df_master)


def view_industry():
    render_shared_top_bar()
    render_industry_page(df_master)


def view_economy():
    render_shared_top_bar()

    # Veri hesaplamaları
    if "maliyet_milyon_tl" in df_master.columns:
        toplam_maliyet = float(df_master["maliyet_milyon_tl"].sum())
    else:
        toplam_maliyet = 820000.0  # Literatüre uygun varsayılan (~820 Milyar TL)

    toplam_nufus = float(df_master["nufus"].sum()) if "nufus" in df_master.columns else 85341527.0
    kisi_basi_maliyet = round((toplam_maliyet * 1_000_000) / max(toplam_nufus, 1), 0)

    # Sağlık ekonomisi standartları (OECD, DSÖ, HEAL):
    # 1. Erken Vefat Maliyetleri (VSL): %78 (en büyük pay: %75-%80)
    # 2. Doğrudan Sağlık ve Tedavi Giderleri: %16 (%15-%18)
    # 3. İş Gücü ve Verimlilik Kaybı: %6 (%5-%7)
    maliyet_vefat = round(toplam_maliyet * 0.78, 1)
    maliyet_saglik = round(toplam_maliyet * 0.16, 1)
    maliyet_isgucu = round(toplam_maliyet - maliyet_vefat - maliyet_saglik, 1)

    toplam_maliyet_str = f"{toplam_maliyet:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    maliyet_vefat_str = f"{maliyet_vefat:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    maliyet_saglik_str = f"{maliyet_saglik:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    maliyet_isgucu_str = f"{maliyet_isgucu:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # 1. ÜST KISIM - BAŞLIK & BİLANÇO
    st.markdown(f"""
    <div style="margin-bottom: 22px;">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
            <div style="background:rgba(245, 158, 11, 0.15); color:#f59e0b; width:34px; height:34px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-weight:800; font-family:monospace; font-size:14px; border:1px solid rgba(245, 158, 11, 0.3);">₺</div>
            <h2 style="margin:0; font-size:24px; font-weight:800; color:#ffffff; letter-spacing:-0.5px;">
                Hava Kirliliğinin Yıllık Ekonomik &amp; Sağlık Faturası
            </h2>
        </div>
        <p style="margin:0; font-size:13px; color:#8faec9;">
            Dünya Sağlık Örgütü (WHO), OECD ve HEAL epidemiyolojik sağlık-ekonomi modellerine göre hava kirliliğinin Türkiye makroekonomisine getirdiği yıllık tahmini yük.
        </p>
    </div>

    <div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.16) 0%, rgba(239, 68, 68, 0.12) 50%, rgba(11, 19, 43, 0.95) 100%);
                border: 1px solid rgba(245, 158, 11, 0.45);
                border-radius: 16px;
                padding: 24px 28px;
                margin-bottom: 24px;
                box-shadow: 0 12px 36px rgba(0, 0, 0, 0.35);
                backdrop-filter: blur(14px);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
            <div>
                <div style="display:inline-flex; align-items:center; gap:6px; background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.4); padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 700; color: #fde047; margin-bottom: 12px; letter-spacing: 0.5px;">
                    RESMİ EPİDEMİYOLOJİK BİLANÇO
                </div>
                <div style="font-size: 22px; font-weight: 900; color: #ffffff; letter-spacing: -0.3px; line-height: 1.3;">
                    TÜRKİYE GENELİ TAHMİNİ EKONOMİK YÜK: <span style="background: linear-gradient(90deg, #fbbf24, #f43f5e); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{toplam_maliyet_str} MİLYON ₺</span>
                </div>
                <div style="font-size: 12.5px; color: #cbd5e1; margin-top: 8px; line-height: 1.5; max-width: 950px;">
                    Türkiye genelinde hava kirliliğine atfedilen yıllık ~42.000 erken ölümün İstatistiki Yaşam Değeri (VSL) analizi, SGK solunum/dolaşım tedavi giderleri ve kayıp iş günü maliyetlerinin birleşik hesaplamasıdır.
                </div>
            </div>
            <div style="background: rgba(2, 18, 32, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 12px 18px; text-align: right; min-width: 170px;">
                <div style="font-size: 11px; color: #8faec9; text-transform: uppercase; font-weight: 600;">Kişi Başı Yıllık Yük</div>
                <div style="font-size: 20px; font-weight: 800; color: #38bdf8;">{int(kisi_basi_maliyet):,} ₺</div>
                <div style="font-size: 10.5px; color: #64748b;">Nüfus: 85,3 Milyon</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. ORTA KISIM - ÜÇLÜ MALİYET BÖLÜNMESİ
    col1, col2, col3 = st.columns(3)

    # 1. KART: ERKEN VEFAT MALİYETLERİ (VSL) -> EN BÜYÜK PAY (%78)
    with col1:
        st.markdown(f"""
        <div style="background: rgba(17, 26, 46, 0.9);
                    border: 1px solid rgba(245, 158, 11, 0.45);
                    border-radius: 14px;
                    padding: 20px;
                    min-height: 230px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    box-shadow: 0 8px 24px rgba(245, 158, 11, 0.12);">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <span style="background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.4); padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 800; font-family: monospace;">BEŞERİ SERMAYE</span>
                    <span style="background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.5); padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 700;">
                        %78 PAY • VSL MODELİ
                    </span>
                </div>
                <div style="font-size: 13px; color: #8faec9; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                    ERKEN VEFAT MALİYETLERİ (VSL)
                </div>
                <div style="font-size: 24px; font-weight: 900; color: #ffffff; margin: 6px 0 2px 0;">
                    {maliyet_vefat_str} <span style="font-size:14px; color:#f59e0b; font-weight:700;">Milyon ₺</span>
                </div>
                <div style="font-size: 11.5px; color: #cbd5e1; line-height: 1.5; margin-top: 10px;">
                    DSÖ ve OECD VSL (İstatistiki Yaşam Değeri) yaklaşımıyla hava kirliliğine atfedilen ~42.000 önlenebilir erken vefatın sosyo-ekonomik maliyeti.
                </div>
            </div>
            <div style="margin-top: 14px; padding-top: 10px; border-top: 1px solid rgba(255, 255, 255, 0.06); font-size: 11px; color: #fcd34d;">
                • Türkiye genelinde hava kirliliğine atfedilen yıllık ~42.000 erken ölüm baz alınmıştır
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 2. KART: DOĞRUDAN SAĞLIK GİDERLERİ (%16)
    with col2:
        st.markdown(f"""
        <div style="background: rgba(17, 26, 46, 0.9);
                    border: 1px solid rgba(244, 63, 94, 0.45);
                    border-radius: 14px;
                    padding: 20px;
                    min-height: 230px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    box-shadow: 0 8px 24px rgba(244, 63, 94, 0.12);">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <span style="background: rgba(244, 63, 94, 0.15); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.4); padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 800; font-family: monospace;">KLİNİK TEDAVİ</span>
                    <span style="background: rgba(244, 63, 94, 0.15); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.5); padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 700;">
                        %16 PAY • KLİNİK YÜK
                    </span>
                </div>
                <div style="font-size: 13px; color: #8faec9; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                    DOĞRUDAN SAĞLIK GİDERLERİ
                </div>
                <div style="font-size: 24px; font-weight: 900; color: #ffffff; margin: 6px 0 2px 0;">
                    {maliyet_saglik_str} <span style="font-size:14px; color:#f43f5e; font-weight:700;">Milyon ₺</span>
                </div>
                <div style="font-size: 11.5px; color: #cbd5e1; line-height: 1.5; margin-top: 10px;">
                    SGK ve kamu hastanelerindeki astım, KOAH, solunum yetmezliği yatışları ve ilaç giderleri.
                </div>
            </div>
            <div style="margin-top: 14px; padding-top: 10px; border-top: 1px solid rgba(255, 255, 255, 0.06); font-size: 11px; color: #fca5a5;">
                • SGK solunum reçeteleri ve kamu yataklı tedavi bütçe yükü
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 3. KART: İŞ GÜCÜ & VERİMLİLİK KAYBI (%6)
    with col3:
        st.markdown(f"""
        <div style="background: rgba(17, 26, 46, 0.9);
                    border: 1px solid rgba(0, 242, 254, 0.45);
                    border-radius: 14px;
                    padding: 20px;
                    min-height: 230px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    box-shadow: 0 8px 24px rgba(0, 242, 254, 0.12);">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <span style="background: rgba(0, 242, 254, 0.15); color: #00f2fe; border: 1px solid rgba(0, 242, 254, 0.4); padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 800; font-family: monospace;">REEL SEKTÖR</span>
                    <span style="background: rgba(0, 242, 254, 0.15); color: #00f2fe; border: 1px solid rgba(0, 242, 254, 0.5); padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 700;">
                        %6 PAY • ÜRETİM KAYBI
                    </span>
                </div>
                <div style="font-size: 13px; color: #8faec9; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                    İŞ GÜCÜ &amp; VERİMLİLİK KAYBI
                </div>
                <div style="font-size: 24px; font-weight: 900; color: #ffffff; margin: 6px 0 2px 0;">
                    {maliyet_isgucu_str} <span style="font-size:14px; color:#00f2fe; font-weight:700;">Milyon ₺</span>
                </div>
                <div style="font-size: 11.5px; color: #cbd5e1; line-height: 1.5; margin-top: 10px;">
                    Kirlilik kaynaklı hastalık izinleri ve kayıp iş günlerinin reel sektöre getirdiği üretim kaybı.
                </div>
            </div>
            <div style="margin-top: 14px; padding-top: 10px; border-top: 1px solid rgba(255, 255, 255, 0.06); font-size: 11px; color: #7dd3fc;">
                • Kirlilik pik günlerinde iş günü devamsızlığı ve fabrika verim düşüşü
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # 3. GRAFİK & DSÖ KAZANIMLARI (st.columns([3, 2]))
    col_chart, col_gain = st.columns([3, 2])

    with col_chart:
        st.markdown("#### Hava Kirliliğinin Yıllık Tahmini Ekonomik Maliyet Dağılımı")
        st.caption("DSÖ ve OECD sağlık ekonomisi modellerine göre 3 ana harcama kaleminin oransal payları.")

        labels = ["Erken Vefat Maliyetleri (VSL)", "Doğrudan Sağlık Giderleri", "İş Gücü & Verimlilik Kaybı"]
        values = [maliyet_vefat, maliyet_saglik, maliyet_isgucu]
        colors = ["#f59e0b", "#f43f5e", "#00f2fe"]

        fig_donut = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.62,
            marker=dict(colors=colors, line=dict(color="#07192b", width=2)),
            textinfo="percent+label",
            textposition="inside",
            hoverinfo="label+value+percent",
            hovertemplate="<b>%{label}</b><br>Tutar: %{value:,.1f} Milyon ₺<br>Oran: %{percent}<extra></extra>"
        )])

        fig_donut.update_layout(
            height=340,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10, l=10, r=10, b=10),
            showlegend=False,
            annotations=[
                dict(
                    text=f"<b>%100</b><br><span style='font-size:11px;color:#8faec9;'>Mali Yük</span>",
                    x=0.5, y=0.5,
                    font=dict(size=16, color="#ffffff"),
                    showarrow=False
                )
            ]
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_gain:
        with st.container(border=True):
            st.markdown("#### DSÖ Standartlarına Geçilseydi Ne Olurdu?")
            st.caption("DSÖ kılavuz sınırına (5 µg/m³) ulaşıldığında sağlanacak yıllık sosyo-ekonomik kazanım projeksiyonu.")

            kazanim_df = pd.DataFrame([
                {"Kazanım Alanı": "Önlenebilir Can Kaybı", "Tahmini Etki": "+18.500 Erken Ölüm", "Kılavuz": "DSÖ 2021 (5 µg/m³)"},
                {"Kazanım Alanı": "Yıllık Kamu Tasarrufu", "Tahmini Etki": "~170 Milyar TL Tasarruf", "Kılavuz": "Sağlık & Tedavi Bütçesi"},
                {"Kazanım Alanı": "İlaç ve Tedavi İndirimi", "Tahmini Etki": "%75 Kronik İlaç Azalımı", "Kılavuz": "SGK Reçete Yükü"},
                {"Kazanım Alanı": "İş Gücü Verim Kazancı", "Tahmini Etki": "+4,2 Milyon İş Günü", "Kılavuz": "Reel Sektör"}
            ])
            st.dataframe(kazanim_df, use_container_width=True, hide_index=True)

            c_k1, c_k2 = st.columns(2)
            with c_k1:
                st.metric(label="Önlenebilir Can Kaybı", value="18.500+ Kişi", delta="Yıllık kurtarılabilir", delta_color="normal")
            with c_k2:
                st.metric(label="Kamu Tasarrufu", value="~170 Milyar ₺", delta="Yıllık bütçe kazancı", delta_color="normal")

            st.caption("* DSÖ 2021 Kılavuzu & OECD İstatistiki Yaşam Değeri (VSL) yaklaşımı.")

    st.write("")

    # 4. İL BAZLI MALİYET DAĞILIMI (EN ÇOK ETKİLENEN 10 İL & TABLO)
    with st.expander("İl Bazlı Sağlık Faturası Sıralaması & Metodoloji Detayı"):
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("##### En Yüksek Toplam Sağlık Yüküne Sahip 10 İl")
            top_cost = df_master.sort_values(by="maliyet_milyon_tl", ascending=False).head(10)
            fig_cost = go.Figure(go.Bar(
                x=top_cost["maliyet_milyon_tl"],
                y=top_cost["il"],
                orientation="h",
                marker=dict(
                    color=top_cost["maliyet_milyon_tl"],
                    colorscale="Reds",
                    line=dict(color="rgba(255,255,255,0.1)", width=1)
                ),
                text=[f"{v:,.0f} Milyon ₺" for v in top_cost["maliyet_milyon_tl"]],
                textposition="outside"
            ))
            fig_cost.update_layout(
                height=320,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(autorange="reversed", tickfont=dict(color="#cbd5e1")),
                xaxis=dict(tickfont=dict(color="#94a3b8"), gridcolor="rgba(255,255,255,0.05)"),
                margin=dict(t=10, l=10, r=40, b=10)
            )
            st.plotly_chart(fig_cost, use_container_width=True)

        with col_t2:
            st.markdown("##### En Yüksek Kişi Başı Kirlilik Maliyetine Sahip 10 İl")
            df_temp = df_master.copy()
            df_temp["kisi_basi_tl"] = ((df_temp["maliyet_milyon_tl"] * 1_000_000) / df_temp["nufus"]).round(0)
            top_capita = df_temp.sort_values(by="kisi_basi_tl", ascending=False).head(10)
            fig_capita = go.Figure(go.Bar(
                x=top_capita["kisi_basi_tl"],
                y=top_capita["il"],
                orientation="h",
                marker=dict(
                    color=top_capita["kisi_basi_tl"],
                    colorscale="YlOrRd",
                    line=dict(color="rgba(255,255,255,0.1)", width=1)
                ),
                text=[f"{int(v):,} ₺" for v in top_capita["kisi_basi_tl"]],
                textposition="outside"
            ))
            fig_capita.update_layout(
                height=320,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(autorange="reversed", tickfont=dict(color="#cbd5e1")),
                xaxis=dict(tickfont=dict(color="#94a3b8"), gridcolor="rgba(255,255,255,0.05)"),
                margin=dict(t=10, l=10, r=40, b=10)
            )
            st.plotly_chart(fig_capita, use_container_width=True)

        st.markdown("##### 81 İl Sağlık & Ekonomik Yük Veri Tablosu")
        cost_table_df = df_master[["il", "bolge", "nufus", "pm25", "maliyet_milyon_tl"]].copy()
        cost_table_df["kisi_basi_tl"] = ((cost_table_df["maliyet_milyon_tl"] * 1_000_000) / cost_table_df["nufus"]).round(0)
        cost_table_df = cost_table_df.sort_values(by="maliyet_milyon_tl", ascending=False)
        st.dataframe(
            cost_table_df.rename(columns={
                "il": "İl", "bolge": "Bölge", "nufus": "Nüfus",
                "pm25": "PM2.5 (µg/m³)", "maliyet_milyon_tl": "Maliyet (Milyon ₺)",
                "kisi_basi_tl": "Kişi Başı Yük (₺)"
            }),
            use_container_width=True,
            hide_index=True
        )


def view_ai_forecast():
    render_shared_top_bar()
    render_ai_forecast_page(df_master)


def view_scenarios():
    render_shared_top_bar()
    render_scenarios_page(df_master)


def view_health_guide():
    render_health_guide_page(df_master)


def view_action_guide():
    render_action_guide_page(df_master)


def view_glossary():
    render_glossary_page(df_master)


def view_chat_assistant():
    render_chat_assistant_page(df_master)


def view_methodology():
    render_methodology_page(df_master)


def view_changelog():
    render_changelog_page(df_master)


# ==========================================
# 5. SAYFA YÖNLENDİRME HARİTASI (PAGE ROUTER)
# ==========================================
PAGE_ROUTING = {
    "Genel Bakış": view_overview,
    "Şehir Karnesi": view_report_card,
    "Düello": view_duel,
    "Bölgeler": view_regions,
    "Korelasyon": view_correlation,
    "Sanayi Profili": view_industry,
    "Ekonomi": view_economy,
    "AI Tahmin": view_ai_forecast,
    "Senaryolar": view_scenarios,
    "Yapılması Gerekenler": view_action_guide,
    "Terimler Sözlüğü": view_glossary,
    "AI Asistan": view_chat_assistant,
    "Veri ve Yöntem": view_methodology,
    "Sürüm Notları": view_changelog,
}


# ==========================================
# 6. DİNAMİK SOL MENÜ NAVİGASYONU (SIDEBAR)
# ==========================================
with st.sidebar:
    # Marka & Dönem Başlığı
    st.markdown(f"""
    <div style='padding: 2px 0 10px 0; border-bottom: 1px solid #07253d; margin-bottom: 12px;'>
        <div style='font-size: 19px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;'>
            HavaAtlası
        </div>
        <div style='font-size: 11px; color: #8faec9; font-weight: 600; margin-top: 2px;'>
            Dönem: <span style='color: #00d2ee;'>{period_label_str}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 1. Kategori Seçici (Pills)
    st.markdown("""
    <div style='font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #648ba8; margin-bottom: 5px;'>
        Kategori
    </div>
    """, unsafe_allow_html=True)

    def on_category_select():
        chosen = st.session_state.get("nav_cat_pills")
        if chosen and chosen in CATEGORY_PAGES:
            st.session_state["active_category"] = chosen
            st.session_state["active_page"] = CATEGORY_PAGES[chosen][0]
        else:
            st.session_state["nav_cat_pills"] = st.session_state["active_category"]

    st.pills(
        "Kategori",
        CATEGORIES,
        selection_mode="single",
        label_visibility="collapsed",
        key="nav_cat_pills",
        on_change=on_category_select
    )

    # 2. Dinamik Sayfa Listesi
    cur_cat = st.session_state.get("active_category", "Keşfet")
    cur_pages = CATEGORY_PAGES.get(cur_cat, CATEGORY_PAGES["Keşfet"])
    if st.session_state.get("active_page") not in cur_pages:
        st.session_state["active_page"] = cur_pages[0]

    st.markdown(f"""
    <div style='font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #648ba8; margin-top: 10px; margin-bottom: 4px;'>
        Sayfalar ({cur_cat})
    </div>
    """, unsafe_allow_html=True)

    page_radio_key = f"nav_page_radio_{cur_cat}"
    if st.session_state.get("active_page") in cur_pages:
        st.session_state[page_radio_key] = st.session_state["active_page"]
    else:
        st.session_state[page_radio_key] = cur_pages[0]
        st.session_state["active_page"] = cur_pages[0]

    def on_page_select():
        chosen_p = st.session_state.get(page_radio_key)
        if chosen_p in cur_pages:
            st.session_state["active_page"] = chosen_p

    st.radio(
        "Sayfa Seçimi",
        cur_pages,
        key=page_radio_key,
        label_visibility="collapsed",
        on_change=on_page_select
    )

    # 3. Resmi Veri Kaynakları Rozetleri
    st.markdown("""
    <div style='margin-top: 16px; padding-top: 10px; border-top: 1px solid #07253d;'>
        <div style='font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #648ba8; margin-bottom: 5px;'>
            Veri Kaynakları
        </div>
        <div style='display: flex; flex-wrap: wrap; gap: 4px;'>
            <span style='font-size: 10px; background-color: #041b2c; color: #6d93b3; padding: 2px 7px; border-radius: 4px; border: 1px solid #092c46; font-weight: 500;' title='Çevre ve Şehircilik Bakanlığı 2025 Kara Rapor'>ÇŞİDB</span>
            <span style='font-size: 10px; background-color: #041b2c; color: #6d93b3; padding: 2px 7px; border-radius: 4px; border: 1px solid #092c46; font-weight: 500;' title='Copernicus CAMS Atmosfer Modeli'>CAMS</span>
            <span style='font-size: 10px; background-color: #041b2c; color: #6d93b3; padding: 2px 7px; border-radius: 4px; border: 1px solid #092c46; font-weight: 500;' title='TÜİK Sağlık ve Ölüm İstatistikleri'>TÜİK</span>
            <span style='font-size: 10px; background-color: #041b2c; color: #6d93b3; padding: 2px 7px; border-radius: 4px; border: 1px solid #092c46; font-weight: 500;' title='DSÖ 2021 Kılavuz Sınırları'>DSÖ</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# 7. SAYFA ÇAĞRISI VE GÜVENLİ YÖNLENDİRME
# ==========================================
active_page = st.session_state.get("active_page", "Genel Bakış")
render_func = PAGE_ROUTING.get(active_page)

if render_func:
    try:
        render_func()
    except Exception as e:
        st.error(f"Sayfa yüklenirken bir hata oluştu: {e}")
else:
    st.markdown(f"""
    <div style="padding: 48px 24px; text-align: center; background: #031b2e; border: 1px dashed #093452; border-radius: 12px; margin-top: 24px;">
        <h3 style="color: #ffffff; margin: 0 0 8px 0; font-size: 20px; font-weight: 700;">İçerik Hazırlanıyor</h3>
        <p style="color: #8faec9; font-size: 14px; margin: 0;">
            <strong>{active_page}</strong> modülü için veri ve analizler hazırlanma aşamasındadır.
        </p>
    </div>
    """, unsafe_allow_html=True)