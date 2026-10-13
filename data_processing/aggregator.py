"""
Veri Agregasyon ve Gösterge Hesaplama Modülü
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List

def aggregate_by_region(df: pd.DataFrame, pollutant: str = "pm25") -> pd.DataFrame:
    """
    7 Coğrafi bölge bazında istatistiksel özet tablosu üretir.
    """
    if pollutant not in df.columns:
        pollutant = "pm25"
        
    grouped = df.groupby("bolge").agg(
        il_sayisi=("il", "count"),
        ortalama=(pollutant, "mean"),
        medyan=(pollutant, "median"),
        std=(pollutant, "std"),
        min_deger=(pollutant, "min"),
        max_deger=(pollutant, "max"),
        toplam_nufus=("nufus", "sum"),
        toplam_osb=("toplam_osb", "sum"),
        toplam_solunum_olum=("solunum_olum", "sum")
    ).reset_index()
    
    # Bölgesel solunum ölüm oranı (100k kişi başı)
    grouped["bolgesel_solunum_olum_100k"] = (
        (grouped["toplam_solunum_olum"] / grouped["toplam_nufus"]) * 100_000
    ).round(1)
    
    grouped["ortalama"] = grouped["ortalama"].round(2)
    grouped["medyan"] = grouped["medyan"].round(2)
    grouped["std"] = grouped["std"].round(2)
    
    return grouped.sort_values(by="ortalama", ascending=False)

def get_dso_compliance_stats(df: pd.DataFrame, pollutant: str = "pm25") -> Dict[str, Any]:
    """
    DSÖ (WHO) kılavuz limitlerine uyum oranlarını hesaplar.
    """
    total = len(df)
    if total == 0:
        return {}
        
    val_col = df[pollutant] if pollutant in df.columns else df["pm25"]
    
    # DSÖ Yıllık Kılavuz Limiti: PM2.5 = 5.0 µg/m³
    threshold = 5.0
    
    exceed_count = int((val_col > threshold).sum())
    safe_count = total - exceed_count
    
    # Risk kategorileri
    critical_count = int((val_col > 50.0).sum())
    high_count = int(((val_col > 25.0) & (val_col <= 50.0)).sum())
    moderate_count = int(((val_col > 10.0) & (val_col <= 25.0)).sum())
    good_count = int((val_col <= 10.0).sum())
    
    return {
        "total_provinces": total,
        "threshold_ug_m3": threshold,
        "exceeding_count": exceed_count,
        "exceeding_pct": round((exceed_count / total) * 100, 1),
        "compliant_count": safe_count,
        "compliant_pct": round((safe_count / total) * 100, 1),
        "risk_breakdown": {
            "Düşük Risk (<=10)": good_count,
            "Orta Risk (10-25)": moderate_count,
            "Yüksek Risk (25-50)": high_count,
            "Kritik Risk (>50)": critical_count
        }
    }
