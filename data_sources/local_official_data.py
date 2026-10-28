"""
Yerel Resmi Veri Yükleyici ve Ayrıştırıcı Modülü
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

Veri Kaynakları:
1. Copernicus CAMS (Open-Meteo) 2025 yıllık PM2.5 / PM10 model ortalaması -> data/cams_annual_2025.csv
   (81 il merkezi, 12 ay saatlik veri; bkz. data_sources/cams_annual_connector.py)
2. Temiz Hava Hakkı Platformu, Kara Rapor 2025 — 2024 istasyon PM2.5 ölçümleri (doğrulama katmanı)
   -> data/kara_rapor_2025_istasyon.csv
3. TÜİK Ölüm ve Ölüm Nedeni İstatistikleri (2022-2025) -> data/tuik_saglik.xlsx
4. OSB verileri: OSBÜK (Ekim 2026) -> data/sanayi.txt

Not: Daha önce kullanılan data/hava_kirliligi.xlsx dosyasındaki il değerleri Kara Rapor 2025'in
yayımlanmış PM2.5 (istasyon azamisi 46,81 µg/m³) ve PM10 (40 µg/m³ üstü 32 il) bulgularıyla
uyuşmadığı ve kaynağı doğrulanamadığı için kaldırılmıştır.
"""

import os
import re
import unicodedata
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple

from data_sources.constants import (
    PLAKA_ILLER,
    IL_TO_PLAKA,
    BOLGELER,
    IL_BOLGE,
    KOORDINATLAR,
    NUFUSLAR,
    DSO_LIMITLERI,
    pm25_kademe_etiketi
)
from data_sources.cams_annual_connector import load_annual, DEFAULT_YEAR as CAMS_YILI

# AirQ+ / Kara Rapor 2025 yöntemi: PM2.5'te her 10 µg/m³ artış için tüm doğal nedenli
# ölümlerde göreli risk (RR) 1,08; karşı-olgu (counterfactual) düzeyi DSÖ kılavuzu 5 µg/m³.
AIRQ_RR_PER_10 = 1.08
AIRQ_KARSI_OLGU = 5.0

def normalize_text(text: str) -> str:
    """Türkçe karakter ve şapkalı harf normalizasyonu."""
    if not isinstance(text, str):
        return ""
    text = text.strip()
    replacements = {
        'â': 'a', 'Â': 'A', 'î': 'i', 'Î': 'I', 'û': 'u', 'Û': 'U',
        'İ': 'İ', 'ı': 'ı'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def parse_kara_rapor_istasyon(filepath: str = "data/kara_rapor_2025_istasyon.csv") -> pd.DataFrame:
    """
    Kara Rapor 2025'te yayımlanan 2024 yılı istasyon bazlı yıllık PM2.5 ortalamalarını okur.
    Rapor yalnızca en yüksek 10 istasyonu yayımladığından tablo 81 ili kapsamaz;
    il başına en yüksek istasyon değeri döndürülür.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Kara Rapor istasyon dosyası bulunamadı: {filepath}")
    df = pd.read_csv(filepath, encoding="utf-8")
    unknown = set(df["il"]) - set(PLAKA_ILLER.values())
    if unknown:
        raise ValueError(f"Kara Rapor istasyon dosyasında tanınmayan il adları: {unknown}")
    return (
        df.groupby("il", as_index=False)["pm25_istasyon_2024"].max()
        .rename(columns={"pm25_istasyon_2024": "pm25_istasyon_max_2024"})
    )


def parse_cams_annual(year: int = CAMS_YILI) -> pd.DataFrame:
    """CAMS yıllık il ortalamalarını (pm25_cams, pm10_cams) döndürür."""
    df = load_annual(year)
    if df["pm25_cams"].isna().any():
        eksik = df.loc[df["pm25_cams"].isna(), "il"].tolist()
        raise ValueError(f"CAMS yıllık verisinde %75 tamlık eşiğini geçemeyen iller: {eksik}")
    return df[["il", "pm25_cams", "pm10_cams"]]


def atfedilen_olum_orani(pm25: pd.Series) -> pd.Series:
    """AirQ+ log-lineer modeliyle PM2.5'e atfedilebilir ölüm payı (PAF, 0-1)."""
    fazla = (pm25 - AIRQ_KARSI_OLGU).clip(lower=0)
    rr = AIRQ_RR_PER_10 ** (fazla / 10.0)
    return 1.0 - 1.0 / rr

def parse_tuik_saglik(filepath: str = "data/tuik_saglik.xlsx") -> pd.DataFrame:
    """
    TÜİK Resmi Ölüm Nedeni Excel dosyasını ayrıştırır.
    Her il için 2022-2025 yılları arası solunum sistemi, dolaşım sistemi
    ve toplam ölüm sayılarını çıkarır.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"TÜİK Sağlık dosyası bulunamadı: {filepath}")
    
    df_raw = pd.read_excel(filepath, engine="xlrd", header=None)
    
    records = []
    current_il = None
    
    for idx in range(5, len(df_raw)):
        val0 = df_raw.iloc[idx, 0]
        if pd.notna(val0):
            current_il = normalize_text(str(val0))
        
        year_raw = str(df_raw.iloc[idx, 1]).strip()
        year_clean = re.sub(r"[^\d]", "", year_raw)
        
        if year_clean in ["2022", "2023", "2024", "2025"]:
            try:
                toplam = float(df_raw.iloc[idx, 2])
                dolasim = float(df_raw.iloc[idx, 3])
                tumor = float(df_raw.iloc[idx, 4])
                solunum = float(df_raw.iloc[idx, 5])
                records.append({
                    "il": current_il,
                    "yil": int(year_clean),
                    "toplam_olum": toplam,
                    "dolasim_olum": dolasim,
                    "tumor_olum": tumor,
                    "solunum_olum": solunum
                })
            except (ValueError, TypeError):
                continue
                
    df_tuik = pd.DataFrame(records)
    
    # Türkiye genelini ayır ve illeri standartlaştır
    il_map = {normalize_text(v): v for v in PLAKA_ILLER.values()}
    df_tuik = df_tuik[df_tuik["il"].isin(il_map.keys())].copy()
    df_tuik["il"] = df_tuik["il"].map(il_map)
    
    # 81 ilin tamamının bulunduğu en güncel yıl kullanılır (dosyaya yeni yıl eklendiğinde kendiliğinden geçer)
    il_sayisi = df_tuik.groupby("yil")["il"].nunique()
    son_yil = int(il_sayisi[il_sayisi == len(PLAKA_ILLER)].index.max())
    df_latest = df_tuik[df_tuik["yil"] == son_yil].copy()
    
    # İl bazlı özet istatistikler
    df_summary = df_tuik.groupby("il").agg(
        solunum_olum_ortalama=("solunum_olum", "mean"),
        toplam_olum_ortalama=("toplam_olum", "mean")
    ).reset_index()
    
    df_latest = pd.merge(df_latest, df_summary, on="il", how="left")
    return df_latest

def parse_sanayi_osb(filepath: str = "data/sanayi.txt") -> pd.DataFrame:
    """
    OSB tablosunu ayrıştırır (OSB verileri: OSBÜK (Ekim 2026)).
    İl bazında: Toplam OSB, Faal OSB, Toplam OSB Alanı (Hektar) ve Toplam Parsel sayısını hesaplar.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Sanayi dosyası bulunamadı: {filepath}")
    
    df_san = pd.read_csv(filepath, sep="\t", encoding="utf-8")
    il_col = df_san.columns[1]
    durum_col = df_san.columns[4]
    hektar_col = df_san.columns[6]
    parsel_col = df_san.columns[7]
    
    df_san["il_norm"] = df_san[il_col].astype(str).apply(normalize_text)
    
    # Sayısal dönüşümler: sanayi.txt dosyasında ondalık ayracı zaten standart noktadır (örn. 815.0, 217.81).
    # Nokta silinmemeli; virgül varsa noktaya çevrilerek standart sayısal dönüşüm yapılmalıdır.
    df_san["hektar"] = pd.to_numeric(
        df_san[hektar_col].astype(str).str.replace(",", ".", regex=False),
        errors="coerce"
    ).fillna(0.0)
    
    df_san["parsel"] = pd.to_numeric(
        df_san[parsel_col].astype(str).str.replace(",", ".", regex=False),
        errors="coerce"
    ).fillna(0.0)
    
    il_map = {normalize_text(v): v for v in PLAKA_ILLER.values()}
    df_san["il"] = df_san["il_norm"].map(il_map)
    
    # Agregasyon
    agg = df_san.groupby("il").agg(
        toplam_osb=("il", "count"),
        faal_osb=(durum_col, lambda s: s.str.contains("İŞLETMEDE|FAAL", case=False, na=False).sum()),
        osb_alani_hektar=("hektar", "sum"),
        toplam_parsel=("parsel", "sum")
    ).reset_index()
    
    # 81 il için eksik olanları 0 ile tamamla
    df_all_provinces = pd.DataFrame({"il": list(PLAKA_ILLER.values())})
    agg = pd.merge(df_all_provinces, agg, on="il", how="left").fillna(0)
    agg["toplam_osb"] = agg["toplam_osb"].astype(int)
    agg["faal_osb"] = agg["faal_osb"].astype(int)
    agg["toplam_parsel"] = agg["toplam_parsel"].astype(int)
    agg["osb_alani_hektar"] = agg["osb_alani_hektar"].round(1)
    
    return agg

def build_master_dataset() -> pd.DataFrame:
    """
    Tüm kaynakları (CAMS yıllık model, Kara Rapor istasyonları, TÜİK, OSBÜK, ADNKS Nüfus,
    Coğrafi Koordinatlar) tek bir analitik ana veri tablosunda (Master Dataset) birleştirir.
    `pm25` sütunu CAMS 2025 yıllık model ortalamasıdır (istasyon ölçümü değildir).
    """
    df_cams = parse_cams_annual()
    df_istasyon = parse_kara_rapor_istasyon()
    df_tuik = parse_tuik_saglik()
    df_sanayi = parse_sanayi_osb()
    
    # Temel il listesi
    df_master = pd.DataFrame({"il": [PLAKA_ILLER[i] for i in range(1, 82)]})
    df_master["plaka"] = df_master["il"].map(IL_TO_PLAKA)
    df_master["bolge"] = df_master["il"].map(IL_BOLGE)
    df_master["lat"] = df_master["il"].map(lambda x: KOORDINATLAR.get(x, (39.0, 35.0))[0])
    df_master["lon"] = df_master["il"].map(lambda x: KOORDINATLAR.get(x, (39.0, 35.0))[1])
    df_master["nufus"] = df_master["il"].map(NUFUSLAR)
    
    # 1. Hava Kirliliği Verisi: CAMS yıllık model (81 il) + Kara Rapor istasyon azamisi (varsa)
    df_master = pd.merge(df_master, df_cams, on="il", how="left")
    df_master["pm25"] = df_master["pm25_cams"]
    df_master["pm25_kaynak"] = f"CAMS {CAMS_YILI} yıllık model"
    df_master = pd.merge(df_master, df_istasyon, on="il", how="left")
    
    # 2. Sanayi Verisi
    df_master = pd.merge(df_master, df_sanayi, on="il", how="left")
    df_master["toplam_osb"] = df_master["toplam_osb"].fillna(0).astype(int)
    df_master["faal_osb"] = df_master["faal_osb"].fillna(0).astype(int)
    df_master["osb_alani_hektar"] = df_master["osb_alani_hektar"].fillna(0.0)
    df_master["toplam_parsel"] = df_master["toplam_parsel"].fillna(0).astype(int)
    
    # Geriye dönük uyumluluk için osb_sayisi kolonu
    df_master["osb_sayisi"] = df_master["toplam_osb"]
    
    # 4. TÜİK Sağlık Verisi
    df_master = pd.merge(
        df_master,
        df_tuik[["il", "yil", "solunum_olum", "toplam_olum", "solunum_olum_ortalama"]].rename(columns={"yil": "olum_yili"}),
        on="il",
        how="left"
    )
    
    # Ham (yaşa göre standartlaştırılmamış) 100.000 kişi başına solunum yolu ölüm oranı.
    # DİKKAT: Yaşlı nüfusu fazla illerde yüksek çıkar; toplam ölüm hızıyla r≈0,88 ilişkilidir.
    # Kirlilik karşılaştırmalarında `solunum_olum_payi` veya `atfedilen_olum_tahmini` tercih edilmelidir.
    df_master["solunum_olum_100k"] = (
        (df_master["solunum_olum"] / df_master["nufus"]) * 100_000
    ).round(1)
    df_master["toplam_olum_100k"] = (
        (df_master["toplam_olum"] / df_master["nufus"]) * 100_000
    ).round(1)

    # Solunum ölümlerinin tüm ölümler içindeki payı (%): genel ölüm düzeyini/yaş yapısını kısmen dengeler
    df_master["solunum_olum_payi"] = (
        df_master["solunum_olum"] / df_master["toplam_olum"] * 100
    ).round(2)

    # PM2.5'e atfedilebilir ölüm tahmini (AirQ+ yöntemi, Kara Rapor 2025 ile aynı RR=1,08).
    # Tüm yaşlardaki toplam ölümler kullanıldığından (TÜİK il verisinde 30+ ve dış neden ayrımı yok)
    # yaklaşık bir üst tahmindir.
    df_master["atfedilen_olum_payi"] = (atfedilen_olum_orani(df_master["pm25"]) * 100).round(2)
    df_master["atfedilen_olum_tahmini"] = (
        df_master["toplam_olum"] * df_master["atfedilen_olum_payi"] / 100
    ).round(0)

    # 5. Kirlilik kademesi (DSÖ 2021 yıllık ara hedeflerine dayalı platform sınıflandırması)
    df_master["dso_risk"] = df_master["pm25"].apply(pm25_kademe_etiketi)
    
    # DSÖ 5 µg/m³ kılavuz limitine oran
    df_master["dso_limit_kat"] = (df_master["pm25"] / 5.0).round(1)
    
    # 6. Sanayi Profili Sınıflandırması (yalnızca OSB sayısı/parsele dayanır, kirlilik içermez)
    def sanayi_profili(row) -> str:
        if row["toplam_osb"] >= 8 or row["toplam_parsel"] >= 1500:
            return "Yoğun OSB"
        elif row["toplam_osb"] >= 3 or row["toplam_parsel"] >= 400:
            return "Gelişmekte Olan Sanayi"
        else:
            return "Tarım / Hizmet / Kırsal"
            
    df_master["sanayi_tipi"] = df_master.apply(sanayi_profili, axis=1)
    
    # Doğrulama: 81 il tam olmalı
    assert len(df_master) == 81, f"Beklenen 81 il, bulunan {len(df_master)}"
    return df_master

if __name__ == "__main__":
    df = build_master_dataset()
    print("Master dataset başarıyla oluşturuldu:")
    print(df.info())
    print("\nİlk 5 satır:")
    print(df[["plaka", "il", "bolge", "pm25", "solunum_olum_100k"]].head())

