"""
Unit tests for 2035 Future Fork (Gelecek Yol Ayrımı) Simulation Page.
"""

import pytest
import pandas as pd
from app_pages.future_fork_page import (
    TIMELINE_YEARS,
    GREEN_PATH_DATA,
    GRAY_PATH_DATA,
    get_fork_scenario_data,
    render_future_fork_page
)


def test_timeline_years_structure():
    assert len(TIMELINE_YEARS) == 4
    assert "2026" in TIMELINE_YEARS[0]
    assert "2029" in TIMELINE_YEARS[1]
    assert "2032" in TIMELINE_YEARS[2]
    assert "2035" in TIMELINE_YEARS[3]


def test_green_path_data():
    for yr in TIMELINE_YEARS:
        assert yr in GREEN_PATH_DATA
        d = GREEN_PATH_DATA[yr]
        assert "action_main" in d
        assert "metrics" in d
        assert len(d["bullets"]) >= 3

    # Check 2035 ultimate targets
    target_2035 = GREEN_PATH_DATA["2035 (Nihai Tablo)"]
    assert "81 ilde DSÖ hava kalitesi standartlarına ulaşıldı" in target_2035["action_main"]
    assert "+18,500" in target_2035["metrics"]["lives_saved"]
    assert "85.0 Milyar" in target_2035["metrics"]["budget_saved"]
    assert "+3.2 Yıl" in target_2035["metrics"]["life_exp"]


def test_gray_path_data():
    for yr in TIMELINE_YEARS:
        assert yr in GRAY_PATH_DATA
        d = GRAY_PATH_DATA[yr]
        assert "action_main" in d
        assert "metrics" in d
        assert len(d["bullets"]) >= 3

    # Check 2035 inaction heavy losses
    loss_2035 = GRAY_PATH_DATA["2035 (Nihai Tablo)"]
    assert "Hava kalitesi geri döndürülemez eşiği aşıyor" in loss_2035["action_main"]
    assert "145,000+" in loss_2035["metrics"]["deaths_lost"]
    assert "210.0 Milyar" in loss_2035["metrics"]["cost_incurred"]
    assert "-3.8 Yıl" in loss_2035["metrics"]["life_loss"]


def test_get_fork_scenario_data_selector():
    green_data = get_fork_scenario_data("Yeşil", TIMELINE_YEARS[0])
    assert "Bireysel Korunma" in green_data["action_title"]

    gray_data = get_fork_scenario_data("Gri", TIMELINE_YEARS[0])
    assert "İhmal" in gray_data["action_title"]


def test_render_future_fork_page_runs():
    df = pd.DataFrame([{"il": "Ankara", "pm25": 30.0}])
    try:
        render_future_fork_page(df)
    except Exception as e:
        pytest.fail(f"render_future_fork_page failed with exception: {e}")
