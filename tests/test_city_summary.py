"""
Birim Testleri: İl özeti cümleleri, Türkçe sayı biçimi ve kirlilik kademeleri
"""

import pytest
import pandas as pd
from data_sources.local_official_data import build_master_dataset
from analytics.summaries import generate_city_summary, to_tr_num, get_dso_risk_tier

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

    # 1-2. Türkçe karakterli iller: sıralama veriden hesaplanan sırayla aynı olmalı
    for il in ["Iğdır", "Şanlıurfa", "İzmir", "Çanakkale"]:
        txt = " ".join(generate_city_summary(df, il)["sentences"])
        sira = int(df["pm25"].rank(ascending=True, method="min")[df["il"] == il].iloc[0])
        assert f"81 il içinde PM2,5'te {sira}. sırada (1 = en düşük)." in txt

    # Bölge ortalamasının altındaki il için fark negatif işaretli yazılmalı (−1 < fark < 0 dahil)
    from analytics.summaries import to_tr_num, to_tr_sign
    assert to_tr_num(-0.4, 1) == "-0,4"
    assert to_tr_sign(-0.4, 1) == "-0,4"
    assert to_tr_sign(0.4, 1) == "+0,4"

    # 3. İstanbul (En kalabalık il)
    ist = generate_city_summary(df, "İstanbul")
    ist_text = " ".join(ist["sentences"])
    assert "81 il içinde nüfus büyüklüğünde 1. sırada" in ist_text
    marmara_ort = df[df["bolge"] == "Marmara"]["pm25"].mean()
    assert f"Marmara Bölgesi ortalamasına ({to_tr_num(marmara_ort, 1)} µg/m³)" in ist_text
    assert ist["kunye"]["nufus"] == 15754053  # TÜİK ADNKS, 31.12.2025
    assert ist["kunye"]["plaka"] == 34
    assert ist["kunye"]["faal_osb"] == 8

    # 4. Bayburt (En az nüfuslu il)
    bayburt = generate_city_summary(df, "Bayburt")
    bayburt_text = " ".join(bayburt["sentences"])
    assert "81 il içinde nüfus büyüklüğünde 81. sırada" in bayburt_text


def test_dso_risk_tier_5_scales_and_afyonkarahisar():
    """DSÖ 2021 yıllık ara hedeflerine (10/15/25/35) dayalı 5 kademeyi ve master tabloyla tutarlılığı doğrular."""
    assert get_dso_risk_tier(4.0) == "Düşük"
    assert get_dso_risk_tier(10.0) == "Düşük"
    assert get_dso_risk_tier(10.1) == "Orta"
    assert get_dso_risk_tier(15.0) == "Orta"
    assert get_dso_risk_tier(15.1) == "Yüksek"
    assert get_dso_risk_tier(25.0) == "Yüksek"
    assert get_dso_risk_tier(25.1) == "Çok Yüksek"
    assert get_dso_risk_tier(35.0) == "Çok Yüksek"
    assert get_dso_risk_tier(35.1) == "Kritik"

    df = build_master_dataset()
    afyon = df[df["il"] == "Afyonkarahisar"].iloc[0]
    assert afyon["dso_risk"] == get_dso_risk_tier(afyon["pm25"])
    assert afyon["dso_risk"] != "Yüksek Risk"
