"""
Birim Testleri: Web veri dışa aktarımı (scripts/export_web_data.py)

Sitedeki tüm sayılar bu JSON dosyalarından gelir; bu testler hem dışa aktarım mantığını hem de
depodaki JSON dosyalarının Python hesaplarıyla güncel olduğunu doğrular.
"""

import json
import os
import sys

import numpy as np
import pytest
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import export_web_data as exp  # noqa: E402
from data_sources.constants import KIRLILIK_KADEMELERI  # noqa: E402
from data_sources.local_official_data import build_master_dataset  # noqa: E402

DATA_DIR = os.path.join(ROOT, "web", "src", "data")


@pytest.fixture(scope="module")
def df():
    return build_master_dataset()


def load(name):
    with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
        return json.load(f)


def test_provinces_payload(df):
    q = exp.quantiles(df)
    rows = exp.build_provinces(df, q)
    assert len(rows) == 81
    labels = {t["etiket"] for t in KIRLILIK_KADEMELERI["pm25"]}
    for r in rows:
        assert r["dso_risk"] in labels
        assert r["kategori"] in {"A", "B", "YK", "N"}
        assert 1 <= r["pm_rank"] <= 81 and 1 <= r["nufus_rank"] <= 81
        assert 0 < r["pct_hava"] <= 100
        assert len(r["ozet"]) == 6
    # Kategori kuralları İl Grupları tanımıyla aynı olmalı
    for r in rows:
        if r["kategori"] == "A":
            assert r["toplam_osb"] <= q["q1_osb"] and r["pm25"] >= q["q3_pm25"]
        if r["kategori"] == "B":
            assert r["toplam_osb"] >= q["q3_osb"] and r["pm25"] >= q["q3_pm25"]


def test_correlation_stats_match_scipy(df):
    c = exp.correlation_stats(df)
    rho = stats.spearmanr(df["osb_alani_hektar"], df["pm25"])[0]
    assert c["osb_pm25"]["spearman_rho"] == pytest.approx(round(rho, 3))
    assert c["osb_pm25"]["ci_lo"] < c["osb_pm25"]["spearman_rho"] < c["osb_pm25"]["ci_hi"]
    # OLS katsayıları statsmodels ile aynı olmalı
    import statsmodels.api as sm
    work = df.assign(rakim=df["il"].map(exp.IL_RAKIM).fillna(500.0), nufus_100k=df["nufus"] / 100000.0)
    ols = sm.OLS(work["pm25"], sm.add_constant(work[["toplam_osb", "rakim", "nufus_100k"]])).fit()
    assert np.allclose([t["coef"] for t in c["ols"]["terms"]], ols.params.values)
    assert c["ols"]["r2"] == pytest.approx(ols.rsquared)
    # Moran's I: 81 nokta, dört çeyrek, geçerli p değeri
    assert len(c["moran"]["points"]) == 81
    assert 0 < c["moran"]["p"] <= 1


def test_map_payload_covers_all_provinces():
    m = exp.map_payload()
    assert len(m["provinces"]) == 81
    for p in m["provinces"]:
        assert p["d"].startswith("M") and p["d"].endswith("Z")
        assert 0 <= p["cx"] <= m["width"] and 0 <= p["cy"] <= m["height"]


def test_committed_json_in_sync(df):
    """web/src/data/*.json güncel değilse `python scripts/export_web_data.py` çalıştırılmalı."""
    rows = {r["il"]: r for r in load("provinces.json")}
    assert len(rows) == 81
    for _, r in df.iterrows():
        assert rows[r["il"]]["pm25"] == pytest.approx(r["pm25"]), r["il"]
        assert rows[r["il"]]["dso_risk"] == r["dso_risk"], r["il"]
    meta = load("meta.json")
    assert meta["tiers"] == KIRLILIK_KADEMELERI
    daily = load("daily.json")
    assert set(daily["cities"]) == set(rows)
    assert all(len(v) == len(daily["dates"]) for v in daily["cities"].values())


def test_json_has_no_nan():
    for name in ["provinces.json", "stats.json", "daily.json", "map.json", "meta.json"]:
        with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
            text = f.read()
        assert "NaN" not in text and "Infinity" not in text, name
