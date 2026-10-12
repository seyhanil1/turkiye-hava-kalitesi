"""
HavaAtlası - Türkiye Coğrafi, İdari ve Sağlık Sabitleri
Kaynaklar:
- TÜİK Adrese Dayalı Nüfus Kayıt Sistemi (ADNKS)
- T.C. İçişleri Bakanlığı İller İdaresi Genel Müdürlüğü
- Dünya Sağlık Örgütü (WHO) Küresel Hava Kalitesi Kılavuzları (2021)
"""

# 81 İl için Plaka Kodu ve Standart Türkçe İsimler
PLAKA_ILLER = {
    1: "Adana", 2: "Adıyaman", 3: "Afyonkarahisar", 4: "Ağrı", 5: "Amasya",
    6: "Ankara", 7: "Antalya", 8: "Artvin", 9: "Aydın", 10: "Balıkesir",
    11: "Bilecik", 12: "Bingöl", 13: "Bitlis", 14: "Bolu", 15: "Burdur",
    16: "Bursa", 17: "Çanakkale", 18: "Çankırı", 19: "Çorum", 20: "Denizli",
    21: "Diyarbakır", 22: "Edirne", 23: "Elazığ", 24: "Erzincan", 25: "Erzurum",
    26: "Eskişehir", 27: "Gaziantep", 28: "Giresun", 29: "Gümüşhane", 30: "Hakkari",
    31: "Hatay", 32: "Isparta", 33: "Mersin", 34: "İstanbul", 35: "İzmir",
    36: "Kars", 37: "Kastamonu", 38: "Kayseri", 39: "Kırklareli", 40: "Kırşehir",
    41: "Kocaeli", 42: "Konya", 43: "Kütahya", 44: "Malatya", 45: "Manisa",
    46: "Kahramanmaraş", 47: "Mardin", 48: "Muğla", 49: "Muş", 50: "Nevşehir",
    51: "Niğde", 52: "Ordu", 53: "Rize", 54: "Sakarya", 55: "Samsun",
    56: "Siirt", 57: "Sinop", 58: "Sivas", 59: "Tekirdağ", 60: "Tokat",
    61: "Trabzon", 62: "Tunceli", 63: "Şanlıurfa", 64: "Uşak", 65: "Van",
    66: "Yozgat", 67: "Zonguldak", 68: "Aksaray", 69: "Bayburt", 70: "Karaman",
    71: "Kırıkkale", 72: "Batman", 73: "Şırnak", 74: "Bartın", 75: "Ardahan",
    76: "Iğdır", 77: "Yalova", 78: "Karabük", 79: "Kilis", 80: "Osmaniye",
    81: "Düzce"
}

IL_TO_PLAKA = {v: k for k, v in PLAKA_ILLER.items()}

# 7 Coğrafi Bölge Eşleştirmesi
BOLGELER = {
    "Marmara": [
        "İstanbul", "Edirne", "Kırklareli", "Tekirdağ", "Çanakkale", 
        "Kocaeli", "Yalova", "Sakarya", "Bilecik", "Bursa", "Balıkesir"
    ],
    "Ege": [
        "İzmir", "Manisa", "Aydın", "Denizli", "Muğla", 
        "Afyonkarahisar", "Kütahya", "Uşak"
    ],
    "Akdeniz": [
        "Antalya", "Burdur", "Isparta", "Mersin", "Adana", 
        "Hatay", "Osmaniye", "Kahramanmaraş"
    ],
    "İç Anadolu": [
        "Ankara", "Konya", "Kayseri", "Eskişehir", "Sivas", "Kırıkkale", 
        "Aksaray", "Karaman", "Kırşehir", "Niğde", "Nevşehir", "Yozgat", "Çankırı"
    ],
    "Karadeniz": [
        "Amasya", "Artvin", "Bartın", "Bayburt", "Bolu", "Çorum", "Düzce", 
        "Giresun", "Gümüşhane", "Karabük", "Kastamonu", "Ordu", "Rize", 
        "Samsun", "Sinop", "Tokat", "Trabzon", "Zonguldak"
    ],
    "Doğu Anadolu": [
        "Ağrı", "Ardahan", "Bingöl", "Bitlis", "Elazığ", "Erzincan", "Erzurum", 
        "Hakkari", "Iğdır", "Kars", "Malatya", "Muş", "Tunceli", "Van"
    ],
    "Güneydoğu Anadolu": [
        "Adıyaman", "Batman", "Diyarbakır", "Gaziantep", "Kilis", 
        "Mardin", "Siirt", "Şanlıurfa", "Şırnak"
    ]
}

IL_BOLGE = {il: bolge for bolge, iller in BOLGELER.items() for il in iller}

# İl Koordinatları (Enlem, Boylam)
KOORDINATLAR = {
    "Adana": (37.0017, 35.3289), "Adıyaman": (37.7648, 38.2786),
    "Afyonkarahisar": (38.7569, 30.5387), "Ağrı": (39.7217, 43.0567),
    "Amasya": (40.6534, 35.8331), "Ankara": (39.9334, 32.8597),
    "Antalya": (36.8969, 30.7133), "Artvin": (41.1828, 41.8183),
    "Aydın": (37.8444, 27.8458), "Balıkesir": (39.6484, 27.8826),
    "Bilecik": (40.1451, 29.9799), "Bingöl": (38.8847, 40.4982),
    "Bitlis": (38.4006, 42.1095), "Bolu": (40.7358, 31.6061),
    "Burdur": (37.7203, 30.2908), "Bursa": (40.1885, 29.0610),
    "Çanakkale": (40.1553, 26.4142), "Çankırı": (40.6013, 33.6134),
    "Çorum": (40.5506, 34.9556), "Denizli": (37.7765, 29.0864),
    "Diyarbakır": (37.9144, 40.2306), "Edirne": (41.6772, 26.5557),
    "Elazığ": (38.6810, 39.2264), "Erzincan": (39.7500, 39.5000),
    "Erzurum": (39.9043, 41.2679), "Eskişehir": (39.7667, 30.5256),
    "Gaziantep": (37.0662, 37.3833), "Giresun": (40.9128, 38.3895),
    "Gümüşhane": (40.4600, 39.4814), "Hakkari": (37.5833, 43.7333),
    "Hatay": (36.4018, 36.3498), "Isparta": (37.7648, 30.5566),
    "Mersin": (36.8121, 34.6415), "İstanbul": (41.0082, 28.9784),
    "İzmir": (38.4192, 27.1287), "Kars": (40.6013, 43.0975),
    "Kastamonu": (41.3887, 33.7827), "Kayseri": (38.7312, 35.4787),
    "Kırklareli": (41.7333, 27.2167), "Kırşehir": (39.1425, 34.1709),
    "Kocaeli": (40.8533, 29.8815), "Konya": (37.8667, 32.4833),
    "Kütahya": (39.4167, 29.9833), "Malatya": (38.3552, 38.3095),
    "Manisa": (38.6191, 27.4289), "Kahramanmaraş": (37.5858, 36.9371),
    "Mardin": (37.3212, 40.7245), "Muğla": (37.2153, 28.3636),
    "Muş": (38.7432, 41.5064), "Nevşehir": (38.6244, 34.7144),
    "Niğde": (37.9667, 34.6833), "Ordu": (40.9839, 37.8764),
    "Rize": (41.0201, 40.5234), "Sakarya": (40.7569, 30.3783),
    "Samsun": (41.2928, 36.3313), "Siirt": (37.9333, 41.9500),
    "Sinop": (42.0231, 35.1531), "Sivas": (39.7477, 37.0179),
    "Tekirdağ": (40.9833, 27.5167), "Tokat": (40.3167, 36.5500),
    "Trabzon": (41.0015, 39.7178), "Tunceli": (39.1079, 39.5401),
    "Şanlıurfa": (37.1674, 38.7955), "Uşak": (38.6823, 29.4082),
    "Van": (38.4891, 43.4089), "Yozgat": (39.8181, 34.8147),
    "Zonguldak": (41.4564, 31.7987), "Aksaray": (38.3687, 34.0370),
    "Bayburt": (40.2552, 40.2249), "Karaman": (37.1759, 33.2287),
    "Kırıkkale": (39.8468, 33.5153), "Batman": (37.8812, 41.1294),
    "Şırnak": (37.5164, 42.4594), "Bartın": (41.6344, 32.3375),
    "Ardahan": (41.1105, 42.7022), "Iğdır": (39.9167, 44.0333),
    "Yalova": (40.6500, 29.2667), "Karabük": (41.2061, 32.6204),
    "Kilis": (36.7184, 37.1212), "Osmaniye": (37.0742, 36.2472),
    "Düzce": (40.8438, 31.1565)
}

# TÜİK Adrese Dayalı Nüfus Kayıt Sistemi (ADNKS Resmi İl Nüfusları - 2023/2024)
NUFUSLAR = {
    "Adana": 2270298, "Adıyaman": 604978, "Afyonkarahisar": 751344, "Ağrı": 510626,
    "Amasya": 339529, "Ankara": 5803482, "Antalya": 2696249, "Artvin": 172356,
    "Aydın": 1161702, "Balıkesir": 1273519, "Bilecik": 228058, "Bingöl": 285655,
    "Bitlis": 357367, "Bolu": 324789, "Burdur": 277452, "Bursa": 3214571,
    "Çanakkale": 570077, "Çankırı": 200244, "Çorum": 524130, "Denizli": 1059082,
    "Diyarbakır": 1818133, "Edirne": 419913, "Elazığ": 604411, "Erzincan": 243399,
    "Erzurum": 749993, "Eskişehir": 915418, "Gaziantep": 2164134, "Giresun": 461712,
    "Gümüşhane": 148539, "Hakkari": 287431, "Hatay": 1544640, "Isparta": 449777,
    "Mersin": 1938389, "İstanbul": 15655924, "İzmir": 4479525, "Kars": 278335,
    "Kastamonu": 388990, "Kayseri": 1445495, "Kırklareli": 377156, "Kırşehir": 247179,
    "Kocaeli": 2102907, "Konya": 2320641, "Kütahya": 575670, "Malatya": 742725,
    "Manisa": 1475716, "Kahramanmaraş": 1116618, "Mardin": 888874, "Muğla": 1066736,
    "Muş": 399879, "Nevşehir": 315994, "Niğde": 377080, "Ordu": 775800,
    "Rize": 350506, "Sakarya": 1098115, "Samsun": 1377546, "Siirt": 331311,
    "Sinop": 229702, "Sivas": 650401, "Tekirdağ": 1167459, "Tokat": 606934,
    "Trabzon": 824352, "Tunceli": 89317, "Şanlıurfa": 2213964, "Uşak": 377001,
    "Van": 1127612, "Yozgat": 418442, "Zonguldak": 591492, "Aksaray": 438504,
    "Bayburt": 86047, "Karaman": 263960, "Kırıkkale": 285744, "Batman": 647205,
    "Şırnak": 570745, "Bartın": 207238, "Ardahan": 92819, "Iğdır": 209738,
    "Yalova": 304780, "Karabük": 255242, "Kilis": 155179, "Osmaniye": 557666,
    "Düzce": 409865
}

# Meteoroloji Genel Müdürlüğü (MGM) Resmi İl Merkezi İstasyon Rakımları (Metre)
IL_RAKIM = {
    "Adana": 23, "Adıyaman": 669, "Afyonkarahisar": 1021, "Ağrı": 1632, "Amasya": 411,
    "Ankara": 890, "Antalya": 39, "Artvin": 345, "Aydın": 65, "Balıkesir": 145,
    "Bilecik": 513, "Bingöl": 1151, "Bitlis": 1545, "Bolu": 726, "Burdur": 957,
    "Bursa": 100, "Çanakkale": 6, "Çankırı": 730, "Çorum": 772, "Denizli": 420,
    "Diyarbakır": 675, "Edirne": 48, "Elazığ": 1067, "Erzincan": 1185, "Erzurum": 1890,
    "Eskişehir": 788, "Gaziantep": 855, "Giresun": 10, "Gümüşhane": 1153, "Hakkari": 1720,
    "Hatay": 85, "Isparta": 1035, "Mersin": 10, "İstanbul": 40, "İzmir": 15,
    "Kars": 1768, "Kastamonu": 775, "Kayseri": 1050, "Kırklareli": 203, "Kırşehir": 985,
    "Kocaeli": 28, "Konya": 1016, "Kütahya": 969, "Malatya": 964, "Manisa": 71,
    "Kahramanmaraş": 568, "Mardin": 1083, "Muğla": 660, "Muş": 1334, "Nevşehir": 1150,
    "Niğde": 1229, "Ordu": 5, "Rize": 6, "Sakarya": 31, "Samsun": 4,
    "Siirt": 895, "Sinop": 32, "Sivas": 1285, "Tekirdağ": 37, "Tokat": 623,
    "Trabzon": 39, "Tunceli": 914, "Şanlıurfa": 518, "Uşak": 907, "Van": 1727,
    "Yozgat": 1300, "Zonguldak": 135, "Aksaray": 980, "Bayburt": 1550, "Karaman": 1033,
    "Kırıkkale": 718, "Batman": 550, "Şırnak": 1400, "Bartın": 25, "Ardahan": 1829,
    "Iğdır": 858, "Yalova": 2, "Karabük": 280, "Kilis": 660, "Osmaniye": 125,
    "Düzce": 160
}

# DSÖ (WHO 2021) Hava Kalitesi Kılavuz Değerleri (µg/m³)
# Kaynak: WHO Global Air Quality Guidelines (2021)
# Önemli Not: DSÖ kılavuzuna göre PM2.5 için risksiz/güvenli bir alt sınır yoktur;
# 5 µg/m³ seviyesi sağlık risklerini minimize etmeyi amaçlayan yıllık kılavuz değerdir.
DSO_KILAVUZ_DEGERLERI = {
    "pm25": {
        "yillik_kilavuz": 5.0,
        "gunluk_kilavuz_24h": 15.0,
        "ara_hedef_1": 35.0,
        "ara_hedef_2": 25.0,
        "ara_hedef_3": 15.0,
        "ara_hedef_4": 10.0,
        "birim": "µg/m³",
        "kaynak": "Dünya Sağlık Örgütü (WHO) Küresel Hava Kalitesi Kılavuzları (2021)",
        "aciklama": "DSÖ'ye göre PM2.5 için güvenli bir eşik yoktur; 5 µg/m³ yıllık kılavuz değerdir."
    }
}

# Geriye dönük uyumluluk için eski isim de korunur
DSO_LIMITLERI = DSO_KILAVUZ_DEGERLERI

# ==========================================
# TEK UNİFİED KİRLİLİK KADEMELENDİRMESİ
# ==========================================
# Tüm sitede (harita, lejant, şehir sıralaması rozetleri, dağılım çubuğu)
# kullanılan tek ve tutarlı operasyonel sınıflandırma.
# Toplam kategori sayısı 5 olup, 81 ilin tamamını kapsar (c1+c2+c3+c4+c5 = 81).
KIRLILIK_KADEMELERI = {
    "kaynak_aciklamasi": "Bu panele özgü operasyonel sınıflandırmadır (DSÖ 2021 24 saatlik 15 µg/m³ kılavuz değeri ve ara hedefleri referans alınmıştır).",
    "pm25": [
        {
            "id": "iyi",
            "etiket": "İyi",
            "tam_ad": "İyi Düzey (≤15 µg/m³)",
            "min_val": 0.0,
            "max_val": 15.0,
            "renk": "#00e599",
            "bg": "rgba(0, 229, 153, 0.15)",
            "border": "#00e599",
            "aciklama": "DSÖ 24 saatlik kılavuz değeri (15 µg/m³) altındaki seviye."
        },
        {
            "id": "orta",
            "etiket": "Orta",
            "tam_ad": "Orta Düzey (15,1 - 30 µg/m³)",
            "min_val": 15.0,
            "max_val": 30.0,
            "renk": "#facc15",
            "bg": "rgba(250, 204, 21, 0.15)",
            "border": "#facc15",
            "aciklama": "DSÖ yıllık kılavuzunun üzerinde, orta düzey partikül yükü."
        },
        {
            "id": "hassas",
            "etiket": "Hassas",
            "tam_ad": "Hassas Grup Riski (30,1 - 50 µg/m³)",
            "min_val": 30.0,
            "max_val": 50.0,
            "renk": "#f97316",
            "bg": "rgba(249, 115, 22, 0.15)",
            "border": "#f97316",
            "aciklama": "DSÖ Ara Hedef-1 sınırını aşan, kronik/çocuk/yaşlı gruplar için riskli seviye."
        },
        {
            "id": "sagliksiz",
            "etiket": "Sağlıksız",
            "tam_ad": "Sağlıksız Seviye (50,1 - 70 µg/m³)",
            "min_val": 50.0,
            "max_val": 70.0,
            "renk": "#f87171",
            "bg": "rgba(248, 113, 113, 0.15)",
            "border": "#f87171",
            "aciklama": "Tüm nüfus için solunum ve dolaşım sağlığı riski."
        },
        {
            "id": "kritik",
            "etiket": "Kritik",
            "tam_ad": "Kritik / Ağır Risk (>70 µg/m³)",
            "min_val": 70.0,
            "max_val": 999.0,
            "renk": "#ef4444",
            "bg": "rgba(239, 68, 68, 0.15)",
            "border": "#ef4444",
            "aciklama": "Acil durum uyarısı gerektiren yüksek maruziyet seviyesi."
        }
    ]
}


def get_dataset_date_info() -> dict:
    """
    Veri setindeki gerçek ilk ve son tarihleri otomatik hesaplar.
    Canlı veri iddiası yerine doğrulanabilir gözlem dönemini döndürür.
    """
    import os
    import pandas as pd
    
    csv_paths = [
        os.path.join("data", "daily_city_air_quality.csv"),
        os.path.join("data", "daily_air_quality_90d.csv")
    ]
    
    start_date = "11.07.2026"
    end_date = "10.10.2026"
    now_ts = pd.Timestamp.now()
    
    for p in csv_paths:
        if os.path.exists(p):
            try:
                df_t = pd.read_csv(p)
                col = "date" if "date" in df_t.columns else ("tarih" if "tarih" in df_t.columns else None)
                if col:
                    d_min = pd.to_datetime(df_t[col]).min()
                    d_max = pd.to_datetime(df_t[col]).max()
                    # Bitiş tarihi bugünden ileri bir gelecek tarih olamaz
                    if d_max > now_ts:
                        d_max = min(d_max, now_ts)
                    start_date = d_min.strftime("%d.%m.%Y")
                    end_date = d_max.strftime("%d.%m.%Y")
                    break
            except Exception:
                pass
                
    return {
        "start_date": start_date,
        "end_date": end_date,
        "date_range_str": f"{start_date} – {end_date}",
        "period_label_str": "Yıllık Konsolidasyon (Son 12 Ay)",
        "reference_year": "2026",
        "sources": {
            "istasyon": "T.C. Çevre, Şehircilik ve İklim Değişikliği Bakanlığı (ÇŞİDB) & Kara Rapor 2025",
            "model": "Copernicus CAMS Atmosferik Yeniden Analiz Modeli",
            "saglik": "TÜİK Ölüm Nedeni İstatistikleri (2022-2024)",
            "sanayi": "OSB verileri: OSBÜK (indirme tarihi: GG.AA.2026)"
        }
    }

