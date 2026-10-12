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

    # Kümülatif Sağlık Harcaması Faturası: round(pm25 * 6.4, 1) = round(82.1 * 6.4, 1) = 525.4
    assert res["kumulatif_fatura_milyon_tl"] == round(82.1 * 6.4, 1)
    assert res["kumulatif_fatura_milyon_tl"] == 525.4

    # Kronikleşme Riski & Resmi Uyarı metin kontrolü
    assert "+%38" in res["kroniklesme_riski"]
    assert "2.8 - 4.1 yıl" in res["resmi_uyari"]


def test_simulate_green_policy_calculations():
    # Varsayılan değerler: Sanayi = 30%, Temiz Enerji = 25%
    sim = simulate_green_policy(
        pm25=82.1,
        solunum_olum=125,
        maliyet_milyon_tl=4276.2,
        industry_pct=30,
        clean_energy_pct=25,
        diag_type="canak"
    )

    assert sim["pm_reduction_pct"] > 0
    assert sim["new_pm25"] < 82.1
    assert sim["saved_lives"] > 0
    assert sim["saved_budget_milyon_tl"] > 0

    # Uç değerler: 0% / 0%
    sim_zero = simulate_green_policy(
        pm25=82.1,
        solunum_olum=125,
        maliyet_milyon_tl=4276.2,
        industry_pct=0,
        clean_energy_pct=0,
        diag_type="canak"
    )
    assert sim_zero["pm_reduction_pct"] == 0.0
    assert sim_zero["saved_lives"] == 0
    assert sim_zero["saved_budget_milyon_tl"] == 0.0

    # %100 / %100
    sim_max = simulate_green_policy(
        pm25=82.1,
        solunum_olum=125,
        maliyet_milyon_tl=4276.2,
        industry_pct=100,
        clean_energy_pct=100,
        diag_type="canak"
    )
    assert sim_max["pm_reduction_pct"] >= 75.0
    assert sim_max["saved_lives"] > sim["saved_lives"]


def test_render_green_page_structure():
    # Mini test dataframe
    test_df = pd.DataFrame([
        {"il": "Iğdır", "pm25": 82.1, "osb_sayisi": 1, "solunum_olum": 125, "solunum_olum_100k": 61.2, "nufus": 204000, "maliyet_milyon_tl": 4276.2},
        {"il": "Osmaniye", "pm25": 83.6, "osb_sayisi": 10, "solunum_olum": 517, "solunum_olum_100k": 94.3, "nufus": 548000, "maliyet_milyon_tl": 18007.3},
        {"il": "İstanbul", "pm25": 38.4, "osb_sayisi": 8, "solunum_olum": 11143, "solunum_olum_100k": 71.0, "nufus": 15655000, "maliyet_milyon_tl": 178398.7}
    ])

    # Should run without raising exceptions
    try:
        render_green_page(test_df)
    except Exception as e:
        # In a headless pytest environment without streamlit active session,
        # it might raise a Streamlit runtime error if any unhandled state occurs.
        # But st functions handle script runs or log warning.
        pytest.fail(f"render_green_page threw exception: {e}")
