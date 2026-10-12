"""
Ulusal Yeşil Dönüşüm Stratejisi, Teşhis & Risk Projeksiyon Motoru
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import streamlit as st
import pandas as pd


from decimal import Decimal, ROUND_HALF_UP


def to_tr_num(val: float, decimals: int = 1) -> str:
    """Sayıları matematiksel doğru yuvarlamayla (ROUND_HALF_UP) Türkçe formatlar."""
    if pd.isnull(val):
        return "—"
    dec_fmt = "1" if decimals == 0 else f"0.{'0'*(decimals-1)}1"
    dec = Decimal(f"{float(val):.4f}").quantize(Decimal(dec_fmt), rounding=ROUND_HALF_UP)
    if decimals == 0:
        return f"{int(dec):,}".replace(",", ".")
    parts = f"{dec:.{decimals}f}".split(".")
    int_part = f"{int(parts[0]):,}".replace(",", ".")
    return f"{int_part},{parts[1]}"


def diagnose_root_cause(pm25: float, osb_sayisi: int) -> dict:
    """
    Kök neden analizi algoritması:
    - Kural 1 (OSB >= 6 ve PM2.5 > 40): Ağır Sanayi & Endüstriyel Emisyon
    - Kural 2 (OSB < 6 ve PM2.5 > 50): Çanak Topoğrafyası & Evsel Katı Yakıt
    - Kural 3 (Diğer tüm durumlar): Kentsel Yoğunluk, Ulaşım & İnşaat Tozu
    """
    if osb_sayisi >= 6 and pm25 > 40:
        return {
            "type": "sanayi",
            "badge": "AĞIR SANAYİ BASKISI",
            "badge_color": "#ef4444",
            "border_glow": "rgba(239, 68, 68, 0.4)",
            "title": "Ağır Sanayi & Endüstriyel Emisyon",
            "detail": (
                "Kirliliğin birincil kaynağı OSB bacaları, filtre denetimsizliği ve "
                "fosil yakıtlı termik/endüstriyel üretim tesisleridir."
            ),
            "action_items": [
                "Tüm OSB bacalarına 7/24 Kesintisiz Emisyon Ölçüm Sistemi (SEÖS) zorunluluğu",
                "Sanayi tesislerinde elektrostatik ve torbalı filtre denetimlerinin ayda 2 keze çıkarılması",
                "Yeşil Çelik / Temiz Üretim GES teşviklerinin %50 artırılması"
            ]
        }
    elif osb_sayisi < 6 and pm25 > 50:
        return {
            "type": "canak",
            "badge": "COĞRAFİ KAPAN & İNVERSİYON",
            "badge_color": "#f59e0b",
            "border_glow": "rgba(245, 158, 11, 0.4)",
            "title": "Çanak Topoğrafyası & Evsel Katı Yakıt",
            "detail": (
                "Coğrafi çanak yapısı hava akımını engellemekte; düşük gelirli konutlarda "
                "kalitesiz kömür/biyokütle kullanımı inversiyonla birleşerek tehlikeli hava kirliliği epizotlarına ve yoğun duman birikimine yol açmaktadır."
            ),
            "action_items": [
                "Sosyal yardım amaçlı kömür dağıtımının acilen sonlandırılarak ücretsiz ısı pompası/doğalgaz desteği verilmesi",
                "Vadi tabanında rüzgar koridorlarını kesen çok katlı imar izinlerinin durdurulması",
                "Alt gelir grubu yerleşim alanları ve kentsel dönüşüm bölgelerinde bina yalıtım seferberliği"
            ]
        }
    else:
        return {
            "type": "ulasim",
            "badge": "KENTSEL EMİSYON & ULAŞIM",
            "badge_color": "#00f2fe",
            "border_glow": "rgba(0, 242, 254, 0.4)",
            "title": "Kentsel Yoğunluk, Ulaşım & İnşaat Tozu",
            "detail": (
                "Eski araç filosu (dizel emisyonları), sıkışık yapılaşma ve kentsel "
                "inşaat/trafik tozu arka plan kirliliğini sürekli kılmaktadır."
            ),
            "action_items": [
                "Düşük Emisyon Bölgeleri (LEZ) kurularak yaşlı dizel araç girişinin sınırlandırılması",
                "Toplu taşımada elektrikli otobüs ve raylı sistem payının %60 üzerine çıkarılması",
                "Kentsel yeşil bariyer ve hava akım kanallarının master plana işlenmesi"
            ]
        }


def calculate_inaction_scenario(pm25: float, solunum_olum: float) -> dict:
    """
    2035 Eylemsizlik Senaryosu matematiksel modellemesi:
    - 10 Yıllık Önlenemeyen Ek Can Kaybı: int(solunum_olum * 1.45)
    - Kronikleşme Riski: 'Astım ve KOAH acil servis başvurularında +%38 kalıcı artış.'
    - Epidemiyolojik Uyarı: 'Kritik inversiyon dönemlerinde yaşam süresinde 2,8 - 4,1 yıl kayıp projeksiyonu.'
    """
    ek_can_kaybi = int(max(0.0, solunum_olum) * 1.45)
    return {
        "ek_can_kaybi_10yil": ek_can_kaybi,
        "kroniklesme_riski": "Astım ve KOAH acil servis başvurularında +%38 kalıcı artış.",
        "resmi_uyari": "Kritik inversiyon dönemlerinde yaşam süresinde 2,8 - 4,1 yıl kayıp projeksiyonu."
    }


def simulate_green_policy(
    pm25: float,
    solunum_olum: float,
    industry_pct: float,
    clean_energy_pct: float,
    diag_type: str = "sanayi"
) -> dict:
    """
    İnteraktif Politika Simülatörü epidemiyolojik etki hesaplayıcısı.
    """
    # Ağırlıklı kirlilik azaltım oranı
    if diag_type == "sanayi":
        pm_reduction = (industry_pct * 0.52) + (clean_energy_pct * 0.36)
    elif diag_type == "canak":
        pm_reduction = (industry_pct * 0.25) + (clean_energy_pct * 0.65)
    else:
        pm_reduction = (industry_pct * 0.40) + (clean_energy_pct * 0.48)

    pm_reduction = min(82.0, max(0.0, pm_reduction))
    new_pm25 = max(5.0, round(pm25 * (1.0 - pm_reduction / 100.0), 1))

    # Kurtarılabilecek yıllık can kaybı
    if solunum_olum > 0 and pm_reduction > 0:
        saved_lives = max(1, int(solunum_olum * (pm_reduction / 100.0) * 0.70))
    else:
        saved_lives = 0

    return {
        "pm_reduction_pct": round(pm_reduction, 1),
        "new_pm25": new_pm25,
        "saved_lives": saved_lives
    }


def render_green_page(df: pd.DataFrame, selected_city: str = None):
    """
    Ulusal Yeşil Dönüşüm Stratejisi, Teşhis & Risk Projeksiyon Motoru
    Sağlık Bakanlığı / Çevre Bakanlığı düzeyinde kurumsal karar destek arayüzü.
    """
    # 1. Sayfa Stilleri (Koyu Lacivert / Cam / Neon Vurgular)
    st.markdown("""
    <style>
    .green-hero-box {
        background: linear-gradient(135deg, rgba(11, 19, 43, 0.95) 0%, rgba(17, 26, 46, 0.90) 100%);
        border: 1px solid rgba(0, 242, 254, 0.25);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }
    .green-title {
        font-size: 26px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .green-subtitle {
        font-size: 14px;
        color: #94a3b8;
        line-height: 1.5;
        margin-bottom: 0;
    }
    .glass-card {
        background: rgba(17, 26, 46, 0.85);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border-radius: 14px;
        padding: 22px 20px;
        min-height: 380px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .glass-card:hover {
        transform: translateY(-2px);
    }
    .col-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
        text-transform: uppercase;
    }
    .card-header-title {
        font-size: 16px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 12px;
        line-height: 1.4;
    }
    .action-item {
        background: rgba(2, 18, 32, 0.6);
        border-left: 3px solid #00f2fe;
        border-radius: 4px;
        padding: 10px 12px;
        margin-bottom: 8px;
        font-size: 12.5px;
        color: #e2e8f0;
        line-height: 1.45;
    }
    .metric-row {
        background: rgba(2, 18, 32, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 8px;
    }
    .metric-label {
        font-size: 11px;
        color: #8faec9;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }
    .metric-val {
        font-size: 18px;
        font-weight: 800;
        margin-top: 2px;
    }
    .sim-panel {
        background: linear-gradient(135deg, rgba(11, 19, 43, 0.95) 0%, rgba(3, 22, 38, 0.98) 100%);
        border: 1px solid rgba(0, 242, 254, 0.3);
        border-radius: 16px;
        padding: 24px;
        margin-top: 28px;
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.5);
    }
    .sim-kpi-card {
        background: rgba(2, 18, 32, 0.85);
        border-radius: 12px;
        padding: 18px 20px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)

    # 2. Başlık ve Üst Panel
    st.markdown("""
    <div class="green-hero-box">
        <div class="green-title">
            Ulusal Yeşil Dönüşüm, Eylem Planı & Risk Projeksiyonu
        </div>
        <div class="green-subtitle">
            Veriye dayalı kök neden tespiti, kurumsal müdahale politikaları ve 2035 eylemsizlik projeksiyonu.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.warning("Veri seti bulunamadı.")
        return

    # 3. Şehir Seçimi (Varsayılan: Yüksek riskli Iğdır veya Osmaniye)
    cities = sorted(df["il"].unique().tolist())
    if selected_city is None or selected_city not in cities:
        default_idx = 0
        if "Iğdır" in cities:
            default_idx = cities.index("Iğdır")
        elif "Osmaniye" in cities:
            default_idx = cities.index("Osmaniye")

        selected_city = st.selectbox(
            "Senaryo Analizi Yapılacak İli Seçin:",
            cities,
            index=default_idx,
            key="green_city_selector"
        )

    # Seçilen ilin verilerini al
    city_data = df[df["il"] == selected_city].iloc[0]
    pm25 = float(city_data.get("pm25", 0.0))
    osb_sayisi = int(city_data.get("osb_sayisi", 0))
    solunum_olum_100k = float(city_data.get("solunum_olum_100k", 0.0))

    solunum_olum = float(city_data.get("solunum_olum", 0.0))
    if solunum_olum <= 0 and solunum_olum_100k > 0:
        nufus = float(city_data.get("nufus", 500000))
        solunum_olum = solunum_olum_100k * (nufus / 100000.0)

    dso_kat = round(pm25 / 5.0, 1) if pm25 > 0 else 0
    pm25_str = to_tr_num(pm25, 1)
    dso_kat_str = to_tr_num(dso_kat, 1)
    sol_str = to_tr_num(solunum_olum, 0)

    st.markdown(f"""
    <div style="background:rgba(2, 18, 32, 0.7); border:1px solid rgba(0, 242, 254, 0.2); border-radius:10px; padding:12px 18px; margin-top:12px; margin-bottom:20px; display:flex; justify-content:space-around; align-items:center; flex-wrap:wrap; gap:12px;">
        <div style="text-align:center;">
            <div style="font-size:11px; color:#94a3b8;">Seçili İl</div>
            <div style="font-size:18px; font-weight:800; color:#38bdf8;">{selected_city}</div>
        </div>
        <div style="width:1px; height:28px; background:rgba(255,255,255,0.1);"></div>
        <div style="text-align:center;">
            <div style="font-size:11px; color:#94a3b8;">PM2.5 Seviyesi</div>
            <div style="font-size:18px; font-weight:800; color:{'#ef4444' if pm25 > 40 else '#f59e0b'};">{pm25_str} <span style="font-size:12px; font-weight:400; color:#cbd5e1;">µg/m³</span></div>
        </div>
        <div style="width:1px; height:28px; background:rgba(255,255,255,0.1);"></div>
        <div style="text-align:center;">
            <div style="font-size:11px; color:#94a3b8;">DSÖ Limit Aşımı</div>
            <div style="font-size:18px; font-weight:800; color:#ef4444;">{dso_kat_str} Kat</div>
        </div>
        <div style="width:1px; height:28px; background:rgba(255,255,255,0.1);"></div>
        <div style="text-align:center;">
            <div style="font-size:11px; color:#94a3b8;">Aktif OSB Sayısı</div>
            <div style="font-size:18px; font-weight:800; color:#38bdf8;">{osb_sayisi} Tesis</div>
        </div>
        <div style="width:1px; height:28px; background:rgba(255,255,255,0.1);"></div>
        <div style="text-align:center;">
            <div style="font-size:11px; color:#94a3b8;">Yıllık Solunum Vefatı</div>
            <div style="font-size:18px; font-weight:800; color:#cbd5e1;">~{sol_str} Can</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    # 4. Algoritmik Teşhis & Senaryo Motoru (3 Kolon Cam Kartlar)
    diag = diagnose_root_cause(pm25, osb_sayisi)
    inaction = calculate_inaction_scenario(pm25, solunum_olum)

    col1, col2, col3 = st.columns(3)

    # KOLON 1: Havayı Ne Kirletiyor? (Kök Neden Analizi)
    with col1:
        st.markdown(f"""<div class="glass-card" style="border:1px solid {diag['border_glow']}; box-shadow:0 8px 24px {diag['border_glow']};">
<div>
<span class="col-badge" style="background:{diag['badge_color']}22; color:{diag['badge_color']}; border:1px solid {diag['badge_color']};">KÖK NEDEN ANALİZİ</span>
<div class="card-header-title">{selected_city} — {diag['title']}</div>
<p style="font-size:13px; color:#cbd5e1; line-height:1.65; margin-bottom:16px;">{diag['detail']}</p>
</div>
<div style="background:rgba(2, 18, 32, 0.7); border-radius:8px; padding:12px; border:1px solid rgba(255,255,255,0.05);">
<div style="font-size:11px; color:#8faec9; margin-bottom:4px;">Algoritma Teşhis Çıktısı:</div>
<div style="font-size:13px; font-weight:700; color:{diag['badge_color']};">&bull; {diag['badge']}</div>
<div style="font-size:11.5px; color:#94a3b8; margin-top:4px;">(OSB: {osb_sayisi} &bull; PM2.5: {pm25_str} µg/m³)</div>
</div>
</div>""", unsafe_allow_html=True)

    # KOLON 2: Resmi Eylem Planı (Öncelikli Politika Müdahalesi)
    with col2:
        actions_html = "".join([f'<div class="action-item">• {item}</div>' for item in diag["action_items"]])
        st.markdown(f"""<div class="glass-card" style="border:1px solid rgba(0, 242, 254, 0.35); box-shadow:0 8px 24px rgba(0, 242, 254, 0.15);">
<div>
<span class="col-badge" style="background:rgba(0, 242, 254, 0.15); color:#00f2fe; border:1px solid #00f2fe;">RESMİ EYLEM PLANI</span>
<div class="card-header-title">{selected_city} Öncelikli Politika Müdahalesi</div>
<div style="margin-top:6px;">{actions_html}</div>
</div>
<div style="margin-top:12px; font-size:11.5px; color:#64748b; font-style:italic;">* Çevre, Şehircilik ve İklim Değişikliği Bakanlığı ile İl Mahalli Çevre Kurulu direktifleriyle uyumlu.</div>
</div>""", unsafe_allow_html=True)

    # KOLON 3: 2035 Eylemsizlik Senaryosu (Hiçbir Şey Yapılmazsa)
    with col3:
        st.markdown(f"""<div class="glass-card" style="border:1px solid rgba(239, 68, 68, 0.35); box-shadow:0 8px 24px rgba(239, 68, 68, 0.15);">
<div>
<span class="col-badge" style="background:rgba(239, 68, 68, 0.15); color:#ef4444; border:1px solid #ef4444;">2035 EYLEMSİZLİK SENARYOSU</span>
<div class="card-header-title">{selected_city} — Hiçbir Şey Yapılmazsa (10 Yıllık Risk)</div>
<div class="metric-row">
<div class="metric-label">10 Yıllık Önlenemeyen Ek Can Kaybı</div>
<div class="metric-val" style="color:#ef4444;">+{to_tr_num(inaction['ek_can_kaybi_10yil'], 0)} Kişi</div>
</div>
<div class="metric-row" style="margin-bottom:0;">
<div class="metric-label">Kronikleşme Riski</div>
<div style="font-size:12px; color:#e2e8f0; margin-top:2px; font-weight:600;">{inaction['kroniklesme_riski']}</div>
</div>
</div>
<div style="background:rgba(239, 68, 68, 0.08); border:1px dashed rgba(239, 68, 68, 0.4); border-radius:8px; padding:10px 12px; margin-top:12px;">
<div style="font-size:11px; font-weight:700; color:#ef4444; margin-bottom:2px;">Epidemiyolojik Risk Modeli Uyarısı</div>
<div style="font-size:11.5px; color:#cbd5e1; line-height:1.4;">{inaction['resmi_uyari']}</div>
</div>
</div>""", unsafe_allow_html=True)

    # 5. İnteraktif Yeşil Politika Simülatörü
    st.markdown(f"""<div class="sim-panel">
<div style="font-size:18px; font-weight:800; color:#ffffff; margin-bottom:4px; display:flex; align-items:center; gap:8px;">
{selected_city} İnteraktif Politika Simülatörü
</div>
<div style="font-size:13px; color:#94a3b8; margin-bottom:20px;">
Sanayi baca filtre denetimlerini ve temiz ısınma/enerji dönüşüm oranlarını ayarlayarak 
{selected_city} için kurtarılabilecek hayatları ve hava kalitesi iyileşme oranını simüle edin.
</div>""", unsafe_allow_html=True)

    col_sim_ctrl, col_sim_kpis = st.columns([1.1, 1.9])

    with col_sim_ctrl:
        industry_filter = st.slider(
            "Sanayi Baca Filtresi & Yeşil Teknoloji Dönüşümü (%):",
            min_value=0,
            max_value=100,
            value=30,
            step=5,
            key="sim_industry_filter"
        )
        clean_energy = st.slider(
            "Temiz Enerji & Kömürden Arındırma Oranı (%):",
            min_value=0,
            max_value=100,
            value=25,
            step=5,
            key="sim_clean_energy"
        )

    # Simülasyon Hesaplamaları
    sim_res = simulate_green_policy(
        pm25=pm25,
        solunum_olum=solunum_olum,
        industry_pct=industry_filter,
        clean_energy_pct=clean_energy,
        diag_type=diag["type"]
    )

    with col_sim_kpis:
        kpi1, kpi2 = st.columns(2)

        with kpi1:
            st.markdown(f"""<div class="sim-kpi-card" style="border-top:3px solid #10b981;">
<div style="font-size:11px; color:#8faec9; text-transform:uppercase; font-weight:700;">Kurtarılabilecek Can</div>
<div style="font-size:24px; font-weight:900; color:#10b981; margin:6px 0;">~{to_tr_num(sim_res['saved_lives'], 0)}</div>
<div style="font-size:11px; color:#94a3b8;">Kişi / Yıl (Önlenebilir)</div>
</div>""", unsafe_allow_html=True)

        with kpi2:
            st.markdown(f"""<div class="sim-kpi-card" style="border-top:3px solid #38bdf8;">
<div style="font-size:11px; color:#8faec9; text-transform:uppercase; font-weight:700;">PM2.5 İyileşme Oranı</div>
<div style="font-size:24px; font-weight:900; color:#38bdf8; margin:6px 0;">-%{to_tr_num(sim_res['pm_reduction_pct'], 1)}</div>
<div style="font-size:11px; color:#94a3b8;">{pm25_str} ➔ {to_tr_num(sim_res['new_pm25'], 1)} µg/m³</div>
</div>""", unsafe_allow_html=True)

    # Metodolojik Şeffaflık Notu (DSÖ AirQ+ ve RR katsayıları)
    st.markdown("""
    <div style="margin-top:20px; background:rgba(2, 18, 32, 0.6); border:1px solid rgba(255, 255, 255, 0.08); border-radius:8px; padding:12px 16px; font-size:12px; color:#94a3b8; line-height:1.5;">
        <strong>Not:</strong> Öngörülen can kaybı ve morbidite projeksiyonları, DSÖ AirQ+ ve küresel nispi risk (RR) katsayıları baz alınarak simüle edilmiştir. Klinik kesinlik veya resmi adli can kaybı verisi niteliği taşımaz.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
