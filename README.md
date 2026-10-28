# HavaAtlası — Türkiye Hava Kalitesi Platformu

[![Next.js](https://img.shields.io/badge/Next.js-16-000000.svg)](https://nextjs.org/)
[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Türkiye'nin 81 ili için ince partikül madde (PM2.5) değerlerini, Kara Rapor 2025 istasyon ölçümlerini, OSB envanterini
ve TÜİK ölüm istatistiklerini bir araya getiren, istatistiksel analizlerle desteklenmiş statik bir web sitesi.

> ⚠️ İl PM2.5 değerleri **istasyon ölçümü değil, Copernicus CAMS model tahminidir** ve yerel kirliliği düşük gösterebilir.
> Ayrıntılar: [`data/README.md`](data/README.md).

## Mimari

```text
Python (veri + istatistik)                       Next.js (statik site)
──────────────────────────                       ─────────────────────
data_sources/   CAMS, Kara Rapor, TÜİK, OSBÜK     web/src/app/        12 sayfa
analytics/      korelasyon, OLS, Moran, ANOVA ──► web/src/data/*.json web/src/components/ harita, grafikler
scripts/export_web_data.py ────────────────────►                      web/src/lib/assistant.ts  veri asistanı
tests/          veri ve hesaplama testleri
```

- Tüm hesaplamalar Python'da yapılır ve `scripts/export_web_data.py` ile `web/src/data/` altına JSON olarak yazılır.
  Site tarayıcıda istatistik hesaplamaz; sayılar test edilmiş Python koduyla birebir aynıdır.
- Site `next build` ile tamamen statik olarak üretilir (`output: "export"`); sunucu gerektirmez.
- `.github/workflows/data-refresh.yml` her gece CAMS günlük verisini yeniler, JSON'ları üretir, testleri çalıştırır ve
  değişiklik varsa commit'ler. Vercel bu commit ile siteyi yeniden yayınlar.

## Sayfalar

| Bölüm | Sayfalar |
| :--- | :--- |
| Keşfet | Genel Bakış (harita, sıralama, günlük seri), Şehir Karnesi, Düello |
| Analiz | Bölgeler (ANOVA), Korelasyon (OLS, Moran's I), Sanayi Profili, İl Grupları |
| Rehber | Eylem Rehberi, Terimler Sözlüğü, Veri Asistanı (kural tabanlı), Veri ve Yöntem, Sürüm Notları |

## Yerel geliştirme

```bash
# Python: veri ve testler
python -m venv venv
venv/Scripts/activate          # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python scripts/export_web_data.py            # JSON'ları üret
python scripts/export_web_data.py --refresh  # önce CAMS günlük verisini API'den yenile
python -m pytest tests -q

# Web sitesi
cd web
npm install
npm run dev     # http://localhost:3000
npm run build   # statik çıktı: web/out/
```

CAMS yıllık verisini yeniden çekmek için: `python -m data_sources.cams_annual_connector 2025`.

## Yayınlama (Vercel)

1. Vercel'de **Add New → Project** ile bu depoyu içe aktarın.
2. **Root Directory** olarak `web` seçin. Framework otomatik olarak Next.js algılanır; ek ayar gerekmez.
3. Özel alan adı için **Settings → Domains** bölümünden alan adını ekleyip Vercel'in verdiği DNS kaydını girin.

## Veri kaynakları

| Kaynak | Kapsam | Lisans |
| :--- | :--- | :--- |
| Copernicus CAMS / Open-Meteo | 81 il 2025 yıllık ve son 90 gün günlük PM2.5/PM10 | CC-BY 4.0 |
| Temiz Hava Hakkı Platformu, Kara Rapor 2025 | En yüksek 10 istasyonun 2024 PM2.5 ortalaması | Kamuya açık rapor |
| TÜİK | İl bazında ölüm nedenleri (2022–2025), ADNKS nüfus | TÜİK açık veri |
| OSBÜK | 81 il OSB envanteri (Ekim 2026) | Kamuya açık kayıt |
| DSÖ | 2021 Küresel Hava Kalitesi Kılavuzu | — |
| Türkiye il sınırları | GeoJSON (`data/tr-cities.json`) | Açık kaynak |

## Bilinen sınırlamalar

1. **Model tahmini:** CAMS (~10 km) konut ısınması, trafik ve kapalı havza kirliliğini düşük gösterir
   (ör. Iğdır: CAMS ~12, Kara Rapor istasyonu 46,8 µg/m³).
2. **Eksik istasyon verisi:** Kara Rapor 2025 il bazında tam PM2.5 tablosu yayımlamaz.
3. **Kaba ölüm hızları:** TÜİK il verisi yaş grubu içermediğinden yaşa göre standardizasyon yapılamaz.
4. **Ekolojik korelasyon:** İl düzeyindeki ilişkiler nüfus ve şehirleşmeyle karışır; nedensellik göstermez.

## Lisans

[MIT](LICENSE). Veri setleri ilgili kurumların (Copernicus, Temiz Hava Hakkı Platformu, TÜİK, OSBÜK) kullanım koşullarına tabidir.
