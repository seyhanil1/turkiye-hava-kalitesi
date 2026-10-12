"""
Görsel Tasarım, Tema ve Renk Paletleri
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

Tasarım Dili:
- Arka Plan: Koyu lacivert ve siyah tonları (#070c18, #0b1120, #0f172a)
- Neon Vurgular: Turkuaz (#06b6d4), elektrik mavisi (#38bdf8), neon yeşil (#10b981)
- Kirlilik Renkleri: DSÖ kademelerine uygun (Yeşil, Sarı, Turuncu, Kırmızı, Bordo)
- Kartlar: İnce mavi kenarlık (1px solid #1e293b / rgba(56, 189, 248, 0.2)), parlama gölgesi
"""

import plotly.io as pio
import plotly.graph_objects as go

# Ana Renk Kodları
COLOR_BG_DARK = "#070c18"
COLOR_CARD_BG = "#0f172a"
COLOR_BORDER = "rgba(56, 189, 248, 0.2)"
COLOR_CYAN = "#06b6d4"
COLOR_SKY = "#38bdf8"
COLOR_GREEN = "#10b981"
COLOR_YELLOW = "#facc15"
COLOR_ORANGE = "#f97316"
COLOR_RED = "#ef4444"
COLOR_MAROON = "#881337"
COLOR_MUTED = "#94a3b8"

# Hava Kalitesi Çoklu Renk Skalası (DSÖ Uyumlu)
AQI_COLOR_SCALE = [
    [0.0, "#10b981"],    # İyi / Güvenli (Yeşil)
    [0.25, "#facc15"],   # Orta / Uyarı (Sarı)
    [0.50, "#f97316"],   # Hassas / Yüksek (Turuncu)
    [0.75, "#ef4444"],   # Sağlıksız / Kritik (Kırmızı)
    [1.0, "#881337"]     # Tehlikeli / Şiddetli (Bordo)
]

def apply_custom_plotly_theme():
    """Plotly için özel karanlık ve minimalist temayı varsayılan yapar."""
    pio.templates["havaatlasi_dark"] = go.layout.Template(
        layout=go.Layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(
                family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                color="#f8fafc",
                size=12
            ),
            xaxis=dict(
                gridcolor="#1e293b",
                zerolinecolor="#334155",
                tickfont=dict(color="#94a3b8")
            ),
            yaxis=dict(
                gridcolor="#1e293b",
                zerolinecolor="#334155",
                tickfont=dict(color="#94a3b8")
            ),
            colorway=["#38bdf8", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"]
        )
    )
    pio.templates.default = "havaatlasi_dark"

# Modül yüklendiğinde temayı etkinleştir
apply_custom_plotly_theme()
