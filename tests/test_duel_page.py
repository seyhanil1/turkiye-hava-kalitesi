import pytest
import pandas as pd
from streamlit.testing.v1 import AppTest
from visualization.distribution_charts import create_duel_radar_chart
from app_pages.duel import render_duel_page
from data_sources.local_official_data import build_master_dataset

def test_duel_radar_chart_categories_and_styling():
    city_a = pd.Series({
        "il": "İstanbul",
        "pm25": 39.25,
        "toplam_osb": 15,
        "faal_osb": 10,
        "solunum_olum_100k": 63.0,
        "yesil_skor": 54.2
    })
    city_b = pd.Series({
        "il": "Ankara",
        "pm25": 24.1,
        "toplam_osb": 8,
        "faal_osb": 6,
        "solunum_olum_100k": 55.4,
        "yesil_skor": 62.1
    })
    
    fig = create_duel_radar_chart(city_a, city_b)
    
    # Trace theta categories
    categories = fig.data[0].theta
    assert "Hava Temizliği Skoru" in categories
    assert "Sanayi Baskısı (Düşük)" in categories
    assert "Solunum Sağlığı" in categories
    assert "Yeşil Dönüşüm Skoru" in categories
    
    # Eski etiketlerin kalmadığını kontrol et
    assert "Temiz Hava (Ters PM2.5)" not in categories
    assert "Hafif Sanayi Yükü" not in categories
    
    # Layout polar ayarları
    polar_layout = fig.layout.polar
    assert polar_layout.radialaxis.angle == 45
    assert polar_layout.radialaxis.range == (0, 100)

def test_duel_page_apptest_rendering():
    def app_duel():
        import streamlit as st
        from app_pages.duel import render_duel_page
        from data_sources.local_official_data import build_master_dataset
        df = build_master_dataset()
        render_duel_page(df)

    at = AppTest.from_function(app_duel)
    at.run()
    
    assert not at.exception
    
    # Selectbox etiketlerini kontrol et: "1. İl:" ve "2. İl:"
    select_labels = [s.label for s in at.selectbox]
    assert "1. İl:" in select_labels
    assert "2. İl:" in select_labels
    assert "1. Şehir (Grup A):" not in select_labels
    assert "2. Şehir (Grup B):" not in select_labels
    
    # Markdown çıktılarında kart başlığı ve format kontrolü
    all_markdown = " ".join([m.value for m in at.markdown])
    assert "TÜİK Solunum Ölüm Hızı" in all_markdown
    assert "TÜİK Solunum Ölümü" not in all_markdown
    assert " OSB" in all_markdown
    assert " / 100k" in all_markdown
    assert " / 100 Puan" in all_markdown
    assert " µg/m³" in all_markdown
    assert "Grup A" not in all_markdown
    assert "Grup B" not in all_markdown

def test_duel_page_identical_cities():
    def app_duel():
        import streamlit as st
        from app_pages.duel import render_duel_page
        from data_sources.local_official_data import build_master_dataset
        df = build_master_dataset()
        render_duel_page(df)

    at = AppTest.from_function(app_duel)
    at.run()
    # 2. Şehri de İstanbul yapalım
    at.selectbox[1].select("İstanbul").run()
    assert not at.exception
    assert len(at.info) > 0
    assert "iki farklı şehir" in at.info[0].value
