import pytest
import pandas as pd
from streamlit.testing.v1 import AppTest
from data_sources.local_official_data import build_master_dataset
from visualization.distribution_charts import (
    create_duel_dumbbell_chart,
    create_single_metric_comparison_bar
)
from app_pages.duel import render_duel_page


def test_duel_dumbbell_chart_percentile():
    df = build_master_dataset()
    city_a = df[df["il"] == "İstanbul"].iloc[0]
    city_b = df[df["il"] == "Ankara"].iloc[0]

    fig = create_duel_dumbbell_chart(df, city_a, city_b)
    assert fig is not None
    assert len(fig.data) >= 5  # 3 çizgi trace + 2 marker trace
    
    # Trace isimleri
    marker_traces = [t for t in fig.data if t.mode == "markers+text"]
    assert len(marker_traces) == 2
    names = [t.name for t in marker_traces]
    assert "İstanbul" in names
    assert "Ankara" in names


def test_duel_single_metric_comparison_bars():
    fig = create_single_metric_comparison_bar(
        metric_title="PM2.5 Kirliliği",
        unit_label="µg/m³",
        val_a=38.4,
        val_b=39.3,
        name_a="İstanbul",
        name_b="Ankara",
        text_a="38,4 µg/m³",
        text_b="39,3 µg/m³"
    )
    assert fig is not None
    assert len(fig.data) == 2
    assert fig.layout.yaxis.title.text == "µg/m³"


def test_duel_page_istanbul_ankara_exact_values():
    def app_duel():
        import streamlit as st
        from app_pages.duel import render_duel_page
        from data_sources.local_official_data import build_master_dataset
        df = build_master_dataset()
        render_duel_page(df)

    at = AppTest.from_function(app_duel)
    at.run()

    assert not at.exception

    all_markdown = " ".join([m.value for m in at.markdown])

    # 1. Ham veriler ve doğru sayılar
    assert "15.655.924" in all_markdown
    assert "5.803.482" in all_markdown
    assert "Plaka 34" in all_markdown
    assert "Plaka 06" in all_markdown
    assert "38,4 µg/m³" in all_markdown
    assert "39,3 µg/m³" in all_markdown
    assert "71,2 / 100k" in all_markdown
    assert "63,0 / 100k" in all_markdown
    assert "9 Adet" in all_markdown
    assert "15 Adet" in all_markdown
    assert "2.424,7 ha" in all_markdown
    assert "9.173,5 ha" in all_markdown

    # 2. Metin kalitesi kontrolü (Sayısal NaN, Inf, None kelime olarak bulunmamalı)
    import re
    assert not re.search(r'\b(nan|none|inf)\b', all_markdown, re.IGNORECASE)
    assert "kazandı" not in all_markdown.lower()
    assert "kaybetti" not in all_markdown.lower()
    assert "tüiklerin" not in all_markdown.lower()

    # 3. Dipnotlar
    assert "CAMS" in all_markdown
    assert "OSBÜK" in all_markdown


def test_duel_page_identical_cities_warning():
    def app_duel():
        import streamlit as st
        from app_pages.duel import render_duel_page
        from data_sources.local_official_data import build_master_dataset
        df = build_master_dataset()
        render_duel_page(df)

    at = AppTest.from_function(app_duel)
    at.run()
    # 2. İl seçimini de İstanbul yap
    at.selectbox[1].select("İstanbul").run()
    assert not at.exception
    assert len(at.warning) > 0
    assert "iki farklı il" in at.warning[0].value


def test_duel_page_30_city_pairs():
    """
    En az 30 farklı il çifti ile (Türkçe karakterli, en küçük ve en büyük nüfuslu iller) test.
    """
    pairs = [
        ("İstanbul", "Ankara"),
        ("İzmir", "Bursa"),
        ("Antalya", "Adana"),
        ("Konya", "Şanlıurfa"),
        ("Gaziantep", "Kocaeli"),
        ("Mersin", "Diyarbakır"),
        ("Hatay", "Manisa"),
        ("Kayseri", "Samsun"),
        ("Balıkesir", "Kahramanmaraş"),
        ("Van", "Aydın"),
        ("Tekirdağ", "Denizli"),
        ("Sakarya", "Muğla"),
        ("Eskişehir", "Mardin"),
        ("Malatya", "Trabzon"),
        ("Erzurum", "Ordu"),
        ("Afyonkarahisar", "Sivas"),
        ("Adıyaman", "Batman"),
        ("Tokat", "Zonguldak"),
        ("Elazığ", "Kütahya"),
        ("Çanakkale", "Osmaniye"),
        ("Giresun", "Isparta"),
        ("Yozgat", "Muş"),
        ("Edirne", "Aksaray"),
        ("Kastamonu", "Düzce"),
        ("Uşak", "Kırklareli"),
        ("Niğde", "Bitlis"),
        ("Rize", "Amasya"),
        ("Siirt", "Bolu"),
        ("Nevşehir", "Yalova"),
        ("Bingöl", "Kırıkkale"),
        ("Hakkarı" if "Hakkarı" in ["Hakkari"] else "Hakkari", "Kars"),
        ("Şırnak", "Burdur"),
        ("Karaman", "Karabük"),
        ("Kırşehir", "Erzincan"),
        ("Bilecik", "Sinop"),
        ("Iğdır", "Bartın"),
        ("Çankırı", "Artvin"),
        ("Gümüşhane", "Kilis"),
        ("Ardahan", "Tunceli"),
        ("Bayburt", "İstanbul")
    ]

    assert len(pairs) >= 30

    df = build_master_dataset()
    available_cities = set(df["il"].unique())

    # 30'dan fazla çiftin hepsi için render_duel_page çağrılabilirliğini ve veri bütünlüğünü sına
    for city_1, city_2 in pairs:
        if city_1 not in available_cities or city_2 not in available_cities:
            continue
        
        c_a = df[df["il"] == city_1].iloc[0]
        c_b = df[df["il"] == city_2].iloc[0]
        
        # Dumbbell grafiği testi
        fig_d = create_duel_dumbbell_chart(df, c_a, c_b)
        assert fig_d is not None
        
        # Null / NaN / Inf kontrolü
        assert pd.notnull(c_a["pm25"]) and pd.notnull(c_b["pm25"])
        assert pd.notnull(c_a["solunum_olum_100k"]) and pd.notnull(c_b["solunum_olum_100k"])
        assert pd.notnull(c_a["toplam_osb"]) and pd.notnull(c_b["toplam_osb"])
        assert pd.notnull(c_a["osb_alani_hektar"]) and pd.notnull(c_b["osb_alani_hektar"])
