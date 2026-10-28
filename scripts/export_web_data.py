"""
Web Sitesi Veri Dışa Aktarımı
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

Python'daki tüm veri birleştirme ve istatistik hesaplarını çalıştırır ve sonuçları
Next.js sitesinin okuduğu JSON dosyalarına (web/src/data/) yazar. Site tamamen statiktir;
tarayıcıda yeniden istatistik hesaplanmaz, böylece sayılar test edilmiş Python koduyla birebir aynıdır.

Kullanım:
    python scripts/export_web_data.py            # mevcut önbellek dosyalarından üret
    python scripts/export_web_data.py --refresh  # önce CAMS günlük verisini yenile
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from scipy import stats

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)

from analytics.correlation import calculate_bivariate_correlation, calculate_bootstrap_ci  # noqa: E402
from analytics.hypothesis_tests import run_regional_anova  # noqa: E402
from analytics.summaries import generate_city_summary  # noqa: E402
from data_processing.aggregator import aggregate_by_region  # noqa: E402
from data_sources.cams_city_connector import load_city_daily, refresh_city_daily  # noqa: E402
from data_sources.constants import (  # noqa: E402
    DSO_KILAVUZ_DEGERLERI,
    IL_RAKIM,
    KIRLILIK_KADEMELERI,
    KOORDINATLAR,
    get_dataset_date_info,
)
from data_sources.local_official_data import (  # noqa: E402
    AIRQ_KARSI_OLGU,
    AIRQ_RR_PER_10,
    CAMS_YILI,
    build_master_dataset,
)
from data_sources.openmeteo_connector import get_national_timeseries  # noqa: E402

OUT_DIR = os.path.join(ROOT_DIR, "web", "src", "data")
MORAN_PERMUTATIONS = 999
MORAN_SEED = 42


def clean(obj):
    """numpy/pandas türlerini ve NaN değerlerini JSON uyumlu hale getirir."""
    if isinstance(obj, dict):
        return {str(k): clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [clean(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        v = float(obj)
        return None if math.isnan(v) or math.isinf(v) else v
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.strftime("%Y-%m-%d")
    return obj


def write_json(name: str, payload) -> None:
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(clean(payload), f, ensure_ascii=False, separators=(",", ":"))
    print(f"  {name}: {os.path.getsize(path) / 1024:.1f} KB")


# ---------------------------------------------------------------------------
# İl tablosu
# ---------------------------------------------------------------------------
def quantiles(df: pd.DataFrame) -> dict:
    return {
        "q1_osb": float(df["toplam_osb"].quantile(0.25)),
        "q3_osb": float(df["toplam_osb"].quantile(0.75)),
        "q1_pm25": float(df["pm25"].quantile(0.25)),
        "q3_pm25": float(df["pm25"].quantile(0.75)),
    }


def category(row: pd.Series, q: dict) -> str:
    """İl Grupları sayfasıyla aynı çeyreklik kuralları (A, B, yüksek kirlilik/orta sanayi, dengeli)."""
    osb, pm = float(row["toplam_osb"]), float(row["pm25"])
    if osb <= q["q1_osb"] and pm >= q["q3_pm25"]:
        return "A"
    if osb >= q["q3_osb"] and pm >= q["q3_pm25"]:
        return "B"
    if pm >= q["q3_pm25"]:
        return "YK"
    return "N"


def build_provinces(df: pd.DataFrame, q: dict) -> list[dict]:
    cols = [
        "il", "plaka", "bolge", "lat", "lon", "nufus", "pm25", "pm10_cams", "pm25_istasyon_max_2024",
        "toplam_osb", "faal_osb", "osb_alani_hektar", "toplam_parsel", "solunum_olum", "toplam_olum",
        "solunum_olum_100k", "toplam_olum_100k", "solunum_olum_payi", "atfedilen_olum_payi",
        "atfedilen_olum_tahmini", "dso_risk", "dso_limit_kat", "sanayi_tipi",
    ]
    pm_rank = df["pm25"].rank(ascending=True, method="min")
    sol_rank = df["solunum_olum_100k"].rank(ascending=True, method="min")
    nufus_rank = df["nufus"].rank(ascending=False, method="min")
    # Düello yüzdelikleri (yüksek = daha olumlu): düşük PM2.5 ve düşük solunum ölüm hızı
    pct_hava = df["pm25"].rank(ascending=False, pct=True) * 100.0
    pct_solunum = df["solunum_olum_100k"].rank(ascending=False, pct=True) * 100.0
    rows = []
    for i, r in df.iterrows():
        row = {c: r[c] for c in cols}
        row["rakim"] = IL_RAKIM.get(r["il"])
        row["pm_rank"] = int(pm_rank[i])
        row["sol_rank"] = int(sol_rank[i])
        row["nufus_rank"] = int(nufus_rank[i])
        row["pct_hava"] = float(pct_hava[i])
        row["pct_solunum"] = float(pct_solunum[i])
        row["kategori"] = category(r, q)
        summary = generate_city_summary(df, r["il"])
        row["ozet"] = summary["sentences"]
        rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# Korelasyon, regresyon ve mekânsal otokorelasyon
# ---------------------------------------------------------------------------
SCATTER_VARS = {
    "osb_alani_hektar": {"label": "OSB Alanı", "unit": "Hektar"},
    "toplam_osb": {"label": "OSB Sayısı", "unit": "Adet"},
    "rakim": {"label": "Ortalama Rakım", "unit": "Metre"},
    "nufus": {"label": "İl Nüfusu", "unit": "Kişi"},
}


def correlation_stats(df: pd.DataFrame) -> dict:
    work = df.copy()
    work["rakim"] = work["il"].map(IL_RAKIM).fillna(500.0)

    biv = calculate_bivariate_correlation(work["osb_alani_hektar"], work["pm25"])
    biv.pop("x_values", None)
    biv.pop("y_values", None)
    ci_lo, ci_hi = calculate_bootstrap_ci(work["osb_alani_hektar"], work["pm25"], method="spearman")
    biv_pop = calculate_bivariate_correlation(work["nufus"], work["pm25"])

    scatter = {}
    for col, meta in SCATTER_VARS.items():
        reg = stats.linregress(work[col].astype(float), work["pm25"].astype(float))
        scatter[col] = {
            **meta,
            "slope": reg.slope, "intercept": reg.intercept,
            "r": reg.rvalue, "r2": reg.rvalue ** 2, "p": reg.pvalue,
        }

    # Çoklu OLS: PM2.5 = b0 + b1(OSB) + b2(Rakım) + b3(Nüfus/100 bin)
    work["nufus_100k"] = work["nufus"].astype(float) / 100000.0
    y = work["pm25"].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(y)), work[["toplam_osb", "rakim", "nufus_100k"]].to_numpy(dtype=float)])
    beta = np.linalg.solve(X.T @ X, X.T @ y)
    resid = y - X @ beta
    df_resid = len(y) - X.shape[1]
    sse = float(resid @ resid)
    sst = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - sse / sst
    adj_r2 = 1 - (1 - r2) * ((len(y) - 1) / df_resid)
    se = np.sqrt(np.maximum(np.diag((sse / df_resid) * np.linalg.inv(X.T @ X)), 1e-12))
    t_vals = beta / se
    p_vals = 2 * (1 - stats.t.cdf(np.abs(t_vals), df=df_resid))
    ols = {
        "n": len(y), "k": 3, "df_resid": df_resid, "r2": r2, "adj_r2": adj_r2,
        "terms": [
            {"name": n, "coef": b, "se": s, "t": t, "p": p}
            for n, b, s, t, p in zip(
                ["Sabit Terim (β₀)", "OSB Sayısı (β₁)", "Ortalama Rakım (β₂)", "İl Nüfusu (100 Bin Kişi) (β₃)"],
                beta, se, t_vals, p_vals,
            )
        ],
    }

    # Global Moran's I: satır standardize ters mesafe ağırlıkları + permütasyon testi
    coords = work[["lat", "lon"]].to_numpy(dtype=float)
    dists = np.sqrt(((coords[:, None, :] - coords[None, :, :]) ** 2).sum(-1))
    np.fill_diagonal(dists, np.inf)
    W = 1.0 / dists
    np.fill_diagonal(W, 0.0)
    W = W / W.sum(axis=1, keepdims=True)
    pm = work["pm25"].to_numpy(dtype=float)
    z = (pm - pm.mean()) / pm.std(ddof=0)
    wz = W @ z
    sum_z2 = float((z ** 2).sum())
    moran_i = float((z * wz).sum() / sum_z2)
    rng = np.random.default_rng(MORAN_SEED)
    perm = np.array([np.sum(zp * (W @ zp)) / sum_z2
                     for zp in (rng.permutation(z) for _ in range(MORAN_PERMUTATIONS))])
    moran_p = float((np.sum(perm >= moran_i) + 1) / (MORAN_PERMUTATIONS + 1))

    def quad(zi, wzi):
        if zi >= 0 and wzi >= 0:
            return "HH"
        if zi < 0 and wzi < 0:
            return "LL"
        if zi >= 0:
            return "HL"
        return "LH"

    moran = {
        "I": moran_i, "p": moran_p, "permutations": MORAN_PERMUTATIONS,
        "points": [
            {"il": il, "bolge": b, "pm25": v, "z": zi, "wz": wzi, "q": quad(zi, wzi)}
            for il, b, v, zi, wzi in zip(work["il"], work["bolge"], pm, z, wz)
        ],
    }

    return {
        "osb_pm25": {**biv, "ci_lo": ci_lo, "ci_hi": ci_hi},
        "nufus_pm25": {"spearman_rho": biv_pop["spearman_rho"], "spearman_p": biv_pop["spearman_p"]},
        "scatter": scatter,
        "ols": ols,
        "moran": moran,
    }


def regions_stats(df: pd.DataFrame) -> dict:
    summary = aggregate_by_region(df, pollutant="pm25")
    rows = []
    for _, r in summary.iterrows():
        sub = df[df["bolge"] == r["bolge"]]
        mx = sub.loc[sub["pm25"].idxmax()]
        rows.append({
            "bolge": r["bolge"], "il_sayisi": r["il_sayisi"], "ortalama": float(sub["pm25"].mean()),
            "medyan": r["medyan"], "std": r["std"], "toplam_osb": r["toplam_osb"],
            "faal_osb": int(sub["faal_osb"].sum()),
            "solunum_100k": r["bolgesel_solunum_olum_100k"], "max_il": mx["il"], "max_pm25": float(mx["pm25"]),
        })
    anova = run_regional_anova(df, group_col="bolge", val_col="pm25")
    anova = {k: v for k, v in anova.items() if not isinstance(v, (pd.DataFrame, pd.Series))}
    return {"rows": rows, "anova": anova}


# ---------------------------------------------------------------------------
# Günlük seriler
# ---------------------------------------------------------------------------
def daily_payload() -> dict:
    city = load_city_daily()
    nat = get_national_timeseries(90)
    if city is None or city.empty:
        return {"dates": [], "cities": {}, "national": []}
    city = city.sort_values("date")
    dates = sorted(city["date"].dt.strftime("%Y-%m-%d").unique())
    pivot = city.pivot_table(index=city["date"].dt.strftime("%Y-%m-%d"), columns="il", values="pm25").reindex(dates)
    cities = {il: [None if pd.isna(v) else round(float(v), 1) for v in pivot[il]] for il in pivot.columns}
    national = [
        {"date": d.strftime("%Y-%m-%d"), "pm25": r.pm25, "min": r.pm25_min, "max": r.pm25_max, "ma7": r.pm25_ma7}
        for d, r in zip(nat["date"], nat.itertuples())
    ]
    return {"dates": dates, "cities": cities, "national": national}


# ---------------------------------------------------------------------------
# Harita geometrisi (GeoJSON -> SVG yolları)
# ---------------------------------------------------------------------------
MAP_WIDTH = 1000.0
MIN_STEP = 0.6  # SVG biriminde; daha yakın noktalar atlanır (dosya boyutu için)


def map_payload() -> dict:
    with open(os.path.join(ROOT_DIR, "data", "tr-cities.json"), encoding="utf-8") as f:
        geo = json.load(f)

    def rings(geom):
        if geom["type"] == "Polygon":
            return geom["coordinates"]
        return [ring for poly in geom["coordinates"] for ring in poly]

    all_pts = [pt for feat in geo["features"] for ring in rings(feat["geometry"]) for pt in ring]
    lon_min = min(p[0] for p in all_pts)
    lon_max = max(p[0] for p in all_pts)
    lat_min = min(p[1] for p in all_pts)
    lat_max = max(p[1] for p in all_pts)
    kx = math.cos(math.radians((lat_min + lat_max) / 2))
    scale = MAP_WIDTH / ((lon_max - lon_min) * kx)
    height = (lat_max - lat_min) * scale

    def proj(lon, lat):
        return (lon - lon_min) * kx * scale, (lat_max - lat) * scale

    provinces = []
    for feat in geo["features"]:
        parts = []
        for ring in rings(feat["geometry"]):
            pts = [proj(*p[:2]) for p in ring]
            kept = [pts[0]]
            for x, y in pts[1:]:
                if math.hypot(x - kept[-1][0], y - kept[-1][1]) >= MIN_STEP:
                    kept.append((x, y))
            if len(kept) < 3:
                continue
            parts.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in kept) + "Z")
        name = feat["properties"]["name"]
        lat, lon = KOORDINATLAR[name]
        cx, cy = proj(lon, lat)
        provinces.append({"il": name, "d": "".join(parts), "cx": round(cx, 1), "cy": round(cy, 1)})
    return {"width": MAP_WIDTH, "height": round(height, 1), "provinces": provinces}


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="CAMS günlük verisini API'den yenile")
    args = ap.parse_args()

    df = build_master_dataset()
    if args.refresh:
        print(refresh_city_daily(df, force=True))
    df.to_csv(os.path.join(ROOT_DIR, "data", "master_data.csv"), index=False, encoding="utf-8")

    os.makedirs(OUT_DIR, exist_ok=True)
    q = quantiles(df)
    stations = pd.read_csv(os.path.join(ROOT_DIR, "data", "kara_rapor_2025_istasyon.csv"), encoding="utf-8")
    date_info = get_dataset_date_info()

    print("JSON dosyaları yazılıyor:")
    write_json("provinces.json", build_provinces(df, q))
    write_json("stats.json", {
        "quantiles": q,
        "correlation": correlation_stats(df),
        "regions": regions_stats(df),
    })
    write_json("daily.json", daily_payload())
    write_json("map.json", map_payload())
    write_json("meta.json", {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "cams_year": CAMS_YILI,
        "daily_start": date_info["start_date"],
        "daily_end": date_info["end_date"],
        "sources": date_info["sources"],
        "tiers": KIRLILIK_KADEMELERI,
        "who": DSO_KILAVUZ_DEGERLERI["pm25"],
        "airq": {"rr_per_10": AIRQ_RR_PER_10, "counterfactual": AIRQ_KARSI_OLGU},
        "stations": stations.to_dict(orient="records"),
    })


if __name__ == "__main__":
    main()
