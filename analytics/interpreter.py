"""
Veri Bilimi Yorum Motoru (Data Science Commentary Engine)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

Özellikler:
- Gerçek Python analizlerine dayalı dinamik, şeffaf ve deterministik içgörü üretimi.
- Harici yapay zeka API'si bağımlılığı olmadan, gerçek istatistiksel sonuçları yorumlar.
- Kirlilik tepe noktaları, DSÖ sınır aşımı, sanayi ilişkisi ve topoğrafik/enversiyon faktörleri.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List

def generate_data_science_notes(
    df: pd.DataFrame, 
    pollutant: str = "pm25",
    ts_summary: Dict[str, Any] = None
) -> List[Dict[str, str]]:
    """
    Seçilen veri kümesi ve kirleticiye göre veri bilimi yorum ve içgörü kartları üretir.
    """
    if df.empty or pollutant not in df.columns:
        return [{
            "title": "Veri Yetersiz",
            "content": "Seçilen filtre kriterlerine uygun yeterli gözlem bulunamadı.",
            "category": "Uyarı"
        }]
        
    notes = []
    
    # 1. Kirlilik Uç Değerleri ve Kat Farkı
    max_row = df.loc[df[pollutant].idxmax()]
    min_row = df.loc[df[pollutant].idxmin()]
    max_val = max_row[pollutant]
    min_val = min_row[pollutant]
    multiplier = round(max_val / max(min_val, 0.1), 1)
    
    notes.append({
        "title": "Bölgesel Uç Noktalar ve Eşitsizlik",
        "category": "Coğrafi Dağılım",
        "badge": "🚨 Kritik Fark",
        "content": (
            f"Analiz edilen bölgede en yüksek {pollutant.upper()} kirliliği **{max_row['il']}** ilinde "
            f"({max_val} µg/m³), en düşük ise **{min_row['il']}** ilinde ({min_val} µg/m³) ölçülmüştür. "
            f"En kirli ve en temiz il arasında yaklaşık **{multiplier} katlık** kirlilik maruziyeti farkı bulunmaktadır."
        )
    })
    
    # 2. DSÖ (WHO) Kılavuz Limit Değerlendirmesi
    dso_limit = 5.0 if pollutant == "pm25" else (15.0 if pollutant == "pm10" else 10.0)
    exceeding_count = (df[pollutant] > dso_limit).sum()
    exceeding_pct = round((exceeding_count / len(df)) * 100, 1)
    avg_val = round(df[pollutant].mean(), 1)
    
    notes.append({
        "title": "DSÖ Kılavuz Değerleri Uyum Durumu",
        "category": "Halk Sağlığı",
        "badge": "🛡️ Kılavuz Değer",
        "content": (
            f"İncelenen {len(df)} ilden **{exceeding_count} tanesi (%{exceeding_pct})** Dünya Sağlık Örgütü'nün "
            f"yıllık {dso_limit} µg/m³ kılavuz limitini aşmaktadır. Ortalama konsantrasyon ({avg_val} µg/m³), "
            f"DSÖ hedef değerinin yaklaşık **{round(avg_val / dso_limit, 1)} katı** seviyesindedir."
        )
    })
    
    # 3. Sanayi ve Toplam Parsel Korelasyon Notu
    if "toplam_parsel" in df.columns and len(df) > 5:
        corr = df[pollutant].corr(df["toplam_parsel"])
        if not np.isnan(corr):
            notes.append({
                "title": "Sanayi Yoğunluğu ve Kirletici Yükü",
                "category": "İstatistiksel Çıkarım",
                "badge": "🏭 Sanayi Analizi",
                "content": (
                    f"OSB sanayi parsel sayısı ile {pollutant.upper()} arasında "
                    f"**r = {corr:.2f}** düzeyinde doğrusal korelasyon tespit edilmiştir. "
                    "Ancak korelasyon doğrudan nedensellik (causation) anlamına gelmez; "
                    "meteorolojik faktörler, kış aylarındaki ısınma yakıtları ve coğrafi çanak topoğrafyası "
                    "da kirlilik konsantrasyonunu belirleyen temel üçüncü değişkenlerdir."
                )
            })
            
    # 4. Zaman Serisi Eğilimi (Eğer aktarılmışsa)
    if ts_summary and "delta_pct" in ts_summary:
        direction = ts_summary.get("trend_direction", "Kararlı")
        delta = ts_summary.get("delta_pct", 0.0)
        sign = "+" if delta > 0 else ""
        notes.append({
            "title": f"Dönemsel Trend: Son {ts_summary.get('window_days', 30)} Gün",
            "category": "Zaman Serisi",
            "badge": "📈 Trend",
            "content": (
                f"Son {ts_summary.get('window_days', 30)} günlük hareketli ortalama verisi incelendiğinde, "
                f"ölçümlerde önceki döneme kıyasla **%{sign}{delta}** oranında bir değişim ve "
                f"**{direction}** seyir saptanmıştır."
            )
        })
        
    return notes
