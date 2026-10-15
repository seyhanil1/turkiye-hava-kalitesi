import pytest
import pandas as pd
from streamlit.testing.v1 import AppTest
from data_sources.local_official_data import build_master_dataset
from app_pages.report_card import generate_city_summary, render_report_card_page, to_tr_num, get_dso_risk_tier


def test_generate_city_summary_all_81_provinces():
    """81 ilin tümü için özet cümlelerinin ve künyesinin hatasız üretildiğini doğrular."""
    df = build_master_dataset()
    assert len(df) == 81, "81 il bulunmalı"

    forbidden_words = [
        "avrupa",
        "sanayi yok",
        "çünkü",
        "nedeniyle",
        "kaynaklı",
        "sebebiyle",
        "yüzünden",
        "en temiz",
        "en kirli"
    ]

    for city_name in df["il"].unique():
        summary = generate_city_summary(df, city_name)
        assert summary is not None
        assert "sentences" in summary
        assert "kunye" in summary
        assert "footnote" in summary

        sentences = summary["sentences"]
        assert len(sentences) >= 5, f"{city_name} için en az 5 cümle üretilmeli"

        # Yasaklı kelime kontrolü (hiçbir cümlede geçmemeli)
        for s in sentences:
            for word in forbidden_words:
                assert word not in s.lower(), f"{city_name} için '{word}' yasaklı kelimesi bulundu: {s}"

        # Sıralama kalıbı kontrolü (1 = en düşük)
        assert "1 = en düşük" in sentences[0], f"PM2.5 sırasında '1 = en düşük' olmalı: {sentences[0]}"
        assert "1 = en düşük" in sentences[4], f"Solunum sırasında '1 = en düşük' olmalı: {sentences[4]}"

        # Künye kontrolleri
        kunye = summary["kunye"]
        assert kunye["nufus"] > 0
        assert kunye["bolge"] in df["bolge"].unique()
        assert 1 <= kunye["plaka"] <= 81
        assert kunye["toplam_osb"] >= 0


def test_city_summary_turkish_characters_and_edge_cases():
    """
    Türkçe karakterli illerde (Iğdır, Şanlıurfa, İzmir, Çanakkale) ve
    en kalabalık (İstanbul) ile en küçük (Bayburt) illerde uç durumları test eder.
    """
    df = build_master_dataset()

    # 1. Iğdır (Düşük OSB + Yüksek PM2.5 uç durumu)
    igdir = generate_city_summary(df, "Iğdır")
    igdir_text = " ".join(igdir["sentences"])
    assert "OSB sayısı düşük gruptayken PM2,5 yüksek gruptadır." in igdir_text
    assert "81 il içinde PM2,5'te 80. sırada (1 = en düşük)." in igdir_text

    # 2. Şanlıurfa (Yüksek OSB + Düşük PM2.5 uç durumu)
    urfa = generate_city_summary(df, "Şanlıurfa")
    urfa_text = " ".join(urfa["sentences"])
    assert "OSB sayısı yüksek gruptayken PM2,5 düşük gruptadır." in urfa_text
    assert "81 il içinde PM2,5'te 13. sırada (1 = en düşük)." in urfa_text

    # 3. İstanbul (En kalabalık il)
    ist = generate_city_summary(df, "İstanbul")
    ist_text = " ".join(ist["sentences"])
    assert "81 il içinde nüfus büyüklüğünde 1. sırada" in ist_text
    assert "Marmara Bölgesi ortalamasına (35,7 µg/m³) göre +2,7 µg/m³ fark göstermektedir." in ist_text
    assert ist["kunye"]["nufus"] == 15655924
    assert ist["kunye"]["plaka"] == 34
    assert ist["kunye"]["faal_osb"] == 8

    # 4. Bayburt (En az nüfuslu il)
    bayburt = generate_city_summary(df, "Bayburt")
    bayburt_text = " ".join(bayburt["sentences"])
    assert "81 il içinde nüfus büyüklüğünde 81. sırada" in bayburt_text


def test_report_card_apptest_rendering_and_dom():
    """
    AppTest ile Şehir Karnesi sayfasının DOM çıktısını test eder:
    - 'İl Özeti' ve 'İl Künyesi' başlıkları bulunmalı.
    - Eski 'Hava Kalitesi Eğilimi' veya 'Son 30 Günlük' bulunmamalı.
    - 'Parsel' veya 'Hektar' künyede bulunmamalı.
    - Metodolojik dipnot tam olarak bulunmalı.
    - Faal OSB satırı ve resmi birimler doğrulanmalı.
    """
    def app_report():
        import streamlit as st
        from app_pages.report_card import render_report_card_page
        from data_sources.local_official_data import build_master_dataset
        d = build_master_dataset()
        render_report_card_page(d)

    at = AppTest.from_function(app_report)
    at.run()

    assert not at.exception
    all_markdown = " ".join([m.value for m in at.markdown])

    # Yeni bölümler mevcut olmalı
    assert "İl Özeti" in all_markdown
    assert "İl Künyesi" in all_markdown

    # Eski bölümler kaldırılmış olmalı
    assert "Son 30 Günlük" not in all_markdown
    assert "Hava Kalitesi Eğilimi" not in all_markdown
    assert "(Faal)" not in all_markdown
    assert "Parsel" not in all_markdown
    assert "Hektar" not in all_markdown
    assert "/ 100k" not in all_markdown

    # İstenen zorunlu dipnot ve metodolojik düzeltme
    assert "PM2.5 verileri Copernicus CAMS atmosferik model reanalizine dayanmaktadır; kaba ölüm hızı yaş standardizasyonu içermez." in all_markdown
    assert "PM2,5 model/istasyon karması" not in all_markdown

    # Faal OSB ve resmi birim kontrolleri
    assert "Faal OSB:" in all_markdown
    assert "8 Adet (%88,9)" in all_markdown
    assert "(Yüz Binde)" in all_markdown
    assert "+2,7 µg/m³" in all_markdown

    # Yasaklı kelimeler DOM'da olmamalı
    assert "en temiz" not in all_markdown.lower()
    assert "en kirli" not in all_markdown.lower()
    assert "sanayi yok" not in all_markdown.lower()


def test_dso_risk_tier_5_scales_and_afyonkarahisar():
    """5 kademeli resmi DSÖ ölçeğini ve Afyonkarahisar'ın 'Hassas' sınıfını doğrular."""
    # Eşik kontrolleri
    assert get_dso_risk_tier(10.0) == "İyi"
    assert get_dso_risk_tier(15.0) == "İyi"
    assert get_dso_risk_tier(15.1) == "Orta"
    assert get_dso_risk_tier(30.0) == "Orta"
    assert get_dso_risk_tier(30.1) == "Hassas"
    assert get_dso_risk_tier(33.94) == "Hassas"
    assert get_dso_risk_tier(50.0) == "Hassas"
    assert get_dso_risk_tier(50.1) == "Sağlıksız"
    assert get_dso_risk_tier(70.0) == "Sağlıksız"
    assert get_dso_risk_tier(70.1) == "Kritik"

    # Afyonkarahisar kontrolü
    df = build_master_dataset()
    afyon = df[df["il"] == "Afyonkarahisar"].iloc[0]
    assert afyon["dso_risk"] == "Hassas"
    assert afyon["dso_risk"] != "Yüksek Risk"


def test_report_card_afyonkarahisar_rendering_and_query_sync():
    """URL parametresi ?il=Afyonkarahisar ile gelindiğinde 'Hassas' rozetinin basıldığını doğrular."""
    def app_afyon():
        import streamlit as st
        from app_pages.report_card import render_report_card_page
        from data_sources.local_official_data import build_master_dataset
        st.query_params["il"] = "Afyonkarahisar"
        d = build_master_dataset()
        render_report_card_page(d)

    at = AppTest.from_function(app_afyon)
    at.run()

    assert not at.exception
    all_markdown = " ".join([m.value for m in at.markdown])
    assert "Afyonkarahisar" in all_markdown
    assert "Hassas" in all_markdown
    assert "Yüksek Risk" not in all_markdown


def test_report_card_top_bar_hides_upper_city_selector():
    """Şehir Karnesi sayfasında üst navbarda şehir seçici bulunmadığını doğrular."""
    def app_top_bar():
        from app.app import render_shared_top_bar
        render_shared_top_bar(show_city=False)

    at = AppTest.from_function(app_top_bar)
    at.run()

    assert not at.exception
    select_labels = [s.label for s in at.selectbox]
    assert "İl veya bölge ara:" not in select_labels
    assert "Kirletici:" in select_labels

