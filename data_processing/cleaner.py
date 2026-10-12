"""
Veri Temizleme ve Doğrulama Modülü
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any

def tr_normalize(text: str) -> str:
    """Türkçe arama ve metin karşılaştırması için harf normalizasyonu."""
    if not isinstance(text, str):
        return ""
    mapping = {
        'İ': 'i', 'I': 'i', 'ı': 'i',
        'ş': 's', 'Ş': 's',
        'ğ': 'g', 'Ğ': 'g',
        'ü': 'u', 'Ü': 'u',
        'ö': 'o', 'Ö': 'o',
        'ç': 'c', 'Ç': 'c'
    }
    t = str(text)
    for k, v in mapping.items():
        t = t.replace(k, v)
    return t.lower().replace('\u0307', '').strip()

def validate_and_clean_air_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Hava kalitesi ölçümlerini doğrular, aykırı değerleri (outliers) tespit eder
    ve eksik değer oranlarını raporlar. Orijinal veriyi bozmadan temiz bir kopyasını üretir.
    """
    df_clean = df.copy()
    report = {
        "total_provinces": len(df_clean),
        "missing_pm25": int(df_clean["pm25"].isna().sum()) if "pm25" in df_clean.columns else 0,
        "outliers": []
    }
    
    # PM2.5 için makul fiziksel sınırlar: 0 ile 500 µg/m³
    if "pm25" in df_clean.columns:
        invalid_mask = (df_clean["pm25"] < 0) | (df_clean["pm25"] > 500)
        if invalid_mask.any():
            report["outliers"].extend(
                df_clean.loc[invalid_mask, "il"].tolist() if "il" in df_clean.columns else []
            )
            df_clean.loc[invalid_mask, "pm25"] = np.nan
            
        # Z-skor aykırı değer analizi (|z| > 3.0)
        mean_pm = df_clean["pm25"].mean()
        std_pm = df_clean["pm25"].std()
        if std_pm > 0:
            z_scores = (df_clean["pm25"] - mean_pm) / std_pm
            statistical_outliers = df_clean[z_scores.abs() > 3.0]
            if not statistical_outliers.empty:
                report["statistical_outliers_pm25"] = statistical_outliers["il"].tolist()
            else:
                report["statistical_outliers_pm25"] = []
                
    report["data_completeness_pct"] = round(
        (1 - (report["missing_pm25"] / max(len(df_clean), 1))) * 100, 2
    )
    return df_clean, report

def filter_by_region_and_search(
    df: pd.DataFrame, 
    region: str = "Tüm Türkiye", 
    search_query: str = ""
) -> pd.DataFrame:
    """
    Bölge ve il adına göre dinamik filtreleme yapar.
    """
    filtered = df.copy()
    if region and region != "Tüm Türkiye":
        filtered = filtered[filtered["bolge"] == region]
        
    if search_query and search_query.strip():
        q_norm = tr_normalize(search_query)
        filtered = filtered[filtered["il"].apply(lambda x: q_norm in tr_normalize(x))]
        
    return filtered
