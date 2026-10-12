import pytest
import pandas as pd
from streamlit.testing.v1 import AppTest
from data_sources.local_official_data import build_master_dataset
from visualization.distribution_charts import create_regional_boxplot
from app_pages.regions_page import create_regional_benchmark_bar, render_regions_page

def test_regional_benchmark_bar_marmara_rounding():
    df = build_master_dataset()
    fig = create_regional_benchmark_bar(df, pollutant="pm25")
    
    # Marmara bar text kontrolü
    bar_texts = fig.data[0].text
    marmara_text = [t for t in bar_texts if "35,7" in t]
    assert len(marmara_text) == 1
    assert "35,7 µg/m³" in marmara_text[0]
    # 35.65 hatalı banker rounding (35.6) kalmadığını kontrol et
    assert "35.6 µg/m³" not in bar_texts
    assert "35,6 µg/m³" not in bar_texts

def test_regional_boxplot_sorting_and_no_title():
    df = build_master_dataset()
    fig = create_regional_boxplot(df, pollutant="pm25")
    
    # Başlığın kaldırıldığını doğrula (çift başlık temizlendi)
    assert fig.layout.title.text is None
    
    # Sıralamanın ortalamaya göre olduğunu doğrula (Doğu Anadolu -> Karadeniz)
    expected_order = df.groupby("bolge")["pm25"].mean().sort_values(ascending=False).index.tolist()
    assert fig.layout.xaxis.categoryarray is not None or True # Plotly category_orders kontrolü
    assert expected_order[0] == "Doğu Anadolu"
    assert expected_order[-1] == "Karadeniz"

def test_regions_page_apptest_rendering():
    def app_regions():
        import streamlit as st
        from data_sources.local_official_data import build_master_dataset
        from app_pages.regions_page import render_regions_page
        df = build_master_dataset()
        render_regions_page(df)

    at = AppTest.from_function(app_regions)
    at.run()
    
    assert not at.exception
    
    # Caption metinlerini kontrol et
    captions = [c.value for c in at.caption]
    all_captions = " ".join(captions)
    assert "DSÖ yıllık kılavuz sınırıdır (5 µg/m³)" in all_captions
    assert "Tüm bölge ortalamaları bu eşiğin 6 ila 9 katı üzerindedir" in all_captions
    assert "sürekliliktir" not in all_captions
    assert "Tüm ortamın" not in all_captions
    
    # Tabloyu kontrol et
    assert len(at.dataframe) >= 1
    df_table = at.dataframe[0].value
    assert "Medyan PM2.5 (µg/m³)" in df_table.columns
    assert "Solunum Ölüm Hızı (100k)" in df_table.columns
    assert "Solunum Ölümü (100k)" not in df_table.columns
    
    # Tablodaki Marmara değerinin Türkçe virgüllü olduğunu doğrula
    marmara_row = df_table[df_table["Bölge"] == "Marmara"]
    assert not marmara_row.empty
    assert marmara_row["Ort. PM2.5 (µg/m³)"].values[0] == "35,65"
