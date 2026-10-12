"""
Sanayi vs. Kirlilik Stratejik Risk Matrisi (Plotly Bubble Chart)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

Özellikler:
1. X Ekseni: Organize Sanayi Bölgesi Sayısı ('osb_sayisi')
2. Y Ekseni: Ortalama PM2.5 Seviyesi ('pm25')
3. Balon Büyüklüğü: Solunum kaynaklı ölüm oranı ('solunum_olum_100k')
4. Balon Renkleri: PM2.5 değerine göre neon yeşilden (#00f2fe) neon kırmızıya (#ff4b4b) uzanan şık bir gradyan.
5. Hover Kartı: Şehir adı, OSB sayısı, PM2.5 değeri, DSÖ katı ve ölüm oranı.
6. Karar Destek Çizgileri (Quadrant / Eşikler):
   - Y ekseninde Türkiye PM2.5 ortalamasına kesikli yatay çizgi
   - X ekseninde Türkiye OSB ortalamasına kesikli dikey çizgi
   - 4 köşe etiketleri:
     * Sol Üst: 'Coğrafi / Isınma Kaynaklı Risk (Örn: Iğdır)'
     * Sağ Üst: 'Sanayi Yoğunluğu Kaynaklı Risk'
     * Sol Alt: 'Ekolojik Güvenli Bölge'
     * Sağ Alt: 'Yeşil / Kontrollü Sanayi'
7. Koyu lacivert/neon tasarım uyumu (#0b132b / #070e20).
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Optional


def create_strategic_risk_matrix(df: pd.DataFrame, height: int = 590) -> go.Figure:
    """
    81 il için Sanayi vs. Kirlilik Stratejik Risk Matrisi (Plotly Bubble Chart) üretir.
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Risk matrisi için veri bulunamadı",
            showarrow=False,
            font=dict(color="#94a3b8")
        )
        return fig

    # Eşik değerler (Türkiye Ortalamaları)
    mean_pm = float(df["pm25"].mean()) if "pm25" in df.columns else 35.0
    mean_osb = float(df["osb_sayisi"].mean()) if "osb_sayisi" in df.columns else 5.0

    # Balon büyüklüğü hesaplama: solunum_olum_100k
    death_col = "solunum_olum_100k" if "solunum_olum_100k" in df.columns else "pm25"
    death_min = float(df[death_col].min())
    death_max = float(df[death_col].max())
    size_min, size_max = 14, 46
    sizes = size_min + (df[death_col] - death_min) / (death_max - death_min + 1e-6) * (size_max - size_min)

    # DSÖ Kılavuz Katı
    dso_kat = (df["pm25"] / 5.0).round(1)

    # Renk Skalası: Neon Yeşilden (#00f2fe) Neon Kırmızıya (#ff4b4b)
    custom_colorscale = [
        [0.0, "#00f2fe"],   # Neon camgöbeği
        [0.25, "#10b981"],  # Neon yeşil
        [0.50, "#facc15"],  # Neon sarı
        [0.75, "#f97316"],  # Neon turuncu
        [1.0, "#ff4b4b"]   # Neon kırmızı
    ]

    # Hover Customdata
    customdata = np.stack((
        df["il"],
        df["bolge"],
        dso_kat,
        df.get("dso_risk", pd.Series(["Kritik" if p > 35 else "Orta" for p in df["pm25"]])),
        df[death_col].round(1),
        df["osb_sayisi"]
    ), axis=-1)

    hovertemplate = (
        "<div style='background-color:#091628; border:1px solid #00e5db; border-radius:10px; padding:12px 16px; font-family:system-ui,sans-serif; color:#f8fafc; min-width:220px; box-shadow:0 8px 24px rgba(0,0,0,0.65);'>"
        "<div style='font-size:16px; font-weight:800; color:#00e5db; margin-bottom:8px; border-bottom:1px solid #143763; padding-bottom:4px;'>%{customdata[0]} <span style='font-size:12px; color:#94a3b8; font-weight:500;'>(%{customdata[1]})</span></div>"
        "<div style='font-size:12.5px; line-height:1.75; color:#cbd5e1;'>"
        "• <b>PM2.5 Kirlilik:</b> <span style='color:#f8fafc; font-weight:700;'>%{y:.1f} µg/m³</span><br>"
        "• <b>DSÖ Sınır Katı:</b> <span style='color:#facc15; font-weight:700;'>%{customdata[2]}x</span> (%{customdata[3]})<br>"
        "• <b>OSB Sayısı:</b> <span style='color:#38bdf8; font-weight:700;'>%{x} adet</span><br>"
        "• <b>Solunum Vefat:</b> <span style='color:#ff4b4b; font-weight:700;'>%{customdata[4]} / 100k</span>"
        "</div>"
        "</div><extra></extra>"
    )

    fig = go.Figure()

    # Balon Grafiği
    fig.add_trace(go.Scatter(
        x=df["osb_sayisi"],
        y=df["pm25"],
        mode="markers+text",
        customdata=customdata,
        hovertemplate=hovertemplate,
        text=df["il"],
        textposition="top center",
        textfont=dict(
            family="system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
            size=10,
            color="rgba(241, 245, 249, 0.78)"
        ),
        marker=dict(
            size=sizes,
            color=df["pm25"],
            colorscale=custom_colorscale,
            showscale=True,
            colorbar=dict(
                title=dict(text="<b>PM2.5 (µg/m³)</b>", font=dict(color="#f8fafc", size=11)),
                tickfont=dict(color="#cbd5e1", size=10),
                thickness=14,
                len=0.78,
                x=1.01,
                bgcolor="rgba(11, 19, 43, 0.85)",
                bordercolor="#1e293b",
                borderwidth=1
            ),
            line=dict(color="rgba(255, 255, 255, 0.45)", width=1.2),
            opacity=0.88
        ),
        name="İller"
    ))

    # 1. Yatay Eşik Çizgisi: Türkiye PM2.5 Ortalaması
    fig.add_hline(
        y=mean_pm,
        line=dict(color="#38bdf8", width=1.8, dash="dash"),
        annotation=dict(
            text=f"TR PM2.5 Ortalaması: {mean_pm:.1f} µg/m³",
            font=dict(color="#38bdf8", size=11, family="system-ui, sans-serif"),
            bgcolor="rgba(9, 22, 40, 0.85)",
            bordercolor="#38bdf8",
            borderwidth=1,
            borderpad=4
        ),
        annotation_position="top left"
    )

    # 2. Dikey Eşik Çizgisi: Türkiye Ortalama OSB Sayısı
    fig.add_vline(
        x=mean_osb,
        line=dict(color="#00e5db", width=1.8, dash="dash"),
        annotation=dict(
            text=f"TR OSB Ortalaması: {mean_osb:.1f} Adet",
            font=dict(color="#00e5db", size=11, family="system-ui, sans-serif"),
            bgcolor="rgba(9, 22, 40, 0.85)",
            bordercolor="#00e5db",
            borderwidth=1,
            borderpad=4
        ),
        annotation_position="top right"
    )

    # 3. 4 Köşe Stratejik Kuadran Etiketleri
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.015, y=0.97,
        text="<b>Coğrafi / Isınma Kaynaklı Risk (Örn: Iğdır)</b><br><span style='font-size:10px; color:#cbd5e1;'>Düşük OSB • Yüksek PM2.5 (Topoğrafik Çanak & Evsel Kömür)</span>",
        showarrow=False,
        align="left",
        font=dict(color="#f87171", size=11.5, family="system-ui, sans-serif"),
        bgcolor="rgba(15, 23, 42, 0.85)",
        bordercolor="rgba(239, 68, 68, 0.45)",
        borderwidth=1,
        borderpad=7
    )

    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.985, y=0.97,
        text="<b>Sanayi Yoğunluğu Kaynaklı Risk</b><br><span style='font-size:10px; color:#cbd5e1;'>Yüksek OSB • Yüksek PM2.5 (Ağır Endüstriyel Emisyon)</span>",
        showarrow=False,
        align="right",
        font=dict(color="#fb923c", size=11.5, family="system-ui, sans-serif"),
        bgcolor="rgba(15, 23, 42, 0.85)",
        bordercolor="rgba(249, 115, 22, 0.45)",
        borderwidth=1,
        borderpad=7
    )

    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.015, y=0.03,
        text="<b>Ekolojik Güvenli Bölge</b><br><span style='font-size:10px; color:#cbd5e1;'>Düşük OSB • Düşük PM2.5 (Yüksek Rakım & Korunmuş Doğa)</span>",
        showarrow=False,
        align="left",
        font=dict(color="#34d399", size=11.5, family="system-ui, sans-serif"),
        bgcolor="rgba(15, 23, 42, 0.85)",
        bordercolor="rgba(16, 185, 129, 0.45)",
        borderwidth=1,
        borderpad=7
    )

    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.985, y=0.03,
        text="<b>Yeşil / Kontrollü Sanayi</b><br><span style='font-size:10px; color:#cbd5e1;'>Yüksek OSB • Kontrollü PM2.5 (Gelişmiş Filtreleme & Yeşil OSB)</span>",
        showarrow=False,
        align="right",
        font=dict(color="#38bdf8", size=11.5, family="system-ui, sans-serif"),
        bgcolor="rgba(15, 23, 42, 0.85)",
        bordercolor="rgba(56, 189, 248, 0.45)",
        borderwidth=1,
        borderpad=7
    )

    # Düzen & Tema
    fig.update_layout(
        title=dict(
            text="<b>Sanayi vs. Kirlilik Stratejik Risk Matrisi</b> <span style='font-size:12px; color:#94a3b8; font-weight:normal;'>| Balon Boyutu: Solunum Kaynaklı Vefat Oranı (/100k)</span>",
            font=dict(family="system-ui, -apple-system, sans-serif", size=15, color="#f8fafc"),
            x=0.015,
            y=0.98
        ),
        height=height,
        margin=dict(l=55, r=45, t=65, b=50),
        paper_bgcolor="#0b132b",
        plot_bgcolor="#070e20",
        xaxis=dict(
            title=dict(text="<b>Organize Sanayi Bölgesi (OSB) Sayısı</b>", font=dict(color="#f8fafc", size=12)),
            tickfont=dict(color="#cbd5e1", size=11),
            gridcolor="rgba(30, 41, 59, 0.5)",
            zerolinecolor="rgba(51, 65, 85, 0.6)",
            showline=True,
            linecolor="#1e293b"
        ),
        yaxis=dict(
            title=dict(text="<b>Yıllık Ortalama PM2.5 Seviyesi (µg/m³)</b>", font=dict(color="#f8fafc", size=12)),
            tickfont=dict(color="#cbd5e1", size=11),
            gridcolor="rgba(30, 41, 59, 0.5)",
            zerolinecolor="rgba(51, 65, 85, 0.6)",
            showline=True,
            linecolor="#1e293b"
        ),
        hoverlabel=dict(
            bgcolor="#091628",
            bordercolor="#00e5db",
            font=dict(family="system-ui, sans-serif", size=12, color="#f8fafc")
        )
    )

    return fig
