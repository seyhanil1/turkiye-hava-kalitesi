"""
Sanayi Profili Sayfası (Industrial Profile Page Alias)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

Bu modül `app_pages.industry_page` bileşenini doğrudan dışa aktarır.
"""

from .industry_page import (
    render_industry_page,
)

render_industry_profile_page = render_industry_page

__all__ = [
    "render_industry_page",
    "render_industry_profile_page",
]
