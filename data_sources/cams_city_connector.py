"""
İl Bazlı Günlük Hava Kalitesi Bağlayıcısı (Copernicus CAMS / Open-Meteo)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

- 81 il merkez koordinatı için saatlik PM2.5, PM10 ve NO₂ model değerlerini çeker.
- Saatlik değerleri günlük ortalamaya çevirir (yalnızca en az 18 saati dolu günler).
- Bugün ve sonrası (tamamlanmamış gün / tahmin) dışarıda bırakılır.
- Sonucu `data/daily_city_air_quality.csv` dosyasında önbellekler.

ÖNEMLİ: Bu değerler istasyon ölçümü değil, CAMS atmosfer modeli çıktısıdır.
Arayüzde her zaman "CAMS model" olarak etiketlenir.
"""

from __future__ import annotations

import logging
import os
import time
from datetime import date, datetime, timedelta
from typing import Optional

import pandas as pd
import requests

logger = logging.getLogger("havaatlasi.cams")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CITY_CACHE_FILE = os.path.join(ROOT_DIR, "data", "daily_city_air_quality.csv")
BASE_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
MIN_HOURS_PER_DAY = 18
# Önbellek bu süreden yeniyse "yenile" isteğinde API'ye tekrar gidilmez.
MIN_REFRESH_INTERVAL_SEC = 3 * 3600


def hourly_to_daily(hourly: dict, il: str, today: Optional[date] = None) -> pd.DataFrame:
    """Open-Meteo saatlik yanıtını günlük ortalamalara dönüştürür."""
    today = today or date.today()
    times = hourly.get("time") or []
    if not times:
        return pd.DataFrame(columns=["date", "il", "pm25", "pm10", "no2", "n_hours"])
    df = pd.DataFrame({
        "datetime": pd.to_datetime(times),
        "pm25": pd.to_numeric(pd.Series(hourly.get("pm2_5", [None] * len(times))), errors="coerce"),
        "pm10": pd.to_numeric(pd.Series(hourly.get("pm10", [None] * len(times))), errors="coerce"),
        "no2": pd.to_numeric(pd.Series(hourly.get("nitrogen_dioxide", [None] * len(times))), errors="coerce"),
    })
    df["date"] = df["datetime"].dt.date
    df = df[df["date"] < today]
    daily = df.groupby("date").agg(
        pm25=("pm25", "mean"), pm10=("pm10", "mean"), no2=("no2", "mean"),
        n_hours=("pm25", "count"),
    ).reset_index()
    daily = daily[daily["n_hours"] >= MIN_HOURS_PER_DAY]
    daily["il"] = il
    for c in ("pm25", "pm10", "no2"):
        daily[c] = daily[c].round(2)
    daily["date"] = pd.to_datetime(daily["date"])
    return daily[["date", "il", "pm25", "pm10", "no2", "n_hours"]]


def fetch_city_daily(cities: pd.DataFrame, past_days: int = 92, chunk: int = 27,
                     timeout: int = 25) -> pd.DataFrame:
    """`cities` (il, lat, lon) için günlük değerleri çeker. Hata durumunda istisna fırlatır."""
    frames = []
    rows = cities[["il", "lat", "lon"]].dropna().reset_index(drop=True)
    for start in range(0, len(rows), chunk):
        part = rows.iloc[start:start + chunk]
        params = {
            "latitude": ",".join(f"{v:.4f}" for v in part["lat"]),
            "longitude": ",".join(f"{v:.4f}" for v in part["lon"]),
            "hourly": "pm10,pm2_5,nitrogen_dioxide",
            "past_days": past_days,
            "forecast_days": 1,
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
            frames.append(hourly_to_daily(item.get("hourly", {}), row["il"]))
    if not frames:
        raise ValueError("CAMS yanıtı boş")
    out = pd.concat(frames, ignore_index=True)
    if out.empty:
        raise ValueError("CAMS yanıtında tam gün verisi yok")
    return out


def load_city_daily() -> Optional[pd.DataFrame]:
    """Önbellekteki il bazlı günlük veriyi okur (yoksa None)."""
    if not os.path.exists(CITY_CACHE_FILE):
        return None
    try:
        df = pd.read_csv(CITY_CACHE_FILE, encoding="utf-8")
        df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as exc:  # pragma: no cover - bozuk dosya
        logger.warning("CAMS önbelleği okunamadı: %s", exc)
        return None


def cache_age_seconds() -> Optional[float]:
    if not os.path.exists(CITY_CACHE_FILE):
        return None
    return time.time() - os.path.getmtime(CITY_CACHE_FILE)


def refresh_city_daily(cities: pd.DataFrame, force: bool = False) -> tuple[str, str]:
    """
    Önbelleği gerekiyorsa yeniler.
    Dönüş: (durum, mesaj) — durum: 'ok' | 'skipped' | 'error'
    """
    age = cache_age_seconds()
    if not force and age is not None and age < MIN_REFRESH_INTERVAL_SEC:
        mins = int(age // 60)
        return "skipped", f"CAMS önbelleği {mins} dk önce güncellendi; tekrar istek gönderilmedi."
    try:
        df = fetch_city_daily(cities)
        os.makedirs(os.path.dirname(CITY_CACHE_FILE), exist_ok=True)
        df.to_csv(CITY_CACHE_FILE, index=False, encoding="utf-8")
        n_city = df["il"].nunique()
        return "ok", (f"CAMS verisi güncellendi: {n_city} il, "
                      f"{df['date'].min():%d.%m.%Y} – {df['date'].max():%d.%m.%Y}.")
    except Exception as exc:
        logger.error("CAMS güncellemesi başarısız: %s", exc)
        return "error", f"CAMS verisi alınamadı ({type(exc).__name__}). Önbellekteki veri kullanılıyor."


def cache_updated_at() -> Optional[datetime]:
    if not os.path.exists(CITY_CACHE_FILE):
        return None
    return datetime.fromtimestamp(os.path.getmtime(CITY_CACHE_FILE))


if __name__ == "__main__":  # Manuel güncelleme: python -m data_sources.cams_city_connector
    logging.basicConfig(level=logging.INFO)
    master = pd.read_csv(os.path.join(ROOT_DIR, "data", "master_data.csv"), encoding="utf-8")
    print(refresh_city_daily(master, force=True))
