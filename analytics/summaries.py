"""
İl Özeti ve Türkçe Sayı Biçimlendirme Yardımcıları
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

Arayüzden bağımsızdır; web veri dışa aktarımı (scripts/export_web_data.py) tarafından kullanılır.
"""

from decimal import Decimal, ROUND_HALF_UP

import pandas as pd

from data_sources.constants import pm25_kademe_etiketi


def to_tr_num(val: float, decimals: int = 1) -> str:
    """Sayıları matematiksel doğru yuvarlamayla (ROUND_HALF_UP) Türkçe formatlar."""
    if pd.isnull(val):
        return "—"
    dec_fmt = "1" if decimals == 0 else f"0.{'0'*(decimals-1)}1"
    dec = Decimal(f"{float(val):.4f}").quantize(Decimal(dec_fmt), rounding=ROUND_HALF_UP)
    if decimals == 0:
        return f"{int(dec):,}".replace(",", ".")
    sign = "-" if dec < 0 else ""
    parts = f"{abs(dec):.{decimals}f}".split(".")
    int_part = f"{int(parts[0]):,}".replace(",", ".")
    return f"{sign}{int_part},{parts[1]}"


def to_tr_sign(val: float, decimals: int = 1) -> str:
    sign = "+" if val > 0 else ""
    return f"{sign}{to_tr_num(val, decimals)}"


def get_disp_val(val: float, decimals: int = 1) -> float:
    """Ekranda gösterilen yuvarlanmış sayısal değeri (ROUND_HALF_UP) döndürür."""
    if pd.isnull(val):
        return 0.0
    dec_fmt = "1" if decimals == 0 else f"0.{'0'*(decimals-1)}1"
    dec = Decimal(f"{float(val):.4f}").quantize(Decimal(dec_fmt), rounding=ROUND_HALF_UP)
    return float(dec)


def get_dso_risk_tier(val: float) -> str:
    """Yıllık PM2.5 için platform kademesini döndürür (eşikler DSÖ 2021 yıllık ara hedefleri)."""
    return pm25_kademe_etiketi(val)


def generate_city_summary(df: pd.DataFrame, city_name: str) -> dict:
    """
    Seçilen il için yalnızca veriden hesaplanan nesnel f-string özet cümleleri ve künye verilerini üretir.
    Değer yargısı, nedensellik ve sübjektif ifadeler içermez.
    """
    il_row = df[df["il"] == city_name].iloc[0]
    bolge = il_row["bolge"]

    # 1. PM2.5 Sırası (1 = en düşük)
    pm_rank = int(df["pm25"].rank(ascending=True, method="min")[df["il"] == city_name].iloc[0])
    sentence_pm_rank = f"81 il içinde PM2,5'te {pm_rank}. sırada (1 = en düşük)."

    # 2. DSÖ Kıyası
    dso_kat = il_row["pm25"] / 5.0
    sentence_dso = f"PM2,5 değeri DSÖ yıllık kılavuzunun (5 µg/m³) {to_tr_num(dso_kat, 1)} katı."

    # 3. Ortalama Farkı (Ekranda görünen yuvarlanmış değerler üzerinden fark)
    tr_ort = float(df["pm25"].mean())
    bolge_ort = float(df[df["bolge"] == bolge]["pm25"].mean())
    il_pm_disp = get_disp_val(il_row["pm25"], 1)
    tr_pm_disp = get_disp_val(tr_ort, 1)
    bolge_pm_disp = get_disp_val(bolge_ort, 1)
    diff_tr = round(il_pm_disp - tr_pm_disp, 1)
    diff_bolge = round(il_pm_disp - bolge_pm_disp, 1)
    diff_tr_str = to_tr_sign(diff_tr, 1)
    diff_bolge_str = to_tr_sign(diff_bolge, 1)
    sentence_ort_fark = (
        f"Türkiye düz il ortalamasına ({to_tr_num(tr_ort, 1)} µg/m³) göre {diff_tr_str} µg/m³, "
        f"{bolge} Bölgesi ortalamasına ({to_tr_num(bolge_ort, 1)} µg/m³) göre {diff_bolge_str} µg/m³ fark göstermektedir."
    )

    # 4. OSB Yoğunluğu & Uç Durum
    q1_osb = float(df["toplam_osb"].quantile(0.25))
    q3_osb = float(df["toplam_osb"].quantile(0.75))
    q1_pm = float(df["pm25"].quantile(0.25))
    q3_pm = float(df["pm25"].quantile(0.75))

    osb_val = float(il_row["toplam_osb"])
    pm_val = float(il_row["pm25"])

    if osb_val <= q1_osb:
        osb_group = "düşük grup"
    elif osb_val >= q3_osb:
        osb_group = "yüksek grup"
    else:
        osb_group = "orta grup"

    if pm_val <= q1_pm:
        pm_group = "düşük grup"
    elif pm_val >= q3_pm:
        pm_group = "yüksek grup"
    else:
        pm_group = "orta grup"

    if osb_group == "düşük grup" and pm_group == "yüksek grup":
        sentence_osb = "OSB sayısı düşük gruptayken PM2,5 yüksek gruptadır."
    elif osb_group == "yüksek grup" and pm_group == "düşük grup":
        sentence_osb = "OSB sayısı yüksek gruptayken PM2,5 düşük gruptadır."
    else:
        sentence_osb = f"OSB sayısı {osb_group}ta, PM2,5 değeri {pm_group}tadır."

    # 5. Solunum Ölüm Hızı Sırası ve Nüfus Sırası
    sol_rank = int(df["solunum_olum_100k"].rank(ascending=True, method="min")[df["il"] == city_name].iloc[0])
    nufus_rank = int(df["nufus"].rank(ascending=False, method="min")[df["il"] == city_name].iloc[0])

    sentence_sol_rank = f"81 il içinde solunum hastalıkları kaba ölüm hızında {sol_rank}. sırada (1 = en düşük, kaba hız)."
    sentence_nufus_rank = f"81 il içinde nüfus büyüklüğünde {nufus_rank}. sırada (1 = en yüksek)."

    sentences = [
        sentence_pm_rank,
        sentence_dso,
        sentence_ort_fark,
        sentence_osb,
        sentence_sol_rank,
        sentence_nufus_rank
    ]

    kunye = {
        "nufus": int(il_row["nufus"]),
        "bolge": bolge,
        "plaka": int(il_row["plaka"]),
        "toplam_osb": int(il_row["toplam_osb"]),
        "faal_osb": int(il_row.get("faal_osb", 0))
    }

    return {
        "sentences": sentences,
        "kunye": kunye,
        "footnote": "Not: PM2.5 verileri Copernicus CAMS atmosferik model reanalizine dayanmaktadır; kaba ölüm hızı yaş standardizasyonu içermez."
    }
