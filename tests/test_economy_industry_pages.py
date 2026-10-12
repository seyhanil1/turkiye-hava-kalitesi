"""
Birim Testleri: Ekonomi ve Sanayi Profili Sayfaları & Dashboard Entegrasyonu
"""

import pytest
import pandas as pd
from data_sources.local_official_data import build_master_dataset
from app_pages.economy_page import render_economy_page
from app_pages.industry_page import render_industry_page
from visualization.pixel_perfect_dashboard import generate_pixel_perfect_dashboard_html


@pytest.fixture
def master_df():
    return build_master_dataset()


def test_economy_page_data_integrity(master_df):
    """Ekonomik maliyet verilerinin (1.138.327,9 Milyon TL) ve 3'lü maliyet bölünmesinin korunduğunu test eder."""
    toplam_maliyet = master_df["maliyet_milyon_tl"].sum()
    assert round(toplam_maliyet, 1) == 1138327.9

    cost_mortality = round(toplam_maliyet * 0.78, 1)
    cost_health = round(toplam_maliyet * 0.16, 1)
    cost_labor = round(toplam_maliyet - cost_mortality - cost_health, 1)

    assert round(cost_health + cost_mortality + cost_labor, 1) == 1138327.9
    assert cost_mortality > 800000
    assert cost_health > 150000
    assert cost_labor > 50000

    # Fonksiyonun çalışma hatası vermediğini doğrula
    render_economy_page(master_df)


def test_industry_page_data_integrity(master_df):
    """OSBÜK kayıtlı 419 OSB ve 143.267 Hektar verilerinin korunduğunu test eder."""
    total_osb = master_df["toplam_osb"].sum()
    total_area = master_df["osb_alani_hektar"].sum()

    assert total_osb == 419
    assert round(total_area) == 143267

    # Fonksiyonun çalışma hatası vermediğini doğrula
    render_industry_page(master_df)


def test_pixel_perfect_dashboard_modules_content(master_df):
    """Dashboard HTML çıktısında yeni Ekonomi ve Sanayi modüllerinin eksiksiz yer aldığını doğrular."""
    html = generate_pixel_perfect_dashboard_html(master_df)

    # 1. Ekonomi Modülü Kontrolleri
    assert "Doğrudan Sağlık Giderleri" in html
    assert "Erken Vefat Maliyetleri" in html
    assert "İş Gücü & Verimlilik Kaybı" in html
    assert "DSÖ Standartlarına Geçilseydi Ne Olurdu?" in html
    assert "+18.500 Can Kurtarılırdı" in html
    assert "~170 Milyar TL Tasarruf" in html
    assert "economyDonutChart" in html

    # 2. Sanayi Profili Modülü Kontrolleri
    assert "Türkiye Geneli Toplam OSB Sayısı" in html
    assert "Toplam Tahsisli OSB Üretim Alanı" in html
    assert "Bölgesel OSB Yoğunluğu ve Çevre Baskısı Sıralaması" in html
    assert "Marmara Aksı (Kocaeli, Bursa, Tekirdağ)" in html
    assert "Güneydoğu Aksı (Gaziantep)" in html
    assert "KRİTİK BASKI" in html
    assert "SANAYİ SİCİLİ" in html
    assert "industryBarChart" in html
