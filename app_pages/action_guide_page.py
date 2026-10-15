"""
Eylem Rehberi Sayfası (Action Guide Page Alias)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

Bu modül `app_pages.action_guide` bileşenini doğrudan dışa aktarır.
"""

from .action_guide import (
    render_action_guide_page,
)

render_action_page = render_action_guide_page

__all__ = [
    "render_action_guide_page",
    "render_action_page",
]
