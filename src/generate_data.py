"""
Veri Birleştirme ve Güncelleme Betiği (Geriye Dönük Uyumluluk)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Kök dizini ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_sources.local_official_data import build_master_dataset

def verileri_birlestir():
    print("[*] CAMS yıllık, Kara Rapor istasyon, TÜİK ve OSBÜK verileri birleştiriliyor...")
    df_master = build_master_dataset()
    output_path = os.path.join("data", "master_data.csv")
    df_master.to_csv(output_path, index=False, encoding="utf-8")
    print(f"[+] BASARILI! 81 ilin birlesik verileri '{output_path}' dosyasina kaydedildi.")
    print("\nMaster Tablosundan Ilk 5 Satir:")
    print(df_master[["plaka", "il", "bolge", "pm25", "solunum_olum_100k"]].head())
    return df_master

if __name__ == "__main__":
    verileri_birlestir()