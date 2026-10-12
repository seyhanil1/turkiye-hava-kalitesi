"""
Türkiye Coğrafi Harita Bileşeni (GeoJSON Choropleth)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional

from visualization.theme import AQI_COLOR_SCALE

GEOJSON_PATH = "data/tr-cities.json"

def load_geojson() -> dict:
    """Türkiye 81 il sınırları GeoJSON dosyasını yükler."""
    if not os.path.exists(GEOJSON_PATH):
        raise FileNotFoundError(f"GeoJSON dosyası bulunamadı: {GEOJSON_PATH}")
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def create_turkey_choropleth_map(
    df: pd.DataFrame, 
    pollutant: str = "pm25",
    title: str = "Türkiye Hava Kalitesi Haritası"
) -> go.Figure:
    """
    81 ilin sınırlarını ve seçilen kirleticiye göre kirlilik yoğunluğunu gösteren
    etkileşimli GeoJSON koroplet haritası üretir.
    """
    geojson = load_geojson()
    
    if pollutant not in df.columns:
        pollutant = "pm25"
        
    pollutant_labels = {
        "pm25": "PM2.5 (µg/m³)",
        "pm10": "PM10 (µg/m³)",
        "no2": "NO₂ (µg/m³)"
    }
    label = pollutant_labels.get(pollutant, f"{pollutant.upper()} (µg/m³)")
    
    # Özel Hover Şablonu
    # İl Adı, Değer, DSÖ Durumu, Bölge, Nüfus, Veri Kaynağı
    fig = px.choropleth(
        df,
        geojson=geojson,
        locations="plaka",
        featureidkey="properties.number",
        color=pollutant,
        color_continuous_scale=AQI_COLOR_SCALE,
        hover_name="il",
        hover_data={
            "plaka": False,
            pollutant: ":.1f",
            "dso_risk": True,
            "bolge": True,
            "toplam_osb": True,
            "solunum_olum_100k": ":.1f"
        },
        labels={
            pollutant: label,
            "dso_risk": "DSÖ Risk Sınıfı",
            "bolge": "Bölge",
            "toplam_osb": "OSB Sayısı",
            "solunum_olum_100k": "Solunum Ölüm (100k)"
        }
    )
    
    # Türkiye Coğrafi Merkez Odaklama ve Koyu Harita Düzeni
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        showland=True, landcolor="#0c1322",
        showocean=True, oceancolor="#070b14",
        showlakes=True, lakecolor="#070b14",
        showcountries=True, countrycolor="#1e293b",
        countrywidth=1.0
    )
    
    fig.update_layout(
        height=560,
        margin=dict(t=10, l=0, r=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(
            title=dict(text=label, font=dict(color="#f8fafc", size=11)),
            tickfont=dict(color="#94a3b8", size=10),
            len=0.75,
            thickness=14,
            x=0.98,
            xpad=0,
            bgcolor="rgba(15, 23, 42, 0.6)",
            bordercolor="rgba(56, 189, 248, 0.2)",
            borderwidth=1
        )
    )
    
    return fig
