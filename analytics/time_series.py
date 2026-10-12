"""
Zaman Serisi Analiz Motoru
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple

def analyze_time_series_window(
    df_ts: pd.DataFrame, 
    window_days: int = 30,
    pollutant: str = "pm25"
) -> Dict[str, Any]:
    """
    Belirli bir gün penceresi (7, 30, 90 gün) için zaman serisini analiz eder.
    Trend yönünü, hareketli ortalamayı, periyotlar arası değişimi hesaplar.
    """
    if df_ts.empty:
        return {}
        
    df = df_ts.copy()
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        
    if pollutant not in df.columns:
        pollutant = "pm25"
        
    # Son window_days kadar günü al
    latest_date = df["date"].max()
    start_date = latest_date - pd.Timedelta(days=window_days)
    
    current_window = df[df["date"] >= start_date].copy()
    
    # Karşılaştırma için bir önceki dönemi al (örneğin son 30 güne karşılık önceki 30 gün)
    prev_start_date = start_date - pd.Timedelta(days=window_days)
    prev_window = df[(df["date"] >= prev_start_date) & (df["date"] < start_date)].copy()
    
    cur_mean = float(current_window[pollutant].mean()) if not current_window.empty else 0.0
    cur_median = float(current_window[pollutant].median()) if not current_window.empty else 0.0
    cur_min = float(current_window[pollutant].min()) if not current_window.empty else 0.0
    cur_max = float(current_window[pollutant].max()) if not current_window.empty else 0.0
    
    prev_mean = float(prev_window[pollutant].mean()) if not prev_window.empty else cur_mean
    
    # Yüzdesel değişim
    if prev_mean > 0:
        delta_pct = round(((cur_mean - prev_mean) / prev_mean) * 100, 1)
    else:
        delta_pct = 0.0
        
    # Doğrusal regresyon eğimi (trend yönü)
    if len(current_window) > 2:
        x = np.arange(len(current_window))
        y = current_window[pollutant].values
        slope, _ = np.polyfit(x, y, 1)
        trend_direction = "Artış Eğiliminde" if slope > 0.05 else ("Azalış Eğiliminde" if slope < -0.05 else "Yatay / Kararlı")
    else:
        slope = 0.0
        trend_direction = "Yetersiz Veri"
        
    return {
        "window_days": window_days,
        "sample_count": len(current_window),
        "current_mean": round(cur_mean, 2),
        "current_median": round(cur_median, 2),
        "min_value": round(cur_min, 2),
        "max_value": round(cur_max, 2),
        "prev_mean": round(prev_mean, 2),
        "delta_pct": delta_pct,
        "slope": round(float(slope), 3),
        "trend_direction": trend_direction,
        "window_df": current_window
    }
