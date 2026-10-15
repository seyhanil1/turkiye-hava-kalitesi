"""
Şehir Karnesi Sayfası (City Card Page Alias)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

Bu modül `app_pages.report_card` bileşenini doğrudan dışa aktarır.
"""

from .report_card import (
    render_report_card_page,
    generate_city_summary,
    to_tr_num,
    to_tr_sign,
    get_disp_val,
    get_dso_risk_tier,
)

render_city_card_page = render_report_card_page

__all__ = [
    "render_report_card_page",
    "render_city_card_page",
    "generate_city_summary",
    "to_tr_num",
    "to_tr_sign",
    "get_disp_val",
    "get_dso_risk_tier",
]
