"""
app_pages paketi
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

from app_pages.overview import render_overview_page
from app_pages.report_card import render_report_card_page
from app_pages.duel import render_duel_page
from app_pages.correlation_page import render_correlation_page
from app_pages.regions_page import render_regions_page
from app_pages.industry_page import render_industry_page
from app_pages.ai_forecast_page import render_ai_forecast_page
from app_pages.action_guide import render_action_guide_page

__all__ = [
    "render_overview_page",
    "render_report_card_page",
    "render_duel_page",
    "render_correlation_page",
    "render_regions_page",
    "render_industry_page",
    "render_ai_forecast_page",
    "render_action_guide_page",
]

