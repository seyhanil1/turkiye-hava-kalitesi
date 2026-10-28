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
    assert "PM2.5 Seviyesi En Yüksek" in resp
    for il in master_df.sort_values("pm25", ascending=False)["il"].head(3):
        assert il in resp


def test_button_2_temiz_3_sehir(master_df):
    resp = generate_local_response("🌿 En Temiz 3 Şehir", master_df)
    assert "PM2.5 Seviyesi En Düşük" in resp
    for il in master_df.sort_values("pm25")["il"].head(3):
        assert il in resp


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
    for il in master_df.sort_values("pm25", ascending=False)["il"].head(3):
        assert il in resp


def test_new_button_3_sanayi_baskisi(master_df):
    resp = generate_local_response("Sanayi Baskısı En Yüksek İller", master_df)
    assert "Sanayi Baskısı" in resp
    assert "Ankara" in resp or "Bursa" in resp
    assert "OSB" in resp


def test_new_button_4_en_temiz_bolge(master_df):
    resp = generate_local_response("En Temiz Bölge", master_df)
    assert master_df.groupby("bolge")["pm25"].mean().idxmin() in resp
    assert "En Temiz Coğrafi Bölge" in resp


def test_natural_language_queries(master_df):
    # 1. Havası en temiz bölge hangisi?
    resp_bolge = generate_local_response("Havası en temiz bölge hangisi?", master_df)
    assert master_df.groupby("bolge")["pm25"].mean().idxmin() in resp_bolge

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
    assert "Nüfus ile PM2.5" in resp_corr
    assert "nedensellik" in resp_corr


def test_six_analytical_questions(master_df):
    # Q1: Sanayisi az olmasına rağmen havası en kirli iller hangileri ve sebebi ne?
    q1 = "Sanayisi az olmasına rağmen havası en kirli iller hangileri ve sebebi ne?"
    r1 = generate_local_response(q1, master_df)
    assert "Sanayisi Az Olmasına Rağmen Havası En Kirli İller" in r1
    q1 = master_df["toplam_osb"].quantile(0.25)
    beklenen = master_df[master_df["toplam_osb"] <= q1].sort_values("pm25", ascending=False)["il"].head(4)
    for il in beklenen:
        assert il in r1
    assert "İnversiyon" in r1 or "inversiyon" in r1
    assert "Topoğrafik" in r1 or "topografik" in r1.lower()

    # Q2: DSÖ'nün 5 µg/m³ kılavuz değerini karşılayan temiz bir ilimiz var mı?
    q2 = "DSÖ'nün 5 µg/m³ kılavuz değerini karşılayan temiz bir ilimiz var mı?"
    r2 = generate_local_response(q2, master_df)
    assert "DSÖ" in r2
    assert "Hayır, 81 ilimizin hiçbirinde" in r2 or "%0" in r2
    assert "5 µg/m³" in r2

    # Q3: İstanbul ile Ankara'nın hava kalitesi ve sanayi yükünü kıyasla.
    q3 = "İstanbul ile Ankara'nın hava kalitesi ve sanayi yükünü kıyasla."
    r3 = generate_local_response(q3, master_df)
    assert "İstanbul vs Ankara" in r3 or ("İstanbul" in r3 and "Ankara" in r3)
    assert "PM2.5 Kirlilik Değeri" in r3
    assert "Organize Sanayi Bölgesi" in r3

    # Q4: Organize Sanayi Bölgesi (OSB) sayısı en yüksek illerde kirlilik ne durumda?
    q4 = "Organize Sanayi Bölgesi (OSB) sayısı en yüksek illerde kirlilik ne durumda?"
    r4 = generate_local_response(q4, master_df)
    assert "Organize Sanayi Bölgesi" in r4 or "OSB" in r4
    assert "Bursa" in r4
    assert "Marmara" in r4

    # Q5: Hava kirliliği ile solunum yolu ölümleri arasında doğrudan bir paralellik var mı?
    q5 = "Hava kirliliği ile solunum yolu ölümleri arasında doğrudan bir paralellik var mı?"
    r5 = generate_local_response(q5, master_df)
    assert "Hava Kirliliği ile Solunum Yolu Ölümleri" in r5
    assert "Doğrudan ve doğrusal bir birebir paralellik bulunmamaktadır" in r5 or "paralellik" in r5
    assert "Demografik Yaş Yapısı" in r5 or "yaş" in r5.lower()

    # Q6: Türkiye'nin havası en temiz ve en kirli coğrafi bölgeleri hangileridir?
    q6 = "Türkiye'nin havası en temiz ve en kirli coğrafi bölgeleri hangileridir?"
    r6 = generate_local_response(q6, master_df)
    assert "En Temiz Coğrafi Bölge" in r6
    assert "Karadeniz" in r6
    assert "En Kirli Coğrafi Bölge" in r6
    assert "Doğu Anadolu" in r6


def test_welcome_message_and_code_hygiene():
    import inspect
    from app_pages.chat_assistant_page import render_chat_assistant_page
    src = inspect.getsource(render_chat_assistant_page)

    # 1. "PM2.5 en yüksek 3 il" kaldırıldı
    assert "PM2.5 en yüksek 3 il" not in src

    # 2. Parantez içi geliştirici açıklamaları kaldırıldı
    assert "(TÜİK solunum ölüm oranlarını listeler)" not in src
    assert "(5 µg/m³ kılavuz sınırını aşım katları)" not in src
    assert "(OSB ve sanayi parseli sıralaması)" not in src

    # 3. 6 sorunun tamamı yer alıyor
    assert "Sanayisi az olmasına rağmen havası en kirli iller hangileri ve sebebi ne?" in src
    assert "DSÖ'nün 5 µg/m³ kılavuz değerini karşılayan temiz bir ilimiz var mı?" in src
    assert "İstanbul ile Ankara'nın hava kalitesi ve sanayi yükünü kıyasla." in src
    assert "Organize Sanayi Bölgesi (OSB) sayısı en yüksek illerde kirlilik ne durumda?" in src
    assert "Hava kirliliği ile solunum yolu ölümleri arasında doğrudan bir paralellik var mı?" in src
    assert "Türkiye'nin havası en temiz ve en kirli coğrafi bölgeleri hangileridir?" in src


