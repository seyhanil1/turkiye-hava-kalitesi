"""
Zaman Serisi Grafik Bileşenleri
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import pandas as pd
import plotly.graph_objects as go
from typing import Optional

def create_timeseries_chart(
    df_ts: pd.DataFrame, 
    window_days: int = 30,
    pollutant: str = "pm25",
    title: Optional[str] = None
) -> go.Figure:
    """
    7, 30 ve 90 günlük dinamik zaman serisi çizgisi, 7 günlük hareketli ortalama bandı
    ve DSÖ kılavuz limit çizgisini içeren yüksek teknolojili Plotly grafiği üretir.
    """
    if df_ts.empty:
        fig = go.Figure()
        fig.add_annotation(text="Zaman serisi verisi bulunamadı", showarrow=False, font=dict(color="#94a3b8"))
        return fig
        
    df = df_ts.copy()
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        
    # Tarih penceresi filtreleme
    latest_date = df["date"].max()
    start_date = latest_date - pd.Timedelta(days=window_days)
    df_window = df[df["date"] >= start_date].copy()
    
    val_col = "pm25"
    label = "PM2.5"
    
    # 7 günlük hareketli ortalama hesapla
    df_window["ma7"] = df_window[val_col].rolling(7, min_periods=1).mean().round(2)
    
    # DSÖ 24 saatlik kılavuz limiti (PM2.5 = 15 µg/m³)
    dso_threshold = 15.0
    
    fig = go.Figure()
    
    # 1. Günlük Ölçümler (Ana Çizgi ve Noktalar)
    fig.add_trace(go.Scatter(
        x=df_window["date"],
        y=df_window[val_col],
        mode="lines+markers",
        name=f"Günlük {label}",
        line=dict(color="#38bdf8", width=2.5),
        marker=dict(size=5, color="#06b6d4", symbol="circle"),
        hovertemplate="<b>Tarih:</b> %{x|%d %b %Y}<br><b>Değer:</b> %{y:.1f} µg/m³<extra></extra>"
    ))
    
    # 2. 7 Günlük Hareketli Ortalama (Trend Çizgisi)
    fig.add_trace(go.Scatter(
        x=df_window["date"],
        y=df_window["ma7"],
        mode="lines",
        name="7 Günlük Ort. (MA7)",
        line=dict(color="#10b981", width=2, dash="dot"),
        hovertemplate="<b>MA7 Trend:</b> %{y:.1f} µg/m³<extra></extra>"
    ))
    
    # 3. DSÖ Kılavuz Limit Eşiği Çizgisi
    fig.add_hline(
        y=dso_threshold,
        line=dict(color="#ef4444", width=1.5, dash="dash"),
        annotation_text=f"DSÖ 24s Sınırı ({int(dso_threshold)} µg/m³)",
        annotation_position="top left",
        annotation_font=dict(size=10, color="#ef4444")
    )
    
    # Grafik Başlığı
    if not title:
        title = f"Son {window_days} Günde {label} Değişim Trendi ve DSÖ Eşiği"
        
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=14, color="#f8fafc"),
            x=0.01,
            y=0.96
        ),
        height=320,
        margin=dict(t=40, l=10, r=10, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color="#94a3b8")
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="#1e293b",
            tickformat="%d %b",
            color="#94a3b8"
        ),
        yaxis=dict(
            title=dict(text="Konsantrasyon (µg/m³)", font=dict(color="#94a3b8", size=11)),
            showgrid=True,
            gridcolor="#1e293b",
            color="#94a3b8"
        ),
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig
