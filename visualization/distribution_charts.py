"""
Dağılım, Sıralama, Korelasyon ve Düello Grafikleri
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, List

from visualization.theme import AQI_COLOR_SCALE

def create_ranking_bar_chart(
    df: pd.DataFrame, 
    pollutant: str = "pm25", 
    top_n: int = 10,
    ascending: bool = False
) -> go.Figure:
    """
    Şehir sıralaması yatay çubuk grafiği (En Kirli veya En Temiz N İl).
    """
    if pollutant not in df.columns:
        pollutant = "pm25"
        
    sorted_df = df.sort_values(by=pollutant, ascending=ascending).head(top_n).copy()
    # Yatay çubukta yukarıdan aşağıya doğru düzgün dizilim
    sorted_df = sorted_df.iloc[::-1]
    
    label = "PM2.5" if pollutant == "pm25" else ("PM10" if pollutant == "pm10" else "NO₂")
    
    fig = px.bar(
        sorted_df,
        x=pollutant,
        y="il",
        orientation="h",
        text=pollutant,
        color=pollutant,
        color_continuous_scale=AQI_COLOR_SCALE
    )
    
    fig.update_traces(
        texttemplate="%{text:.1f} µg/m³",
        textposition="outside",
        textfont=dict(color="#f8fafc", size=11),
        marker=dict(line=dict(width=0))
    )
    
    fig.update_layout(
        height=560,
        margin=dict(t=10, l=10, r=40, b=10),
        xaxis=dict(
            title=dict(text=f"Ortalama {label} (µg/m³)", font=dict(color="#94a3b8", size=11)),
            showgrid=True,
            gridcolor="#1e293b",
            color="#94a3b8"
        ),
        yaxis=dict(
            title="",
            tickfont=dict(color="#f8fafc", size=11),
            autorange="reversed" if not ascending else True
        ),
        coloraxis_showscale=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_regional_boxplot(
    df: pd.DataFrame, 
    pollutant: str = "pm25"
) -> go.Figure:
    """
    7 Coğrafi Bölgenin kirlilik dağılımını gösteren Kutu Grafiği (Boxplot).
    Medyan, çeyreklikler (Q1, Q3) ve aykırı değerleri görselleştirir.
    """
    val_col = pollutant if pollutant in df.columns else "pm25"
    label = "PM2.5" if val_col == "pm25" else ("PM10" if val_col == "pm10" else "NO₂")
    
    # Bölgeleri ortalama kirliliğe göre sırala
    order = df.groupby("bolge")[val_col].median().sort_values(ascending=False).index.tolist()
    
    fig = px.box(
        df,
        x="bolge",
        y=val_col,
        color="bolge",
        category_orders={"bolge": order},
        points="all",
        hover_name="il"
    )
    
    fig.update_layout(
        title=dict(
            text=f"<b>Bölgesel {label} Dağılımı ve Varyans (Box-Plot)</b>",
            font=dict(size=14, color="#f8fafc")
        ),
        height=380,
        margin=dict(t=40, l=20, r=20, b=30),
        xaxis=dict(title="", tickfont=dict(color="#94a3b8", size=11)),
        yaxis=dict(
            title=dict(text=f"{label} Konsantrasyonu (µg/m³)", font=dict(color="#94a3b8", size=11)),
            gridcolor="#1e293b"
        ),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_correlation_heatmap(
    corr_df: pd.DataFrame, 
    title: str = "Korelasyon Matrisi (Pearson r)"
) -> go.Figure:
    """
    Değişkenler arası korelasyon matrisi ısı haritası (Heatmap).
    """
    labels = [c.replace("_", " ").title() for c in corr_df.columns]
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_df.values,
        x=labels,
        y=labels,
        colorscale="RdBu_r",
        zmin=-1.0,
        zmax=1.0,
        text=corr_df.values,
        texttemplate="%{text:.2f}",
        textfont=dict(size=11, color="#f8fafc"),
        colorbar=dict(
            title=dict(text="r", font=dict(color="#94a3b8")),
            tickfont=dict(color="#94a3b8")
        )
    ))
    
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", font=dict(size=14, color="#f8fafc")),
        height=420,
        margin=dict(t=40, l=20, r=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_regression_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    x_label: str,
    y_label: str
) -> go.Figure:
    """
    İki değişken arasındaki OLS Regresyon dağılım grafiği (Scatter plot + Trendline).
    """
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        trendline="ols",
        hover_name="il",
        color="bolge",
        labels={x_col: x_label, y_col: y_label, "bolge": "Bölge"}
    )
    
    fig.update_traces(marker=dict(size=9, opacity=0.8, line=dict(width=1, color="#f8fafc")))
    
    fig.update_layout(
        title=dict(
            text=f"<b>{x_label} vs {y_label} Dağılımı ve OLS Eğilimi</b>",
            font=dict(size=14, color="#f8fafc")
        ),
        height=400,
        margin=dict(t=40, l=20, r=20, b=30),
        xaxis=dict(gridcolor="#1e293b", tickfont=dict(color="#94a3b8")),
        yaxis=dict(gridcolor="#1e293b", tickfont=dict(color="#94a3b8")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_duel_radar_chart(
    city_a: pd.Series, 
    city_b: pd.Series
) -> go.Figure:
    """
    İki ilin hava kalitesi, sanayi ve sağlık profilini karşılaştıran Radar Grafiği.
    Boyutlar 0-100 ölçeğine normalize edilir.
    """
    categories = [
        "Temiz Hava (Ters PM2.5)", 
        "Hafif Sanayi Yükü", 
        "Solunum Sağlığı", 
        "Yeşil Dönüşüm Skoru"
    ]
    
    # Skorlama (100 = En iyi durum)
    val_a = [
        max(0, 100 - (city_a["pm25"] / 85.0 * 100)),
        max(0, 100 - (city_a.get("toplam_osb", 0) / 15.0 * 100)),
        max(0, 100 - (city_a.get("solunum_olum_100k", 35.0) / 60.0 * 100)),
        city_a.get("yesil_skor", 50.0)
    ]
    
    val_b = [
        max(0, 100 - (city_b["pm25"] / 85.0 * 100)),
        max(0, 100 - (city_b.get("toplam_osb", 0) / 15.0 * 100)),
        max(0, 100 - (city_b.get("solunum_olum_100k", 35.0) / 60.0 * 100)),
        city_b.get("yesil_skor", 50.0)
    ]
    
    # Radar grafiği kapanması için ilk elemanı sona ekle
    categories_closed = categories + [categories[0]]
    val_a_closed = val_a + [val_a[0]]
    val_b_closed = val_b + [val_b[0]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=val_a_closed,
        theta=categories_closed,
        fill="toself",
        fillcolor="rgba(56, 189, 248, 0.25)",
        name=city_a["il"],
        line=dict(color="#38bdf8", width=2.5)
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=val_b_closed,
        theta=categories_closed,
        fill="toself",
        fillcolor="rgba(16, 185, 129, 0.25)",
        name=city_b["il"],
        line=dict(color="#10b981", width=2.5)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color="#94a3b8", size=9), gridcolor="#1e293b"),
            angularaxis=dict(tickfont=dict(color="#f8fafc", size=10), gridcolor="#1e293b"),
            bgcolor="rgba(0,0,0,0)"
        ),
        title=dict(
            text=f"<b>{city_a['il']} vs {city_b['il']} Çevresel Yetkinlik Radarı</b>",
            font=dict(size=13, color="#f8fafc")
        ),
        height=360,
        margin=dict(t=40, l=30, r=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig
