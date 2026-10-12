"""
Birim Testleri: Sanayi vs. Kirlilik Stratejik Risk Matrisi (Plotly Bubble Chart)
"""

import pytest
import pandas as pd
import plotly.graph_objects as go
from data_sources.local_official_data import build_master_dataset
from visualization.risk_matrix import create_strategic_risk_matrix


@pytest.fixture
def master_df():
    return build_master_dataset()


def test_create_strategic_risk_matrix_basic(master_df):
    fig = create_strategic_risk_matrix(master_df)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    trace = fig.data[0]
    assert trace.type == "scatter"
    assert "markers" in trace.mode


def test_create_strategic_risk_matrix_axes_and_data(master_df):
    fig = create_strategic_risk_matrix(master_df)
    trace = fig.data[0]
    # X ekseni: osb_sayisi, Y ekseni: pm25
    assert len(trace.x) == len(master_df)
    assert len(trace.y) == len(master_df)
    assert list(trace.x) == list(master_df["osb_sayisi"])
    assert list(trace.y) == list(master_df["pm25"])


def test_create_strategic_risk_matrix_thresholds_and_quadrants(master_df):
    fig = create_strategic_risk_matrix(master_df)
    annotations = fig.layout.annotations
    assert len(annotations) >= 6

    annotation_texts = [a.text for a in annotations if a.text]
    all_text = " ".join(annotation_texts)

    # 1. Yatay ve dikey eşik çizgileri
    assert "TR PM2.5 Ortalaması" in all_text
    assert "TR OSB Ortalaması" in all_text

    # 2. 4 Köşe Stratejik Kuadran Etiketleri
    assert "Coğrafi / Isınma Kaynaklı Risk" in all_text
    assert "Sanayi Yoğunluğu Kaynaklı Risk" in all_text
    assert "Ekolojik Güvenli Bölge" in all_text
    assert "Yeşil / Kontrollü Sanayi" in all_text


def test_create_strategic_risk_matrix_hover_and_colorscale(master_df):
    fig = create_strategic_risk_matrix(master_df)
    trace = fig.data[0]

    # Renk skalası neon renkler içermeli
    colorscale = trace.marker.colorscale
    assert colorscale is not None
    # Neon camgöbeği/yeşil (#00f2fe) ve neon kırmızı (#ff4b4b)
    cs_colors = [c[1] for c in colorscale]
    assert any("#00f2fe" in c.lower() for c in cs_colors)
    assert any("#ff4b4b" in c.lower() for c in cs_colors)

    # Hover kartı alanları
    hovertemplate = trace.hovertemplate
    assert "PM2.5 Kirlilik" in hovertemplate
    assert "DSÖ Sınır Katı" in hovertemplate
    assert "OSB Sayısı" in hovertemplate
    assert "Solunum Vefat" in hovertemplate


def test_create_strategic_risk_matrix_empty_df():
    empty_df = pd.DataFrame()
    fig = create_strategic_risk_matrix(empty_df)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 0
