"""
İl Bazlı Yıllık PM2.5 / PM10 Ortalaması (Copernicus CAMS / Open-Meteo)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

- 81 il merkez koordinatı için seçilen takvim yılının TÜM saatlik PM2.5 ve PM10
  model değerlerini çeker (kış/ısınma sezonu dahil 12 ay).
- Saatlik veri tamlığı %75'in altındaysa il değeri boş bırakılır (AB/DSÖ veri tamlığı kuralı).
- Sonuç `data/cams_annual_<yil>.csv` dosyasına yazılır ve master tablonun ana PM kaynağıdır.

ÖNEMLİ: Bu değerler istasyon ölçümü değil, CAMS atmosfer modeli çıktısıdır (~10 km ızgara,
il merkezi noktası). İstasyon ölçümlerinden genellikle düşük çıkar; arayüzde her zaman
"CAMS model" olarak etiketlenir. İstasyon karşılaştırması için bkz. `data/kara_rapor_2025_istasyon.csv`.

Manuel güncelleme:  python -m data_sources.cams_annual_connector 2025
"""

from __future__ import annotations

import os
import sys

import pandas as pd
import requests

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
MIN_COMPLETENESS = 0.75
DEFAULT_YEAR = 2025


def annual_cache_path(year: int = DEFAULT_YEAR) -> str:
    return os.path.join(ROOT_DIR, "data", f"cams_annual_{year}.csv")


def hourly_to_annual(hourly: dict, il: str, year: int) -> dict:
    """Bir ilin saatlik yanıtını yıllık ortalamaya ve veri tamlığına çevirir."""
    times = hourly.get("time") or []
    n_expected = len(times)
    out = {"il": il, "yil": year}
    for src, dst in (("pm2_5", "pm25_cams"), ("pm10", "pm10_cams")):
        s = pd.to_numeric(pd.Series(hourly.get(src, [None] * n_expected)), errors="coerce")
        completeness = s.notna().sum() / n_expected if n_expected else 0.0
        out[f"{dst}_tamlik"] = round(float(completeness), 3)
        out[dst] = round(float(s.mean()), 2) if completeness >= MIN_COMPLETENESS else None
    return out


def fetch_annual(cities: pd.DataFrame, year: int = DEFAULT_YEAR, chunk: int = 20,
                 timeout: int = 60) -> pd.DataFrame:
    """`cities` (il, lat, lon) için yıllık ortalamaları çeker. Hata durumunda istisna fırlatır."""
    rows = cities[["il", "lat", "lon"]].dropna().reset_index(drop=True)
    records = []
    for start in range(0, len(rows), chunk):
        part = rows.iloc[start:start + chunk]
        params = {
            "latitude": ",".join(f"{v:.4f}" for v in part["lat"]),
            "longitude": ",".join(f"{v:.4f}" for v in part["lon"]),
            "hourly": "pm2_5,pm10",
            "start_date": f"{year}-01-01",
            "end_date": f"{year}-12-31",
            "timezone": "Europe/Istanbul",
        }
        resp = requests.get(BASE_URL, params=params, timeout=timeout)
        resp.raise_for_status()
        payload = resp.json()
        if isinstance(payload, dict):
            payload = [payload]
        if len(payload) != len(part):
            raise ValueError(f"Beklenen {len(part)} konum, gelen {len(payload)}")
        for (_, row), item in zip(part.iterrows(), payload):
            records.append(hourly_to_annual(item.get("hourly", {}), row["il"], year))
    return pd.DataFrame(records)


def load_annual(year: int = DEFAULT_YEAR) -> pd.DataFrame:
    path = annual_cache_path(year)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"CAMS yıllık dosyası bulunamadı: {path}. "
            f"Oluşturmak için: python -m data_sources.cams_annual_connector {year}"
        )
    return pd.read_csv(path, encoding="utf-8")


if __name__ == "__main__":
    sys.path.insert(0, ROOT_DIR)
    from data_sources.constants import PLAKA_ILLER, KOORDINATLAR

    yil = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_YEAR
    iller = pd.DataFrame({"il": [PLAKA_ILLER[i] for i in range(1, 82)]})
    iller["lat"] = iller["il"].map(lambda x: KOORDINATLAR[x][0])
    iller["lon"] = iller["il"].map(lambda x: KOORDINATLAR[x][1])
    df = fetch_annual(iller, yil)
    df.to_csv(annual_cache_path(yil), index=False, encoding="utf-8")
    print(f"{len(df)} il yazıldı -> {annual_cache_path(yil)}")
    print(df.describe().round(2))
