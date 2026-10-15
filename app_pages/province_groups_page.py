"""
İl Grupları Modülü (Province Groups Page Alias)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

Bu modül `app_pages.ai_forecast_page` bileşenini doğrudan dışa aktarır.
"""

from .ai_forecast_page import (
    calculate_quantiles_and_anomalies,
    determine_city_category,
    build_projection_series,
    create_forecast_figure,
    render_ai_forecast_page,
)

render_province_groups_page = render_ai_forecast_page

__all__ = [
    "calculate_quantiles_and_anomalies",
    "determine_city_category",
    "build_projection_series",
    "create_forecast_figure",
    "render_ai_forecast_page",
    "render_province_groups_page",
]
