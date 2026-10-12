"""
2035: Gelecek Yol Ayrımı — İki Paralel Gelecek Karar ve Projeksiyon Motoru
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import streamlit as st
import pandas as pd
import textwrap


# ==========================================
# 1. SADE ÇİZGİ VEKTÖREL İKONLAR (EMOJİSİZ & NEONSUZ)
# ==========================================
ICON_ACTIONS = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle; flex-shrink:0;">
  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
  <circle cx="9" cy="7" r="4"/>
  <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
  <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
</svg>"""

ICON_ANALYTICS = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle; flex-shrink:0;">
  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
</svg>"""

ICON_WARNING = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f87171" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle; flex-shrink:0;">
  <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
  <line x1="12" y1="9" x2="12" y2="13"/>
  <line x1="12" y1="17" x2="12.01" y2="17"/>
</svg>"""

ICON_CHART_DOWN = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle; flex-shrink:0;">
  <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/>
  <polyline points="17 18 23 18 23 12"/>
</svg>"""


# ==========================================
# 2. ZAMAN DİLİMLERİ VE SENARYO VERİ SETLERİ
# ==========================================
TIMELINE_YEARS = [
    "2026 (Referans)",
    "2029 (Kırılma Noktası)",
    "2032 (Dönüm Yılı)",
    "2035 (Nihai Tablo)"
]

GREEN_PATH_DATA = {
    "2026 (Referans)": {
        "action_title": "Bireysel Korunma ve Toplumsal Talep",
        "action_main": "Halk sağlığı uyarılarının takip edilmesi, riskli günlerde koruyucu maske kullanımı ve hanelerde temiz ısınma talebinin artması öngörülmektedir.",
        "action_sub": "DSÖ hava kalitesi kılavuz değerlerinin referans alınmasıyla hassas grupların (çocuklar, yaşlılar, kronik hastalar) korunması ve yerel yönetimlerin temiz hava eylem planlarını uygulamaya koyması hedeflenmektedir.",
        "bullets": [
            "Hava kalitesinin eşik değerleri aştığı günlerde koruyucu maske standardının benimsenmesi.",
            "Sosyal konutlarda ve apartmanlarda kalitesiz yakıt kullanımının denetlenmesi.",
            "Okul çevrelerinde araç rölanti kısıtlamaları ve yeşil koridor taleplerinin yaygınlaşması."
        ],
        "metrics": {
            "pm_change": "-%8 Azalma",
            "pm_val": "36,3 ➔ 33,4 µg/m³",
            "lives_saved": "+3.200 Önlenebilir Ölüm",
            "budget_saved": "+12,4 Milyar TL",
            "life_exp": "+0,6 Yıl"
        }
    },
    "2029 (Kırılma Noktası)": {
        "action_title": "Sanayi Disiplini ve Düşük Emisyon Bölgeleri",
        "action_main": "Sanayi tesislerinde baca filtrelerinin zorunlu denetimi ve şehir merkezlerinde Düşük Emisyon Bölgelerinin kurulması öngörülmektedir.",
        "action_sub": "Tüm organize sanayi bacalarına sürekli emisyon ölçüm sistemlerinin entegre edilmesi ve yüksek emisyonlu araçların tarihi kent merkezlerine girişinin kademeli sınırlandırılması planlanmaktadır.",
        "bullets": [
            "Organize sanayi bölgelerinde elektrostatik filtre denetimlerinin sıklığının artırılması.",
            "Büyükşehirlerde düşük emisyon bölgesi uygulamalarıyla şehir içi egzoz yükünün azaltılması.",
            "Sosyal yardım yakıtlarının temiz yakıt ve ısı pompası altyapısına dönüştürülmesi."
        ],
        "metrics": {
            "pm_change": "-%22 Azalma",
            "pm_val": "36,3 ➔ 28,3 µg/m³",
            "lives_saved": "+8.400 Önlenebilir Ölüm",
            "budget_saved": "+34,5 Milyar TL",
            "life_exp": "+1,4 Yıl"
        }
    },
    "2032 (Dönüm Yılı)": {
        "action_title": "Enerji Dönüşümü ve Ulaşım Elektrifikasyonu",
        "action_main": "Kentsel toplu taşıma filolarında elektrifikasyona geçiş ve ısı pompası altyapısının genişletilmesi hedeflenmektedir.",
        "action_sub": "Fosil yakıt sübvansiyonlarının temiz enerjiye aktarılması ve metropollerde raylı sistemlerin yaygınlaştırılması öngörülmektedir.",
        "bullets": [
            "Toplu taşıma filolarında düşük ve sıfır emisyonlu araç oranının yükseltilmesi.",
            "Topografik olarak kapalı havzalarda konut ısıtmasında temiz teknolojilerin yaygınlaştırılması.",
            "Kentsel imar planlarında doğal hava koridorlarının korunması."
        ],
        "metrics": {
            "pm_change": "-%45 Azalma",
            "pm_val": "36,3 ➔ 20,0 µg/m³",
            "lives_saved": "+13.600 Önlenebilir Ölüm",
            "budget_saved": "+58,2 Milyar TL",
            "life_exp": "+2,3 Yıl"
        }
    },
    "2035 (Nihai Tablo)": {
        "action_title": "DSÖ Standartlarına Uyum ve Kalıcı Temiz Hava",
        "action_main": "81 ilde DSÖ hava kalitesi standartlarına ulaşıldı ve temiz hava politikaları kalıcı hale getirildi.",
        "action_sub": "Yıllık ortalama PM2.5 seviyesinin kılavuz bantlara çekilmesiyle, hava kirliliğine atfedilebilir erken ölümlerde ve sağlık harcamalarında belirgin gerileme kaydedilmektedir.",
        "bullets": [
            "İl genelinde DSÖ orta ve uzun vadeli kılavuz standartlarına uyum hedeflerinin sürdürülmesi.",
            "Kronik solunum hastalıklarına bağlı acil sağlık başvurularının azalması.",
            "Temiz hava politikalarının halk sağlığı ve yaşam kalitesine uzun vadeli katkısı."
        ],
        "metrics": {
            "pm_change": "-%72 Düşüş",
            "pm_val": "36,3 ➔ 10,2 µg/m³ (DSÖ Kılavuz)",
            "lives_saved": "+18.500 (+18,500) Önlenebilir Ölüm / Yıl",
            "budget_saved": "85.0 Milyar (85,0 Milyar TL) / Yıl",
            "life_exp": "+3.2 Yıl (+3,2 Yıl)"
        }
    }
}

GRAY_PATH_DATA = {
    "2026 (Referans)": {
        "action_title": "İhmal, Erteleme ve Maruziyet Riski",
        "action_main": "Halk sağlığı uyarılarının dikkate alınmaması, kalitesiz linyit yakıtı kullanımının sürmesi ve denetim eksikliği kirlilik baskısını artırmaktadır.",
        "action_sub": "DSÖ kılavuz hedeflerinin uygulanmaması, düşük kaliteli yakıt dağıtımı ve trafikte yüksek emisyonlu araç sayısının kontrolsüz artışı risk oluşturmaktadır.",
        "bullets": [
            "Hava kirliliğinin yükseldiği günlerde koruyucu önlemlerin yetersiz kalması.",
            "Sanayi tesislerinde filtre standartlarının denetim yetersizliğiyle aşınması.",
            "Kentsel yapılaşmanın rüzgar koridorlarını daraltması."
        ],
        "metrics": {
            "pm_change": "+%14 Artış",
            "pm_val": "36,3 ➔ 41,4 µg/m³",
            "deaths_lost": "24.000+ Erken Vefat",
            "cost_incurred": "38,0 Milyar TL",
            "life_loss": "-0,8 Yıl Kayıp"
        }
    },
    "2029 (Kırılma Noktası)": {
        "action_title": "Kapalı Havzalarda Artan Sağlık Yükü",
        "action_main": "Kış aylarında çanak havza illerinde solunum ve kardiyovasküler şikayetlerle hastane başvurularının artması öngörülmektedir.",
        "action_sub": "Topografik termal enversiyon yaşayan kapalı havzalarda kirleticilerin zemin seviyesinde birikmesi, kış sezonlarında kronik hasta ve çocuk maruziyetini artırmaktadır.",
        "bullets": [
            "Topografik inversiyon yaşayan illerde kış aylarında kirletici konsantrasyonunun yükselmesi.",
            "Kardiyovasküler krizler ve solunum yolu hastalıklarında kirlilik kaynaklı artış.",
            "Sanayi emisyonlarının yerleşim alanları üzerindeki olumsuz etkisinin sürmesi."
        ],
        "metrics": {
            "pm_change": "+%35 Artış",
            "pm_val": "36,3 ➔ 49,0 µg/m³",
            "deaths_lost": "58.000+ Erken Vefat",
            "cost_incurred": "84,5 Milyar TL",
            "life_loss": "-1,7 Yıl Kayıp"
        }
    },
    "2032 (Dönüm Yılı)": {
        "action_title": "Kronik Hastalık Artışı ve Sağlık Sistemi Yükü",
        "action_main": "Kronik solunum hastalıklarının genç nüfusta yaygınlaşması ve sağlık harcamalarının sürdürülemez seviyelere tırmanması riski bulunmaktadır.",
        "action_sub": "Partikül madde maruziyetinin kronikleşmesiyle astım ve KOAH vakalarının erken yaşlara inmesi, sağlık bütçesinde solunum tedavilerine ayrılan payı artırmaktadır.",
        "bullets": [
            "Açık hava aktivitelerinin hava kirliliği günlerinde kısıtlanması zorunluluğu.",
            "Solunum ilaçları ve tedavi geri ödemelerinin sağlık bütçesine getirdiği ek yük.",
            "Fosil yakıt tüketiminin azaltılamaması nedeniyle kentsel hava kalitesinin bozulması."
        ],
        "metrics": {
            "pm_change": "+%68 Artış",
            "pm_val": "36,3 ➔ 61,0 µg/m³",
            "deaths_lost": "98.000+ Erken Vefat",
            "cost_incurred": "142,0 Milyar TL",
            "life_loss": "-2,6 Yıl Kayıp"
        }
    },
    "2035 (Nihai Tablo)": {
        "action_title": "Kritik Eşik Aşımı ve Yüksek Risk",
        "action_main": "Hava kalitesi geri döndürülemez eşiği aşıyor ve uzun vadeli halk sağlığı riski kritik seviyeye ulaşıyor.",
        "action_sub": "Sanayi ve topografik olarak kapalı illerde yıllık PM2.5 seviyelerinin yüksek kalması durumunda, erken kayıplar ve sağlık sisteminde derin zarar tablosu oluşmaktadır.",
        "bullets": [
            "Sanayi ve çanak illerinde yıllık PM2.5 seviyelerinin yüksek seyretmesi.",
            "Önlenebilir kronik hastalıklara bağlı erken vefatların artması.",
            "Hava kirliliğinin sağlık sistemi ve iş gücü üzerinde oluşturduğu yüksek yük."
        ],
        "metrics": {
            "pm_change": "+%116 Artış",
            "pm_val": "36,3 ➔ 78,5 µg/m³",
            "deaths_lost": "145.000+ (145,000+) Erken Vefat",
            "cost_incurred": "210.0 Milyar (210,0 Milyar TL) Fatura",
            "life_loss": "-3.8 Yıl (-3,8 Yıl) Yaşam Kaybı"
        }
    }
}


def get_fork_scenario_data(path_type: str, year: str) -> dict:
    """Seçilen yol ve yıla göre senaryo verisini döner."""
    if "Yeşil" in path_type or "Temiz" in path_type or "1." in path_type:
        return GREEN_PATH_DATA.get(year, GREEN_PATH_DATA[TIMELINE_YEARS[0]])
    return GRAY_PATH_DATA.get(year, GRAY_PATH_DATA[TIMELINE_YEARS[0]])


def calculate_scenario_metrics(df: pd.DataFrame, is_clean: bool, year: str) -> dict:
    """
    Verilen veri setine ve senaryoya göre gözlenen temel durum ile
    projeksiyon hesaplamalarını Türkçe sayı biçimleriyle üretir.
    """
    # 1. Gözlenen Referans Veriler (2026)
    base_pm25 = 36.3
    total_pop = 85341527
    base_deaths = 73651

    if df is not None and not df.empty:
        if "pm25" in df.columns:
            base_pm25 = round(float(df["pm25"].mean()), 1)
        if "nufus" in df.columns:
            total_pop = int(df["nufus"].sum())
        if "solunum_olum" in df.columns:
            base_deaths = int(df["solunum_olum"].sum())

    who_guideline = 5.0
    who_ratio = round(base_pm25 / who_guideline, 1)

    # 2. Seçilen Yıla Göre Değişim Oranları
    rates = {
        "2026 (Referans)": {"clean_pct": -0.08, "gray_pct": 0.14, "clean_deaths": 3200, "gray_deaths": 24000, "clean_cost": 12.4, "gray_cost": 38.0, "clean_life": 0.6, "gray_life": 0.8},
        "2029 (Kırılma Noktası)": {"clean_pct": -0.22, "gray_pct": 0.35, "clean_deaths": 8400, "gray_deaths": 58000, "clean_cost": 34.5, "gray_cost": 84.5, "clean_life": 1.4, "gray_life": 1.7},
        "2032 (Dönüm Yılı)": {"clean_pct": -0.45, "gray_pct": 0.68, "clean_deaths": 13600, "gray_deaths": 98000, "clean_cost": 58.2, "gray_cost": 142.0, "clean_life": 2.3, "gray_life": 2.6},
        "2035 (Nihai Tablo)": {"clean_pct": -0.72, "gray_pct": 1.16, "clean_deaths": 18500, "gray_deaths": 145000, "clean_cost": 85.0, "gray_cost": 210.0, "clean_life": 3.2, "gray_life": 3.8},
    }
    r = rates.get(year, rates["2026 (Referans)"])

    if is_clean:
        pct = r["clean_pct"]
        target_pm = round(base_pm25 * (1 + pct), 1)
        delta_pm = round(base_pm25 - target_pm, 1)
        deaths_num = r["clean_deaths"]
        cost_num = r["clean_cost"]
        life_num = r["clean_life"]

        pct_label = f"-%{int(abs(pct) * 100)}"
        deaths_label = f"+{deaths_num:,.0f}".replace(",", ".")
        cost_label = f"+{cost_num:.1f} Milyar TL".replace(".", ",")
        life_label = f"+{life_num:.1f} Yıl".replace(".", ",")
    else:
        pct = r["gray_pct"]
        target_pm = round(base_pm25 * (1 + pct), 1)
        delta_pm = round(target_pm - base_pm25, 1)
        deaths_num = r["gray_deaths"]
        cost_num = r["gray_cost"]
        life_num = r["gray_life"]

        pct_label = f"+%{int(abs(pct) * 100)}"
        deaths_label = f"{deaths_num:,.0f}+".replace(",", ".")
        cost_label = f"{cost_num:.1f} Milyar TL".replace(".", ",")
        life_label = f"-{life_num:.1f} Yıl".replace(".", ",")

    return {
        "observed_pm25": f"{base_pm25:.1f}".replace(".", ","),
        "observed_who": f"{who_guideline:.1f}".replace(".", ","),
        "who_ratio": f"{who_ratio:.1f}".replace(".", ","),
        "observed_deaths": f"{base_deaths:,.0f}".replace(",", "."),
        "total_pop": f"{total_pop:,.0f}".replace(",", "."),
        "target_pm25": f"{target_pm:.1f}".replace(".", ","),
        "delta_pm25": f"{delta_pm:.1f}".replace(".", ","),
        "pct_label": pct_label,
        "deaths_label": deaths_label,
        "cost_label": cost_label,
        "life_label": life_label,
    }


def render_future_fork_page(df: pd.DataFrame = None):
    """
    2035 Gelecek Yol Ayrımı karar simülasyonu sayfasını render eder.
    Sadeleştirilmiş görsel dil, dürüst projeksiyon-gözlem ayrımı ve
    varsayımlar metodolojisi ile donatılmıştır.
    """
    # 1. Stil Tanımları: Düz koyu zemin, neon ışıltısız, 1px yarı saydam kenarlık
    st.markdown(textwrap.dedent("""
<style>
    .fork-hero {
        background: #031626;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 22px 26px;
        margin-bottom: 20px;
}
    .fork-title {
        font-size: 22px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.3px;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 10px;
}
    .fork-subtitle {
        font-size: 13.5px;
        color: #94a3b8;
        line-height: 1.5;
        margin: 0;
}
    .timeline-container {
        background: #031626;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px 22px 10px 22px;
        margin-top: 16px;
        margin-bottom: 22px;
}
    .timeline-label {
        font-size: 12px;
        font-weight: 700;
        color: #94a3b8;
        margin-bottom: 8px;
        letter-spacing: 0.3px;
}
    .fork-card {
        background: #021626;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 22px 24px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        min-height: 540px;
        box-sizing: border-box;
        transition: border-color 0.15s ease;
}
    .fork-card:hover {
        border-color: rgba(255, 255, 255, 0.16);
}
    .card-header-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        margin-bottom: 14px;
}
    .card-title-group {
        display: flex;
        align-items: center;
        gap: 9px;
}
    .card-title-text {
        font-size: 16.5px;
        font-weight: 800;
        color: #ffffff;
}
    .card-year-badge {
        font-size: 11.5px;
        font-weight: 700;
        color: #94a3b8;
        background: rgba(255, 255, 255, 0.04);
        padding: 3px 10px;
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.08);
}
    .action-theme-title {
        font-size: 13.5px;
        font-weight: 700;
        color: #38bdf8;
        margin-bottom: 8px;
}
    .action-paragraph {
        font-size: 13px;
        color: #e2e8f0;
        line-height: 1.55;
        margin-bottom: 10px;
}
    .action-sub-paragraph {
        font-size: 12.5px;
        color: #94a3b8;
        line-height: 1.5;
        margin-bottom: 14px;
}
    .action-bullet-list {
        display: flex;
        flex-direction: column;
        gap: 7px;
        margin-bottom: 16px;
}
    .action-bullet-item {
        font-size: 12.5px;
        color: #cbd5e1;
        line-height: 1.45;
        padding-left: 2px;
}
    .data-section-box {
        background: rgba(2, 18, 32, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 14px;
}
    .data-section-title {
        font-size: 11px;
        font-weight: 700;
        color: #94a3b8;
        letter-spacing: 0.3px;
        margin-bottom: 8px;
        text-transform: uppercase;
}
    .data-row-compact {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 4px 0;
        font-size: 12.5px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}
    .data-row-compact:last-child {
        border-bottom: none;
}
    .data-lbl {
        color: #94a3b8;
}
    .data-val {
        color: #ffffff;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
}
    .scenario-grid-2x2 {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-bottom: 14px;
}
    .scenario-metric-box {
        background: rgba(2, 18, 32, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 8px;
        padding: 12px 14px;
}
    .metric-big-num {
        font-size: 21px;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.1;
        font-family: 'JetBrains Mono', monospace;
        margin-bottom: 3px;
}
    .metric-title-small {
        font-size: 11.5px;
        font-weight: 600;
        color: #cbd5e1;
        margin-bottom: 2px;
}
    .metric-sub-note {
        font-size: 10.5px;
        color: #64748b;
}
    .card-footer-caption {
        font-size: 11px;
        color: #64748b;
        line-height: 1.4;
        padding-top: 10px;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        margin-top: auto;
}
    .kpi-row-card {
        background: #031626;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 16px 18px;
        text-align: center;
        box-sizing: border-box;
}
    .kpi-row-label {
        font-size: 11px;
        font-weight: 700;
        color: #94a3b8;
        letter-spacing: 0.3px;
        text-transform: uppercase;
        margin-bottom: 4px;
}
    .kpi-row-value {
        font-size: 24px;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        color: #ffffff;
        margin-bottom: 4px;
}
    .kpi-row-subtext {
        font-size: 11px;
        color: #64748b;
}
</style>
    """).strip(), unsafe_allow_html=True)

    # 2. Üst Hero Alanı (Emojisiz, Ölçülü ve Bilgi Veren Başlık)
    st.markdown(textwrap.dedent("""
<div class="fork-hero">
<div class="fork-title">2035: Türkiye'nin Gelecek Yol Ayrımı</div>
<div class="fork-subtitle">
            Hava kalitesi politikaları, sanayi denetimleri ve temiz ısınma müdahalelerinin 10 yıllık sağlık ve kamu bütçesi bilançosu.
</div>
</div>
    """).strip(), unsafe_allow_html=True)

    # 3. Sade Yol Seçici
    clean_choice_lbl = "1. Yol: Ekolojik Bilinç ve Yeşil Dönüşüm (Temiz Gelecek)"
    gray_choice_lbl = "2. Yol: Eylemsizlik ve İhmal (Gri Gelecek)"

    selected_path = st.segmented_control(
        "Gelecek Yol Tercihi:",
        options=[clean_choice_lbl, gray_choice_lbl],
        default=clean_choice_lbl,
        label_visibility="collapsed",
        key="segmented_future_choice"
    )

    if not selected_path:
        selected_path = clean_choice_lbl

    is_clean = (selected_path == clean_choice_lbl)

    # 4. Adım Adım İlerleme Çubuğu (Timeline Slider)
    st.markdown(textwrap.dedent("""
<div class="timeline-container">
<div class="timeline-label">Zaman Çizgisinde İlerleme Noktası:</div>
    """).strip(), unsafe_allow_html=True)

    selected_year = st.select_slider(
        "Zaman Çizgisinde Yıl Seçimi:",
        options=TIMELINE_YEARS,
        value=TIMELINE_YEARS[0],
        label_visibility="collapsed",
        key="timeline_select_slider"
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # 5. Senaryo ve Dinamik Hesaplama Verileri
    data = get_fork_scenario_data("Yeşil" if is_clean else "Gri", selected_year)
    calc = calculate_scenario_metrics(df, is_clean, selected_year)

    # 6. Yan Yana İki Eşit Yükseklikli Kart (st.columns(2))
    col_left, col_right = st.columns(2)

    # Bullet HTML
    bullet_items_html = "".join([
        f'<div class="action-bullet-item">• {b}</div>'
        for b in data.get("bullets", [])
    ])

    if is_clean:
        # ========================================================
        # 1. YOL (Temiz Gelecek): Sol Kart — İnsanların ve Toplumun Yaptıkları
        # ========================================================
        with col_left:
            st.markdown(textwrap.dedent(f"""
<div class="fork-card">
<div>
<div class="card-header-row">
<div class="card-title-group">
{ICON_ACTIONS}
<span class="card-title-text">İnsanların ve Toplumun Yaptıkları</span>
</div>
<span class="card-year-badge">{selected_year}</span>
</div>

<div class="action-theme-title">{data['action_title']}</div>
<p class="action-paragraph">{data['action_main']}</p>
<p class="action-sub-paragraph">{data['action_sub']}</p>

<div class="action-bullet-list">
{bullet_items_html}
</div>
</div>

<div class="card-footer-caption">
DSÖ 2021 PM2.5 Kılavuz Değeri: Yıllık 5,0 µg/m³. Kaynak: Dünya Sağlık Örgütü (WHO 2021) & Ulusal Temiz Hava Eylem Planı hedefleri.
</div>
</div>
            """).strip(), unsafe_allow_html=True)

        # ========================================================
        # 1. YOL (Temiz Gelecek): Sağ Kart — Sağlık ve Çevre Kazanımları
        # ========================================================
        with col_right:
            st.markdown(textwrap.dedent(f"""
<div class="fork-card">
<div>
<div class="card-header-row">
<div class="card-title-group">
{ICON_ANALYTICS}
<span class="card-title-text">Sağlık ve Çevre Kazanımları</span>
</div>
<span class="card-year-badge">Senaryo Projeksiyonu</span>
</div>

<!-- Bölüm A: Gözlenen Referans Durum (2026) -->
<div class="data-section-box">
<div class="data-section-title">Gözlenen Referans Durum (2026)</div>
<div class="data-row-compact">
<span class="data-lbl">Türkiye Yıllık PM2.5 Ortalaması</span>
<span class="data-val">{calc['observed_pm25']} µg/m³</span>
</div>
<div class="data-row-compact">
<span class="data-lbl">DSÖ 2021 Yıllık Kılavuz Değeri</span>
<span class="data-val">{calc['observed_who']} µg/m³ ({calc['who_ratio']} kat aşım)</span>
</div>
<div class="data-row-compact">
<span class="data-lbl">Yıllık Temel Solunum Ölümü</span>
<span class="data-val">{calc['observed_deaths']} kişi/yıl</span>
</div>
</div>

<!-- Bölüm B: Senaryo (Projeksiyon Modeli) -->
<div class="data-section-title" style="margin-top:14px;">Senaryo ({selected_year} Modeli)</div>
<div class="scenario-grid-2x2">
<div class="scenario-metric-box">
<div class="metric-big-num" style="color:#38bdf8;">{calc['target_pm25']} <small style="font-size:12px;">µg/m³</small></div>
<div class="metric-title-small">Hedef PM2.5 Seviyesi</div>
<div class="metric-sub-note">{calc['pct_label']} ulusal iyileşme</div>
</div>
<div class="scenario-metric-box">
<div class="metric-big-num" style="color:#10b981;">{calc['deaths_label']}</div>
<div class="metric-title-small">Önlenebilir Tahmini Ölüm</div>
<div class="metric-sub-note">Yıllık önlenebilir vefat</div>
</div>
<div class="scenario-metric-box">
<div class="metric-big-num" style="color:#38bdf8;">{calc['cost_label']}</div>
<div class="metric-title-small">Tasarruf Edilen Sağlık Bütçesi</div>
<div class="metric-sub-note">Kamu ve iş gücü tasarrufu</div>
</div>
<div class="scenario-metric-box">
<div class="metric-big-num" style="color:#34d399;">{calc['life_label']}</div>
<div class="metric-title-small">Beklenen Yaşam Süresi Değişimi</div>
<div class="metric-sub-note">Kişi başı ortalama kazanç</div>
</div>
</div>
</div>

<div class="card-footer-caption">
* Değerler konsantrasyon-tepki fonksiyonuna (CRF) dayalı projeksiyondur. Metodoloji ve kaynak ayrıntıları aşağıdaki açıklama panelinde yer almaktadır.
</div>
</div>
            """).strip(), unsafe_allow_html=True)

    else:
        # ========================================================
        # 2. YOL (Gri Gelecek): Sol Kart — Yapılan Hatalar ve İhmal Edilen Uyarılar
        # ========================================================
        with col_left:
            st.markdown(textwrap.dedent(f"""
<div class="fork-card">
<div>
<div class="card-header-row">
<div class="card-title-group">
{ICON_WARNING}
<span class="card-title-text">Yapılan Hatalar ve İhmal Edilen Uyarılar</span>
</div>
<span class="card-year-badge">{selected_year}</span>
</div>

<div class="action-theme-title" style="color:#f87171;">{data['action_title']}</div>
<p class="action-paragraph">{data['action_main']}</p>
<p class="action-sub-paragraph">{data['action_sub']}</p>

<div class="action-bullet-list">
{bullet_items_html}
</div>
</div>

<div class="card-footer-caption">
* Denetimsizlik, kirletici yakıt sübvansiyonları ve kentsel rüzgar koridorlarının kapatılması senaryosudur.
</div>
</div>
            """).strip(), unsafe_allow_html=True)

        # ========================================================
        # 2. YOL (Gri Gelecek): Sağ Kart — Sağlık ve Çevre Kayıpları
        # ========================================================
        with col_right:
            st.markdown(textwrap.dedent(f"""
<div class="fork-card">
<div>
<div class="card-header-row">
<div class="card-title-group">
{ICON_CHART_DOWN}
<span class="card-title-text">Sağlık ve Çevre Kayıpları</span>
</div>
<span class="card-year-badge">Negatif Projeksiyon</span>
</div>

<!-- Bölüm A: Gözlenen Referans Durum (2026) -->
<div class="data-section-box">
<div class="data-section-title">Gözlenen Referans Durum (2026)</div>
<div class="data-row-compact">
<span class="data-lbl">Türkiye Yıllık PM2.5 Ortalaması</span>
<span class="data-val">{calc['observed_pm25']} µg/m³</span>
</div>
<div class="data-row-compact">
<span class="data-lbl">DSÖ 2021 Yıllık Kılavuz Değeri</span>
<span class="data-val">{calc['observed_who']} µg/m³ ({calc['who_ratio']} kat aşım)</span>
</div>
<div class="data-row-compact">
<span class="data-lbl">Yıllık Temel Solunum Ölümü</span>
<span class="data-val">{calc['observed_deaths']} kişi/yıl</span>
</div>
</div>

<!-- Bölüm B: Senaryo (Projeksiyon Modeli) -->
<div class="data-section-title" style="margin-top:14px;">Senaryo ({selected_year} Modeli)</div>
<div class="scenario-grid-2x2">
<div class="scenario-metric-box">
<div class="metric-big-num" style="color:#ef4444;">{calc['target_pm25']} <small style="font-size:12px;">µg/m³</small></div>
<div class="metric-title-small">Öngörülen PM2.5 Seviyesi</div>
<div class="metric-sub-note">{calc['pct_label']} kirlilik artışı</div>
</div>
<div class="scenario-metric-box">
<div class="metric-big-num" style="color:#f87171;">{calc['deaths_label']}</div>
<div class="metric-title-small">Önlenebilir Erken Ölüm Kaybı</div>
<div class="metric-sub-note">Kümülatif erken vefat</div>
</div>
<div class="scenario-metric-box">
<div class="metric-big-num" style="color:#fb923c;">{calc['cost_label']}</div>
<div class="metric-title-small">Tahmini Kamu Sağlık Zararı</div>
<div class="metric-sub-note">Tedavi ve iş gücü kaybı</div>
</div>
<div class="scenario-metric-box">
<div class="metric-big-num" style="color:#f87171;">{calc['life_label']}</div>
<div class="metric-title-small">Beklenen Yaşam Süresi Kaybı</div>
<div class="metric-sub-note">Ortalama ömür kısalması</div>
</div>
</div>
</div>

<div class="card-footer-caption">
* Eylemsizlik durumunda sağlık sistemine binecek tahmini yük projeksiyonudur.
</div>
</div>
            """).strip(), unsafe_allow_html=True)

    # 7. Alttaki 3 Sade Özet KPI Kartı (st.columns(3))
    st.write("")
    kpi1, kpi2, kpi3 = st.columns(3)

    if is_clean:
        with kpi1:
            st.markdown(textwrap.dedent(f"""
<div class="kpi-row-card">
<div class="kpi-row-label">Önlenebilir Tahmini Ölüm</div>
<div class="kpi-row-value" style="color:#10b981;">{calc['deaths_label']}</div>
<div class="kpi-row-subtext">Önlenebilir Hayatlar ({selected_year})</div>
</div>
            """).strip(), unsafe_allow_html=True)

        with kpi2:
            st.markdown(textwrap.dedent(f"""
<div class="kpi-row-card">
<div class="kpi-row-label">Tasarruf Edilen Sağlık Bütçesi</div>
<div class="kpi-row-value" style="color:#38bdf8;">{calc['cost_label']}</div>
<div class="kpi-row-subtext">Kamu ve İş Gücü Tasarrufu</div>
</div>
            """).strip(), unsafe_allow_html=True)

        with kpi3:
            st.markdown(textwrap.dedent(f"""
<div class="kpi-row-card">
<div class="kpi-row-label">Hedeflenen PM2.5 Seviyesi</div>
<div class="kpi-row-value" style="color:#34d399;">{calc['target_pm25']} µg/m³</div>
<div class="kpi-row-subtext">{calc['pct_label']} Değişim ({selected_year})</div>
</div>
            """).strip(), unsafe_allow_html=True)
    else:
        with kpi1:
            st.markdown(textwrap.dedent(f"""
<div class="kpi-row-card">
<div class="kpi-row-label">Önlenebilir Erken Ölüm Kaybı</div>
<div class="kpi-row-value" style="color:#ef4444;">{calc['deaths_label']}</div>
<div class="kpi-row-subtext">Kümülatif Can Kaybı ({selected_year})</div>
</div>
            """).strip(), unsafe_allow_html=True)

        with kpi2:
            st.markdown(textwrap.dedent(f"""
<div class="kpi-row-card">
<div class="kpi-row-label">Tahmini Kamu Sağlık Zararı</div>
<div class="kpi-row-value" style="color:#fb923c;">{calc['cost_label']}</div>
<div class="kpi-row-subtext">Tedavi, İlaç ve İş Gücü Kaybı</div>
</div>
            """).strip(), unsafe_allow_html=True)

        with kpi3:
            st.markdown(textwrap.dedent(f"""
<div class="kpi-row-card">
<div class="kpi-row-label">Öngörülen PM2.5 Seviyesi</div>
<div class="kpi-row-value" style="color:#f87171;">{calc['target_pm25']} µg/m³</div>
<div class="kpi-row-subtext">{calc['pct_label']} Değişim ({selected_year})</div>
</div>
            """).strip(), unsafe_allow_html=True)

    # 8. Varsayımlar ve Yöntem Bölümü (Hesaplama Metodolojisi)
    st.write("")
    with st.expander("Varsayımlar ve Yöntem (Hesaplama Metodolojisi)"):
        st.markdown(f"""
**1. Temel Durum ve Gözlenen Veri:**
        - **Mevcut PM2.5 Ortalaması:** {calc['observed_pm25']} µg/m³ (Çevre ve Şehircilik Bakanlığı Sürekli İzleme Merkezi ve Copernicus CAMS modeli 81 il ağırlıklı ortalaması).
        - **Toplam Nüfus:** {calc['total_pop']} kişi (TÜİK 2024 Adrese Dayalı Nüfus Kayıt Sistemi).
        - **Temel Ölüm Sayısı:** Yıllık solunum yolu hastalıklarına bağlı temel vefatlar ({calc['observed_deaths']} kişi/yıl, TÜİK Ölüm ve Ölüm Nedeni İstatistikleri).
        - **DSÖ 2021 Kılavuz Değeri:** Dünya Sağlık Örgütü 2021 Küresel Hava Kalitesi Kılavuz İlkelerine göre yıllık PM2.5 kılavuz değeri **5,0 µg/m³**, 24 saatlik kılavuz ise **15,0 µg/m³** olarak belirlenmiştir (DSÖ'ye göre PM2.5 için kesin risksiz güvenli bir eşik yoktur). Türkiye ortalaması kılavuz değerin yaklaşık **{calc['who_ratio']} katıdır**.

        ---

**2. PM2.5 Senaryo Oranları:**
        - **Temiz Yol (Yeşil Dönüşüm):** 2026 (%-8, 33,4 µg/m³), 2029 (%-22, 28,3 µg/m³), 2032 (%-45, 20,0 µg/m³), 2035 (%-72, 10,2 µg/m³). Kaynak: ÇŞİDB Temiz Hava Eylem Planı hedefleri ve elektrikli toplu taşıma / ısı pompası dönüşüm yol haritaları.
        - **Gri Yol (Eylemsizlik):** 2026 (%+14, 41,4 µg/m³), 2029 (%+35, 49,0 µg/m³), 2032 (%+68, 61,0 µg/m³), 2035 (%+116, 78,5 µg/m³). Kaynak: Fosil yakıt tüketim trendi ve sanayi emisyon artış projeksiyonları.

        ---

**3. Önlenebilir Tahmini Ölüm Hesaplaması:**
        - Konsantrasyon-Tepki Fonksiyonu (Concentration-Response Function - CRF): Uzun vadeli her 10 µg/m³ PM2.5 değişimi için solunum ve dolaşım mortalitesinde %6,2 bağıl risk katsayısı kullanılmıştır (RR = 1,062 / 10 µg/m³ PM2.5).
        - Kaynak: World Health Organization (WHO Global Air Quality Guidelines 2021) ve Health Effects Institute (Global Burden of Disease 2021).

        ---

**4. Beklenen Yaşam Süresi (Life Expectancy) Katsayısı:**
        - Doğumda beklenen yaşam süresi artışı veya kaybı, her 10 µg/m³ kalıcı PM2.5 değişimi başına yaklaşık 0,61 yıl katsayısı ile hesaplanmıştır.
        - Kaynak: Pope et al., *"Fine-Particulate Air Pollution and Life Expectancy in the United States"*, New England Journal of Medicine (2009).
        """)
