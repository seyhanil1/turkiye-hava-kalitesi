"""
Betimsel İstatistik Hesaplama Motoru
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Union

def calculate_descriptive_stats(data: Union[pd.Series, np.ndarray, list]) -> Dict[str, Any]:
    """
    Verilen sayısal serinin kapsamlı betimsel istatistiklerini hesaplar:
    Ortalama, medyan, standart sapma, varyans, IQR, yüzdelikler, basıklık, çarpıklık.
    """
    s = pd.Series(data).dropna()
    total_obs = len(pd.Series(data))
    valid_obs = len(s)
    
    if valid_obs == 0:
        return {
            "count": 0, "valid_count": 0, "missing_count": total_obs,
            "coverage_pct": 0.0, "mean": 0.0, "median": 0.0, "std": 0.0,
            "var": 0.0, "iqr": 0.0, "min": 0.0, "max": 0.0,
            "p10": 0.0, "p25": 0.0, "p50": 0.0, "p75": 0.0, "p90": 0.0,
            "skewness": 0.0, "kurtosis": 0.0
        }
        
    mean_val = float(s.mean())
    median_val = float(s.median())
    std_val = float(s.std(ddof=1)) if valid_obs > 1 else 0.0
    var_val = float(s.var(ddof=1)) if valid_obs > 1 else 0.0
    
    q25 = float(s.quantile(0.25))
    q75 = float(s.quantile(0.75))
    iqr_val = float(q75 - q25)
    
    p10 = float(s.quantile(0.10))
    p90 = float(s.quantile(0.90))
    min_val = float(s.min())
    max_val = float(s.max())
    
    skew_val = float(s.skew()) if valid_obs > 2 else 0.0
    kurt_val = float(s.kurtosis()) if valid_obs > 3 else 0.0
    
    coverage_pct = round((valid_obs / max(total_obs, 1)) * 100, 2)
    
    return {
        "count": total_obs,
        "valid_count": valid_obs,
        "missing_count": total_obs - valid_obs,
        "coverage_pct": coverage_pct,
        "mean": round(mean_val, 2),
        "median": round(median_val, 2),
        "std": round(std_val, 2),
        "var": round(var_val, 2),
        "iqr": round(iqr_val, 2),
        "min": round(min_val, 2),
        "max": round(max_val, 2),
        "p10": round(p10, 2),
        "p25": round(q25, 2),
        "p50": round(median_val, 2),
        "p75": round(q75, 2),
        "p90": round(p90, 2),
        "skewness": round(skew_val, 2),
        "kurtosis": round(kurt_val, 2)
    }
