"""
Birim Testleri: Pixel Perfect Dashboard & Genel Bakış Gerçek Veri Analitik Paneli
"""

import pytest
import pandas as pd
from data_sources.local_official_data import build_master_dataset
from visualization.pixel_perfect_dashboard import (
    generate_pixel_perfect_dashboard_html,
    _generate_overview_analytics_components,
    BOLGELER_DICT,
    IL_TO_BOLGE_MAP
)


def test_bolgeler_dict_coverage():
    """81 ilin tamamının bölge haritasında yer aldığını doğrular."""
    assert len(BOLGELER_DICT) == 7
    total_mapped_cities = sum(len(iller) for iller in BOLGELER_DICT.values())
    assert total_mapped_cities == 81
    assert len(IL_TO_BOLGE_MAP) == 81
    assert IL_TO_BOLGE_MAP["İstanbul"] == "Marmara"
    assert IL_TO_BOLGE_MAP["Iğdır"] == "Doğu Anadolu"
    assert IL_TO_BOLGE_MAP["İzmir"] == "Ege"


def test_analytics_components_generation():
    """Analitik bileşenlerin doğru metriklerle üretildiğini doğrular."""
    df = build_master_dataset()
    bar_html, card_html = _generate_overview_analytics_components(df)
    
    assert len(bar_html) > 500
    assert len(card_html) > 500
    
    # 1. Bar Grafiği içeriği (Plotly JSON unicode kaçışlarını da destekler)
    assert ("DSÖ Yıllık Kılavuz Değeri" in bar_html) or ("DS\\u00d6 Y\\u0131ll\\u0131k K\\u0131lavuz De\\u011feri" in bar_html)
    assert ("Doğu Anadolu" in bar_html) or ("Do\\u011fu Anadolu" in bar_html)
    assert ("En Kritik İl" in bar_html) or ("En Kritik \\u0130l" in bar_html)
    
    # 2. Küme kartı içeriği
    assert "Ulusal Kirlilik Maruziyeti" in card_html
    assert "0 / 81 İl" in card_html
    assert "Kritik" in card_html
    assert "Sağlıksız" in card_html
    assert "TOPOGRAFİK RİSK GRUBU (ÇANAK HAVZALAR)" in card_html
    assert "Iğdır, Düzce, Erzincan vb." in card_html


def test_fallback_when_bolge_column_missing():
    """Veri setinde 'bolge' kolonu olmadığında dahi hatasız çalıştığını test eder."""
    df = build_master_dataset()
    df_no_bolge = df.drop(columns=["bolge"])
    assert "bolge" not in df_no_bolge.columns
    
    bar_html, card_html = _generate_overview_analytics_components(df_no_bolge)
    assert len(bar_html) > 500
    assert ("Doğu Anadolu" in bar_html) or ("Do\\u011fu Anadolu" in bar_html)
    assert "0 / 81 İl" in card_html


def test_dashboard_html_structure_and_no_old_health_shield():
    """Üretilen dashboard HTML içinde sadeleştirilmiş yapıyı ve eski sağlık kalkanı bölümünün olmadığını doğrular."""
    df = build_master_dataset()
    html = generate_pixel_perfect_dashboard_html(df)
    
    # Sadeleştirilmiş yapı: Hero, harita, sıralama tablosu ve alt bilgi
    assert "HavaAtlası" in html
    assert "rankingTableContent" in html
    assert "mapContainer" in html
    assert "plotly-2.27.0.min.js" in html
    assert "81 İlin Ortalaması" in html
    
    # 7 Coğrafi Bölge Benchmark grafiğinin Bölgeler sayfasında üretildiğini doğrula
    from app_pages.regions_page import create_regional_benchmark_bar
    fig_bench = create_regional_benchmark_bar(df)
    assert fig_bench is not None
    assert len(fig_bench.data) > 0
    
    # Eski statik metinler ve healthShieldSection ID'si kaldırıldı
    assert 'id="healthShieldSection"' not in html
    assert "Hassas Gruplar (Kronik/Çocuk/Yaşlı)" not in html
