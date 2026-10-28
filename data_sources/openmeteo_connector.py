"""
Open-Meteo Air Quality (Copernicus CAMS) Bağlayıcısı
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

Özellikler:
- Avrupa CAMS (Copernicus Atmosphere Monitoring Service) verileri.
- Tek koordinat için geçmiş saatlik/günlük PM2.5 zaman serisi.
- Ulusal seri: il bazlı CAMS önbelleğinin nüfus ağırlıklı ortalaması (sentetik yedek yok).
"""

import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple


class OpenMeteoAirQualityConnector:
    BASE_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
    
    def __init__(self, timeout: int = 8):
        self.timeout = timeout
        
    def fetch_city_timeseries(
        self, 
        lat: float = 39.9334, 
        lon: float = 32.8597, 
        past_days: int = 90
    ) -> Optional[pd.DataFrame]:
        """
        Belirtilen koordinat için son N günlük hava kalitesi zaman serisini çeker.
        """
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "pm2_5",
            "past_days": past_days,
            "timezone": "auto"
        }
        try:
            resp = requests.get(self.BASE_URL, params=params, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                hourly = data.get("hourly", {})
                times = hourly.get("time", [])
                if not times:
                    return None
                    
                df_hourly = pd.DataFrame({
                    "datetime": pd.to_datetime(times),
                    "pm25": hourly.get("pm2_5", [])
                })
                
                # Günlük agregasyon
                df_hourly["date"] = df_hourly["datetime"].dt.date
                df_daily = df_hourly.groupby("date").agg(
                    pm25=("pm25", "mean"),
                    pm25_min=("pm25", "min"),
                    pm25_max=("pm25", "max")
                ).reset_index()
                
                df_daily["date"] = pd.to_datetime(df_daily["date"])
                df_daily = df_daily.sort_values("date")
                df_daily["pm25_ma7"] = df_daily["pm25"].rolling(7, min_periods=1).mean().round(2)
                df_daily["pm25"] = df_daily["pm25"].round(2)
                return df_daily
        except Exception as e:
            # Ağ hatası veya zaman aşımında sessizce yakala
            pass
        return None

def get_national_timeseries(past_days: int = 90) -> pd.DataFrame:
    """
    Türkiye geneli günlük PM2.5 serisi: 81 il merkezinin CAMS günlük değerlerinin
    NÜFUS AĞIRLIKLI ortalaması (data/daily_city_air_quality.csv üzerinden).

    Veri yoksa boş DataFrame döner; sentetik/uydurma yedek seri ÜRETİLMEZ.
    Arayüz boş sonuçta "veri yok" göstermelidir.
    """
    from data_sources.constants import NUFUSLAR

    cols = ["date", "pm25", "pm25_min", "pm25_max", "pm25_ma7"]
    city_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "data", "daily_city_air_quality.csv")
    if not os.path.exists(city_file):
        return pd.DataFrame(columns=cols)
    try:
        df = pd.read_csv(city_file, encoding="utf-8")
    except Exception:
        return pd.DataFrame(columns=cols)
    df["date"] = pd.to_datetime(df["date"])
    df["w"] = df["il"].map(NUFUSLAR)
    df = df.dropna(subset=["pm25", "w"])
    if df.empty:
        return pd.DataFrame(columns=cols)
    cutoff = df["date"].max() - timedelta(days=past_days)
    df = df[df["date"] > cutoff]
    out = df.groupby("date").apply(
        lambda g: pd.Series({
            "pm25": np.average(g["pm25"], weights=g["w"]),
            "pm25_min": g["pm25"].min(),
            "pm25_max": g["pm25"].max(),
        }),
        include_groups=False,
    ).reset_index().sort_values("date")
    out["pm25_ma7"] = out["pm25"].rolling(7, min_periods=1).mean().round(2)
    for c in ("pm25", "pm25_min", "pm25_max"):
        out[c] = out[c].round(2)
    return out[cols]
