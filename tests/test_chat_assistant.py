"""
Birim Testleri: Yerel & Çevrimdışı AI Veri Asistanı Sorgu Motoru
"""

import pytest
import pandas as pd
from data_sources.local_official_data import build_master_dataset
from app_pages.chat_assistant_page import (
    generate_local_response,
    generate_assistant_response,
    detect_cities_in_prompt,
    normalize_tr
)


@pytest.fixture
def master_df():
    return build_master_dataset()


def test_turkish_normalization():
    assert normalize_tr("İSTANBUL") == "istanbul"
    assert normalize_tr("IĞDIR'da") == "igdir da"
    assert normalize_tr("ANKARA'YA") == "ankara ya"
    assert normalize_tr("Şanlıurfa") == "sanliurfa"


def test_city_detection_single_and_multiple(master_df):
    cities_single = detect_cities_in_prompt("Iğdır hava kirliliği", master_df)
    assert cities_single == ["Iğdır"]

    cities_compare = detect_cities_in_prompt("⚖️ İstanbul vs Ankara Kıyasla", master_df)
    assert cities_compare == ["İstanbul", "Ankara"]

    cities_suffix = detect_cities_in_prompt("İzmir'de ve Bursa'da sanayi durumu", master_df)
    assert "İzmir" in cities_suffix
    assert "Bursa" in cities_suffix


def test_button_1_riskli_3_sehir(master_df):
    resp = generate_local_response("🚨 En Riskli 3 Şehir", master_df)
    assert "En Riskli" in resp or "En Kirli" in resp
    assert "Osmaniye" in resp
    assert "Iğdır" in resp
    assert "Erzincan" in resp


def test_button_2_temiz_3_sehir(master_df):
    resp = generate_local_response("🌿 En Temiz 3 Şehir", master_df)
    assert "En Temiz" in resp
    assert "Tunceli" in resp
    assert "Artvin" in resp


def test_button_3_saglik_faturasi(master_df):
    resp = generate_local_response("💰 Ulusal Sağlık Faturası", master_df)
    assert "Ulusal Sağlık Faturası" in resp or "Toplam Sağlık Maliyeti" in resp
    assert "Milyon ₺" in resp
    assert "Trilyon ₺" in resp


def test_button_4_karsilastirma(master_df):
    resp = generate_local_response("⚖️ İstanbul vs Ankara Kıyasla", master_df)
    assert "İstanbul vs Ankara" in resp
    assert "Karşılaştırmalı" in resp
    assert "Organize Sanayi Bölgesi (OSB)" in resp
    assert "PM2.5 Kirlilik" in resp


def test_single_city_scorecard(master_df):
    resp = generate_local_response("Iğdır hava durumu nasıl?", master_df)
    assert "Iğdır İli Çevre & Hava Kalitesi Karnesi" in resp
    assert "PM2.5" in resp
    assert "DSÖ" in resp
    assert "Organize Sanayi Bölgesi" in resp


def test_unmatched_general_query_guide(master_df):
    resp = generate_local_response("Selam naber?", master_df)
    assert "HavaAtlası Yerel Veri Asistanı" in resp
    assert "Nasıl soru sorabilirsiniz" in resp or "kalıplarla soru sorabilirsiniz" in resp
    assert "4 hazır buton" in resp
