# Veri Dosyaları ve Kaynakları

Bu klasördeki her dosyanın nereden geldiği, nasıl üretildiği ve nasıl güncelleneceği.
Platformdaki PM2.5 değerlerinin **istasyon ölçümü değil, CAMS model tahmini** olduğunu unutmayın.

| Dosya | İçerik | Kaynak | Nasıl üretilir / güncellenir |
| :--- | :--- | :--- | :--- |
| `cams_annual_2025.csv` | 81 il merkezi için 2025 yıllık ortalama PM2.5 ve PM10 (µg/m³), saatlik veri tamlığı | [Copernicus CAMS](https://atmosphere.copernicus.eu/) üzerinden [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api) (CC-BY 4.0) | `python -m data_sources.cams_annual_connector 2025` |
| `daily_city_air_quality.csv` | 81 il merkezi için son ~90 günün günlük PM2.5 ortalaması (en az 18 saat dolu günler) | CAMS / Open-Meteo | `python -m data_sources.cams_city_connector` (uygulama içinden de yenilenir) |
| `kara_rapor_2025_istasyon.csv` | 2024 yılı en yüksek 10 istasyonun yıllık PM2.5 ortalaması | Temiz Hava Hakkı Platformu, [Kara Rapor 2025](https://temizhavahakki.org/kara-rapor-2025/) — D. Gümüşel sunumu, "Yıllık PM2,5 ortalamaları" (s. 12) | Elle aktarıldı; rapor yalnızca ilk 10 istasyonu yayımlıyor |
| `tuik_saglik.xlsx` | İl bazında 2022–2025 toplam, dolaşım, tümör ve solunum sistemi ölümleri | TÜİK Ölüm ve Ölüm Nedeni İstatistikleri | TÜİK veri portalından indirilen tablo |
| `sanayi.txt` | 81 ilin OSB listesi (tür, durum, alan, parsel) | OSBÜK (Ekim 2026) | Sekme ayrımlı dışa aktarım |
| `tr-cities.json` | 81 il sınırları (GeoJSON) | Açık kaynak coğrafi veri | — |
| `master_data.csv` | Yukarıdakilerin birleşimi (uygulama önbelleği) | Türetilmiş | `python src/generate_data.py` |

Nüfus (TÜİK ADNKS 2023), il merkezi koordinatları ve DSÖ 2021 kılavuz değerleri `data_sources/constants.py` içindedir.

## Bilinen sınırlamalar

- **CAMS düşük tahmin eder.** ~10 km çözünürlüklü model, konut ısınması, trafik ve kapalı havza (inversiyon) kirliliğini
  yakalayamaz. Örnek: Iğdır için CAMS 2025 yıllık ortalaması ~12 µg/m³, Kara Rapor 2025'te Iğdır istasyonu 46,8 µg/m³.
  Mutlak değerleri alt sınır olarak yorumlayın.
- **İstasyon verisi eksik.** Kara Rapor 2025'e göre PM2.5 ölçüm altyapısı olan 189 istasyonun yalnızca 113'ünden yeterli veri
  alınabilmiştir ve rapor il bazında tam PM2.5 tablosu yayımlamamaktadır.
- **Ölüm hızları kabadır.** TÜİK il verisi yaş grubu ayrımı içermediğinden yaşa göre standardizasyon yapılamamaktadır.
  Karşılaştırmalarda `solunum_olum_payi` (solunum ölümlerinin tüm ölümlere oranı) ve `atfedilen_olum_tahmini` daha uygundur.
- **Atfedilebilir ölüm yaklaşık bir tahmindir.** AirQ+ yöntemi (RR = 1,08 / 10 µg/m³, karşı-olgu 5 µg/m³) tüm yaşlardaki
  ölümlere uygulanır; Kara Rapor 30+ yaş ve dış nedenler hariç ölümleri kullanır.

## Kaldırılan dosyalar

- `hava_kirliligi.xlsx`: "Kara Rapor 2025" olarak etiketlenmiş 81 il değeri. Raporun yayımlanmış bulgularıyla uyuşmadı
  (raporda istasyon bazında en yüksek PM2.5 46,81 µg/m³ iken dosyada Osmaniye 83,6; PM10 için 40 µg/m³ üstü 32 il
  bildirilirken dosyada 15 il). Kaynağı doğrulanamadığı için kaldırıldı.
- `turkey_81_provinces_data.csv`, `turkey_industrial_health_data.csv`: Kaynağı belirtilmemiş, birbiriyle ve ana tabloyla
  çelişen değerler içeren sentetik görünümlü tablolar.
- `daily_air_quality_90d.csv`: Tek bir koordinatın serisiydi ve API hatasında sentetik veriyle üzerine yazılabiliyordu.
