"""
Unit tests for the Green Transformation Strategy, Diagnosis & Inaction Projection engine.
"""

import pytest
import pandas as pd
from app_pages.green_page import (
    diagnose_root_cause,
    calculate_inaction_scenario,
    simulate_green_policy,
    render_green_page
)


def test_diagnose_root_cause_rules():
    # Kural 1: OSB >= 6 ve PM2.5 > 40 -> Ağır Sanayi
    res_sanayi = diagnose_root_cause(pm25=48.5, osb_sayisi=14)
    assert res_sanayi["type"] == "sanayi"
    assert "Ağır Sanayi" in res_sanayi["title"]
    assert "SEÖS" in res_sanayi["action_items"][0]

    # Kural 2: OSB < 6 ve PM2.5 > 50 -> Çanak Topoğrafyası & Evsel Katı Yakıt
    res_canak = diagnose_root_cause(pm25=82.1, osb_sayisi=1)
    assert res_canak["type"] == "canak"
    assert "Çanak Topoğrafyası" in res_canak["title"]
    assert "kömür" in res_canak["action_items"][0].lower()

    # Kural 3: Diğer tüm durumlar -> Kentsel Yoğunluk, Ulaşım & İnşaat Tozu
    res_ulasim = diagnose_root_cause(pm25=38.4, osb_sayisi=8)
    assert res_ulasim["type"] == "ulasim"
    assert "Kentsel Yoğunluk" in res_ulasim["title"]
    assert "Düşük Emisyon Bölgeleri" in res_ulasim["action_items"][0]

    res_ulasim_low_pm = diagnose_root_cause(pm25=18.0, osb_sayisi=2)
    assert res_ulasim_low_pm["type"] == "ulasim"


def test_calculate_inaction_scenario_formulas():
    # İlin verileri: PM2.5 = 82.1, Solunum Ölüm = 125
    res = calculate_inaction_scenario(pm25=82.1, solunum_olum=125)
    
    # 10 Yıllık Önlenemeyen Ek Can Kaybı: int(solunum_olum * 1.45) = int(125 * 1.45) = 181
    assert res["ek_can_kaybi_10yil"] == int(125 * 1.45)
    assert res["ek_can_kaybi_10yil"] == 181

    # Kronikleşme Riski & Resmi Uyarı metin kontrolü
    assert "+%38" in res["kroniklesme_riski"]
    assert "2,8 - 4,1 yıl" in res["resmi_uyari"]


def test_ethical_and_scientific_terminology():
    res_canak = diagnose_root_cause(pm25=82.1, osb_sayisi=1)
    
    # 1. 'varoş' kelimesi kesinlikle bulunmamalı
    for item in res_canak["action_items"]:
        assert "varoş" not in item.lower()
    assert "Alt gelir grubu yerleşim alanları" in res_canak["action_items"][2]

    # 2. 'ölümcül kirlilik sisi' yerine bilimsel ifade olmalı
    assert "ölümcül" not in res_canak["detail"].lower()
    assert "tehlikeli hava kirliliği epizotlarına" in res_canak["detail"]


def test_simulate_green_policy_calculations():
    # Varsayılan değerler: Sanayi = 30%, Temiz Enerji = 25%
    sim = simulate_green_policy(
        pm25=82.1,
        solunum_olum=125,
        industry_pct=30,
        clean_energy_pct=25,
        diag_type="canak"
    )

    assert sim["pm_reduction_pct"] > 0
    assert sim["new_pm25"] < 82.1
    assert sim["saved_lives"] > 0

    # Uç değerler: 0% / 0%
    sim_zero = simulate_green_policy(
        pm25=82.1,
        solunum_olum=125,
        industry_pct=0,
        clean_energy_pct=0,
        diag_type="canak"
    )
    assert sim_zero["pm_reduction_pct"] == 0.0
    assert sim_zero["saved_lives"] == 0

    # %100 / %100
    sim_max = simulate_green_policy(
        pm25=82.1,
        solunum_olum=125,
        industry_pct=100,
        clean_energy_pct=100,
        diag_type="canak"
    )
    assert sim_max["pm_reduction_pct"] >= 75.0
    assert sim_max["saved_lives"] > sim["saved_lives"]


def test_render_green_page_structure():
    from streamlit.testing.v1 import AppTest

    def app_green():
        import pandas as pd
        from app_pages.green_page import render_green_page
        test_df = pd.DataFrame([
            {"il": "Iğdır", "pm25": 82.1, "osb_sayisi": 1, "solunum_olum": 125, "solunum_olum_100k": 61.2, "nufus": 204000},
            {"il": "Osmaniye", "pm25": 83.6, "osb_sayisi": 10, "solunum_olum": 517, "solunum_olum_100k": 94.3, "nufus": 548000},
            {"il": "İstanbul", "pm25": 38.4, "osb_sayisi": 8, "solunum_olum": 11143, "solunum_olum_100k": 71.0, "nufus": 15655000}
        ])
        render_green_page(test_df)

    at = AppTest.from_function(app_green)
    at.run()
    assert not at.exception

    all_markdown = " ".join([m.value for m in at.markdown])

    # 1. Etik dil kontrolü
    assert "varoş" not in all_markdown.lower()
    assert "ölümcül" not in all_markdown.lower()
    assert "RESMİ EPİDEMİYOLOJİK" not in all_markdown
    assert "Epidemiyolojik Risk Modeli Uyarısı" in all_markdown

    # 2. Metodolojik şeffaflık notu
    assert "DSÖ AirQ+" in all_markdown
    assert "Klinik kesinlik veya resmi adli can kaybı verisi niteliği taşımaz" in all_markdown

    # 3. Sayı ve birim formatı kontrolü (Türkçe virgüllü ondalık)
    assert "82,1" in all_markdown
    assert "2,8 - 4,1" in all_markdown

    # 4. Şehir entegrasyonu ve il seçici
    assert "Senaryo Analizi Yapılacak İli Seçin:" in at.selectbox[0].label
    assert "Iğdır İnteraktif Politika Simülatörü" in all_markdown


def test_render_scenarios_page_dropdown():
    from streamlit.testing.v1 import AppTest

    def app_scenarios():
        import pandas as pd
        from app_pages.scenarios_page import render_scenarios_page
        test_df = pd.DataFrame([
            {"il": "Iğdır", "pm25": 82.1, "osb_sayisi": 1, "solunum_olum": 125, "solunum_olum_100k": 61.2, "nufus": 204000},
            {"il": "Osmaniye", "pm25": 83.6, "osb_sayisi": 10, "solunum_olum": 517, "solunum_olum_100k": 94.3, "nufus": 548000}
        ])
        render_scenarios_page(test_df)

    at = AppTest.from_function(app_scenarios)
    at.run()
    assert not at.exception

    # Sayfanın en üstünde dropdown olmalı
    assert len(at.selectbox) >= 1
    assert "Senaryo Analizi Yapılacak İli Seçin:" in at.selectbox[0].label
