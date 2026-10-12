"""
Birim Testleri: Sanayi Profili Sayfası & Dashboard Entegrasyonu
"""

import pytest
import pandas as pd
from data_sources.local_official_data import build_master_dataset
from app_pages.industry_page import render_industry_page
from visualization.pixel_perfect_dashboard import generate_pixel_perfect_dashboard_html


@pytest.fixture
def master_df():
    return build_master_dataset()


def test_industry_page_data_integrity(master_df):
    """OSBÜK kayıtlı 419 OSB ve 143.267 Hektar verilerinin korunduğunu test eder."""
    total_osb = master_df["toplam_osb"].sum()
    total_area = master_df["osb_alani_hektar"].sum()

    assert total_osb == 419
    assert round(total_area) == 143267

    # Fonksiyonun çalışma hatası vermediğini doğrula
    render_industry_page(master_df)


def test_pixel_perfect_dashboard_modules_content(master_df):
    """Dashboard HTML çıktısında Sanayi modülünün eksiksiz yer aldığını doğrular."""
    html = generate_pixel_perfect_dashboard_html(master_df)

    # 2. Sanayi Profili Modülü Kontrolleri
    assert "Türkiye Geneli Toplam OSB Sayısı" in html
    assert "Toplam Tahsisli OSB Üretim Alanı" in html
    assert "Bölgesel OSB Yoğunluğu ve Çevre Baskısı Sıralaması" in html
    assert "Marmara Aksı (Kocaeli, Bursa, Tekirdağ)" in html
    assert "Güneydoğu Aksı (Gaziantep)" in html
    assert "KRİTİK BASKI" in html
    assert "SANAYİ SİCİLİ" in html
    assert "industryBarChart" in html
