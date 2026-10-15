import pytest
import pandas as pd
from streamlit.testing.v1 import AppTest
from data_sources.local_official_data import build_master_dataset
from visualization.distribution_charts import create_regional_boxplot, create_regional_distribution_strip
from app_pages.regions_page import create_regional_benchmark_bar, render_regions_page
from analytics.hypothesis_tests import run_regional_anova


def test_regional_benchmark_bar_marmara_rounding_and_colors():
    df = build_master_dataset()
    fig = create_regional_benchmark_bar(df, pollutant="pm25")
    
    # Marmara bar text kontrolü
    bar_texts = fig.data[0].text
    marmara_text = [t for t in bar_texts if "35,7" in t]
    assert len(marmara_text) == 1
    assert "35,7 µg/m³" in marmara_text[0]
    assert "35.6 µg/m³" not in bar_texts
    assert "35,6 µg/m³" not in bar_texts

    # Tek ton mavi gradyan kontrolü: kırmızı ve turuncu renklerin kaldırıldığını doğrula
    colorscale = fig.data[0].marker.colorscale
    colors = [c[1].lower() for c in colorscale]
    assert "#ef4444" not in colors
    assert "#f97316" not in colors
    # Koyu ve açık mavi tonlarının varlığını doğrula
    assert any("083358" in c or "0284c7" in c or "38bdf8" in c for c in colors)

    # DSÖ vline ve tavan boşluğu kontrolü
    assert list(fig.layout.xaxis.range) == [0, 50]
    ann = [a for a in fig.layout.annotations if "DSÖ Yıllık Kılavuz Değeri" in a.text][0]
    assert ann.y == 1.04
    assert ann.yanchor == "bottom"
    assert ann.x == 5


def test_regional_distribution_strip_sorting_and_properties():
    df = build_master_dataset()
    fig = create_regional_distribution_strip(df, pollutant="pm25")
    
    # Başlığın kaldırıldığını doğrula
    assert fig.layout.title.text is None
    
    # Sıralamanın ortalamaya göre olduğunu doğrula (Doğu Anadolu -> Karadeniz)
    expected_order = df.groupby("bolge")["pm25"].mean().sort_values(ascending=False).index.tolist()
    assert expected_order[0] == "Doğu Anadolu"
    assert expected_order[-1] == "Karadeniz"

    # Alt boşluk ve yükseklik kontrolü
    assert fig.layout.margin.b == 70
    assert fig.layout.margin.t == 40
    assert fig.layout.margin.l == 50
    assert fig.layout.margin.r == 20
    assert fig.layout.height == 420
    assert fig.data[0].boxpoints == "all"
    assert fig.data[0].jitter == 0.35
    assert fig.data[0].pointpos == 0
    assert fig.data[0].marker.color == "#0ea5e9"
    assert fig.data[0].marker.size == 8
    assert fig.data[0].marker.opacity == 0.75
    assert fig.data[0].fillcolor == "rgba(0,0,0,0)"
    assert fig.data[0].line.color == "rgba(0,0,0,0)"
    assert len(fig.layout.shapes) == 7
    assert fig.layout.yaxis.title.text == "PM2.5 Düzeyi (µg/m³)"
    assert fig.layout.xaxis.title.text is None
    # Hover text format kontrolü (örn. "Iğdır: 82,1 µg/m³ (16,4x DSÖ)")
    assert any("µg/m³" in t and "x DSÖ" in t for t in fig.data[0].hovertext)


def test_regional_anova_academic_turkish():
    df = build_master_dataset()
    res = run_regional_anova(df, group_col="bolge", val_col="pm25")
    
    assert res["success"] is True
    # H0 ve H1 akademik Türkçe kontrolleri
    assert res["h0"] == "H₀: Bölgelerin ortalama PM2.5 kirlilik seviyeleri arasında istatistiksel olarak anlamlı bir fark yoktur."
    assert res["h1"] == "H₁: En az bir bölgenin kirlilik seviyesi diğer bölgelerden istatistiksel olarak anlamlı derecede farklıdır."
    assert "PM25" not in res["h0"]
    assert "PM25" not in res["h1"]
    
    # İstatistiksel değerlendirme cümlesi
    assert "gruplar arasında istatistiksel olarak anlamlı bir fark tespit edilmemiştir (p > 0.05)." in res["interpretation"]
    assert "anlamlı bir varyasyon tespit edilmemiştir" not in res["interpretation"]


def test_regions_page_apptest_rendering():
    def app_regions():
        import streamlit as st
        from data_sources.local_official_data import build_master_dataset
        from app_pages.regions_page import render_regions_page
        df = build_master_dataset()
        render_regions_page(df)

    at = AppTest.from_function(app_regions)
    at.run(timeout=15)
    
    assert not at.exception
    
    # Caption metinlerini kontrol et
    captions = [c.value for c in at.caption]
    all_captions = " ".join(captions)
    assert "DSÖ yıllık kılavuz sınırıdır (5 µg/m³)" in all_captions
    assert "Tüm bölge ortalamaları bu eşiğin 6 ila 9 katı üzerindedir" in all_captions
    assert "son 12 ay" not in all_captions
    assert ("Metodolojik Not: Bölgesel solunum ölüm hızları TÜİK kaba ölüm verisidir (yaş standardizasyonu içermez)." in all_captions or
            "Metodolojik Not: Bölgesel solunum ölüm hızları TÜİK kaba ölüm" in all_captions)
    
    # Tabloyu kontrol et
    assert len(at.dataframe) >= 1
    df_table = at.dataframe[0].value
    assert "Medyan PM2.5 (µg/m³)" in df_table.columns
    assert "Solunum Ölüm Hızı (Yüz Binde)" in df_table.columns
    assert "Solunum Ölüm Hızı (100k)" not in df_table.columns
    
    # Tablodaki Marmara değerinin Türkçe virgüllü olduğunu doğrula
    marmara_row = df_table[df_table["Bölge"] == "Marmara"]
    assert not marmara_row.empty
    assert marmara_row["Ort. PM2.5 (µg/m³)"].values[0] == "35,65"

    # ANOVA ve değerlendirme metinlerini kontrol et
    all_md = " ".join([m.value for m in at.markdown])
    assert "İstatistiksel Değerlendirme:" in all_md
    assert "İstatistiki Sonuç:" not in all_md
    assert "F = 1,04" in all_md
    assert "p = 0,407" in all_md
    assert "Bölgesel PM2.5 İl Dağılımı ve Kümelenmesi" in all_md
    assert "Fark Anlamsız (p > 0.05)" in all_md

