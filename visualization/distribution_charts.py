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
    Şehir sıralaması yatay çubuk grafiği (En Yüksek veya En Düşük N İl).
    """
    if pollutant not in df.columns:
        pollutant = "pm25"
        
    sorted_df = df.sort_values(by=pollutant, ascending=ascending).head(top_n).copy()
    # Yatay çubukta yukarıdan aşağıya doğru düzgün dizilim
    sorted_df = sorted_df.iloc[::-1]
    
    label = "PM2.5"
    
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
    label = "PM2.5"
    
    # Bölgeleri ortalama kirliliğe göre yüksekten düşüğe doğru sırala
    order = df.groupby("bolge")[val_col].mean().sort_values(ascending=False).index.tolist()
    
    fig = px.box(
        df,
        x="bolge",
        y=val_col,
        category_orders={"bolge": order},
        points="outliers",
        hover_name="il"
    )
    
    fig.update_traces(
        boxpoints="outliers",
        marker=dict(color="#00d2ee", size=5),
        line=dict(color="#00d2ee", width=1.5),
        fillcolor="rgba(0, 210, 238, 0.2)"
    )
    
    fig.update_layout(
        title=None,
        height=400,
        margin=dict(b=70, t=40, l=50, r=20),
        xaxis=dict(title=None, tickfont=dict(color="#94a3b8", size=11), tickangle=-45),
        yaxis=dict(
            title=dict(text=f"{label} Konsantrasyonu (µg/m³)", font=dict(color="#94a3b8", size=11)),
            gridcolor="#1e293b",
            tickfont=dict(color="#94a3b8", size=10)
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
        "Hava Temizliği Skoru", 
        "Sanayi Baskısı (Düşük)", 
        "Solunum Sağlığı"
    ]
    
    # Skorlama (100 = En iyi durum)
    val_a = [
        max(0, 100 - (city_a["pm25"] / 85.0 * 100)),
        max(0, 100 - (city_a.get("toplam_osb", 0) / 15.0 * 100)),
        max(0, 100 - (city_a.get("solunum_olum_100k", 35.0) / 60.0 * 100))
    ]
    
    val_b = [
        max(0, 100 - (city_b["pm25"] / 85.0 * 100)),
        max(0, 100 - (city_b.get("toplam_osb", 0) / 15.0 * 100)),
        max(0, 100 - (city_b.get("solunum_olum_100k", 35.0) / 60.0 * 100))
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
            radialaxis=dict(
                visible=True, 
                range=[0, 100], 
                angle=45,
                tickfont=dict(color="#94a3b8", size=9), 
                gridcolor="#1e293b"
            ),
            angularaxis=dict(
                tickfont=dict(color="#f8fafc", size=10), 
                gridcolor="#1e293b"
            ),
            bgcolor="rgba(0,0,0,0)"
        ),
        title=dict(
            text=f"<b>{city_a['il']} vs {city_b['il']} Çevresel Yetkinlik Radarı</b>",
            font=dict(size=13, color="#f8fafc")
        ),
        height=360,
        margin=dict(t=50, l=60, r=60, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=-0.18, xanchor="center", x=0.5),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig


def create_duel_dumbbell_chart(
    df: pd.DataFrame, 
    city_a: pd.Series, 
    city_b: pd.Series
) -> go.Figure:
    """
    81 il içindeki yüzdelik konumu (Percentile Rank: 0-100, yüksek = daha olumlu)
    gösteren yatay dumbbell (nokta-çizgi) karşılaştırma grafiği.
    Ham veriden doğrudan hesaplanır (PM2.5, Solunum Ölümü).
    Kaynaksız göstergeler (Yeşil Skor vb.) içermez.
    """
    # 1. Hava Temizliği: PM2.5 düşük olan daha yüksek yüzdelik alır (ters rank)
    pm_rank_series = df["pm25"].rank(ascending=False, pct=True) * 100.0
    pct_pm_a = float(pm_rank_series[df["il"] == city_a["il"]].iloc[0])
    pct_pm_b = float(pm_rank_series[df["il"] == city_b["il"]].iloc[0])

    # 2. Solunum Sağlığı: 100k ölüm hızı düşük olan daha yüksek yüzdelik alır (ters rank)
    sol_rank_series = df["solunum_olum_100k"].rank(ascending=False, pct=True) * 100.0
    pct_sol_a = float(sol_rank_series[df["il"] == city_a["il"]].iloc[0])
    pct_sol_b = float(sol_rank_series[df["il"] == city_b["il"]].iloc[0])

    categories = [
        "Solunum Sağlığı (Düşük Ölüm)",
        "Hava Temizliği (Düşük PM2.5)"
    ]
    vals_a = [pct_sol_a, pct_pm_a]
    vals_b = [pct_sol_b, pct_pm_b]

    # Ham metinler
    raw_a = [
        f"{float(city_a['solunum_olum_100k']):.1f} / yüz binde".replace(".", ","),
        f"{float(city_a['pm25']):.1f} µg/m³".replace(".", ",")
    ]
    raw_b = [
        f"{float(city_b['solunum_olum_100k']):.1f} / yüz binde".replace(".", ","),
        f"{float(city_b['pm25']):.1f} µg/m³".replace(".", ",")
    ]

    fig = go.Figure()

    # Bağlantı çizgileri (Dumbbell bar)
    for cat, va, vb in zip(categories, vals_a, vals_b):
        fig.add_trace(go.Scatter(
            x=[va, vb],
            y=[cat, cat],
            mode="lines",
            line=dict(color="#334155", width=3.5),
            showlegend=False,
            hoverinfo="none"
        ))

    # Dinamik metin pozisyonları (yakın noktalarda çakışmayı önler: 1. İl daima üstte, 2. İl daima altta)
    pos_a = ["top center" for _ in vals_a]
    pos_b = ["bottom center" for _ in vals_b]

    # Şehir A noktaları (Mavi)
    fig.add_trace(go.Scatter(
        x=vals_a,
        y=categories,
        mode="markers+text",
        name=city_a["il"],
        marker=dict(color="#38bdf8", size=13, line=dict(color="#ffffff", width=1.5)),
        text=[f"{city_a['il']} %{va:.0f}" for va in vals_a],
        textposition=pos_a,
        cliponaxis=False,
        textfont=dict(color="#38bdf8", size=10),
        customdata=raw_a,
        hovertemplate=f"<b>{city_a['il']}</b><br>%{{y}}<br>Yüzdelik Konum: %{{x:.1f}} / 100<br>Ham Değer: %{{customdata}}<extra></extra>"
    ))

    # Şehir B noktaları (Yeşil)
    fig.add_trace(go.Scatter(
        x=vals_b,
        y=categories,
        mode="markers+text",
        name=city_b["il"],
        marker=dict(color="#10b981", size=13, line=dict(color="#ffffff", width=1.5)),
        text=[f"{city_b['il']} %{vb:.0f}" for vb in vals_b],
        textposition=pos_b,
        cliponaxis=False,
        textfont=dict(color="#10b981", size=10),
        customdata=raw_b,
        hovertemplate=f"<b>{city_b['il']}</b><br>%{{y}}<br>Yüzdelik Konum: %{{x:.1f}} / 100<br>Ham Değer: %{{customdata}}<extra></extra>"
    ))

    fig.update_layout(
        title=dict(
            text="<b>81 İl İçindeki Yüzdelik Konum (0–100, Yüksek = Daha Olumlu)</b>",
            font=dict(size=13, color="#f8fafc")
        ),
        height=260,
        margin=dict(t=50, l=30, r=40, b=45),
        xaxis=dict(
            title=dict(
                text="81 İl İçindeki Yüzdelik Sıralama (Percentile)",
                font=dict(color="#94a3b8", size=11),
                standoff=10
            ),
            range=[-12, 112],
            gridcolor="#1e293b",
            tickfont=dict(color="#94a3b8", size=10),
            zeroline=False
        ),
        yaxis=dict(
            tickfont=dict(color="#f8fafc", size=11),
            gridcolor="#1e293b"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.04,
            xanchor="right",
            x=1.0,
            font=dict(color="#f8fafc", size=11)
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    return fig


def create_single_metric_comparison_bar(
    metric_title: str,
    unit_label: str,
    val_a: float,
    val_b: float,
    name_a: str,
    name_b: str,
    text_a: str,
    text_b: str
) -> go.Figure:
    """
    Tek bir birim için bağımsız, ölçeği karışmayan küçük çubuk grafik (Small Multiple).
    """
    max_val = max(val_a, val_b, 1.0)
    upper_limit = max_val * 1.25

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[name_a],
        y=[val_a],
        name=name_a,
        text=[text_a],
        textposition="outside",
        textfont=dict(color="#f8fafc", size=11),
        marker_color="#38bdf8",
        hovertemplate=f"<b>{name_a}</b><br>{metric_title}: {text_a}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        x=[name_b],
        y=[val_b],
        name=name_b,
        text=[text_b],
        textposition="outside",
        textfont=dict(color="#f8fafc", size=11),
        marker_color="#10b981",
        hovertemplate=f"<b>{name_b}</b><br>{metric_title}: {text_b}<extra></extra>"
    ))

    fig.update_layout(
        title=dict(
            text=f"<b>{metric_title}</b>",
            font=dict(size=12, color="#f8fafc")
        ),
        height=260,
        margin=dict(t=35, l=15, r=15, b=20),
        yaxis=dict(
            title=dict(
                text=unit_label,
                font=dict(color="#94a3b8", size=10)
            ),
            range=[0, upper_limit],
            gridcolor="#1e293b",
            tickfont=dict(color="#94a3b8", size=9)
        ),
        xaxis=dict(
            tickfont=dict(color="#f8fafc", size=11),
            gridcolor="#1e293b"
        ),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    return fig
