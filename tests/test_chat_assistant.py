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


def test_button_3_osb_sehirler(master_df):
    resp = generate_local_response("🏭 En Çok OSB'li 3 İl", master_df)
    assert "OSB" in resp
    assert "Bursa" in resp


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
    assert "kalıplarla soru sorabilirsiniz" in resp or "hazır buton" in resp


def test_new_button_1_solunum_riski(master_df):
    resp = generate_local_response("Solunum Riski En Yüksek 3 İl", master_df)
    assert "Solunum Kaynaklı Vefat Oranı" in resp or "Solunum" in resp
    assert "Edirne" in resp
    assert "Çorum" in resp
    assert "Çanakkale" in resp


def test_new_button_2_dso_limit_asanlar(master_df):
    resp = generate_local_response("DSÖ Limitini En Çok Aşanlar", master_df)
    assert "DSÖ" in resp
    assert "Osmaniye" in resp
    assert "Iğdır" in resp


def test_new_button_3_sanayi_baskisi(master_df):
    resp = generate_local_response("Sanayi Baskısı En Yüksek İller", master_df)
    assert "Sanayi Baskısı" in resp
    assert "Ankara" in resp or "Bursa" in resp
    assert "OSB" in resp


def test_new_button_4_en_temiz_bolge(master_df):
    resp = generate_local_response("En Temiz Bölge", master_df)
    assert "Karadeniz" in resp
    assert "Havası En Temiz" in resp


def test_natural_language_queries(master_df):
    # 1. Havası en temiz bölge hangisi?
    resp_bolge = generate_local_response("Havası en temiz bölge hangisi?", master_df)
    assert "Karadeniz" in resp_bolge

    # 2. Bursa il profili
    resp_bursa = generate_local_response("Bursa il profili", master_df)
    assert "Bursa İli Çevre & Hava Kalitesi Karnesi" in resp_bursa
    assert "PM2.5" in resp_bursa
    assert "Organize Sanayi Bölgesi" in resp_bursa

    # 3. Hangi ilde solunum ölümü daha fazla?
    resp_sol = generate_local_response("Hangi ilde solunum ölümü daha fazla?", master_df)
    assert "Solunum" in resp_sol
    assert "Edirne" in resp_sol

    # 4. Kirlilik ve OSB ilişkisi
    resp_corr = generate_local_response("Kirlilik ve OSB ilişkisi", master_df)
    assert "Korelasyon" in resp_corr or "Spearman" in resp_corr
    assert "Marmara" in resp_corr

