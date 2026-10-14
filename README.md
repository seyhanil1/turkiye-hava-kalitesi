# 🍃 HavaAtlası — Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.65.0-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-7.1.0-3F4F75.svg)](https://plotly.com/)
[![Tests](https://img.shields.io/badge/Tests-19%20Passed-success.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **"Havanın hikâyesini veriler anlatır."**  
> HavaAtlası; Türkiye'nin 81 iline ait hava kirliliği ölçümlerini (PM2.5), sanayi parsel yoğunluklarını, TÜİK resmi ölüm istatistiklerini ve Dünya Sağlık Örgütü (WHO) kılavuz sınırlarını bir araya getiren, ileri düzey istatistiksel hipotez testleriyle desteklenmiş analitik bir karar destek platformudur.

---

## 1. Proje Özeti

HavaAtlası, yalnızca görsel bir dashboard olmanın ötesinde; Python istatistik motoru (`scipy`, `statsmodels`) ile donatılmış, bilimsel hipotez testleri çalıştıran (t-Testi, Mann-Whitney U, Tek Yönlü ANOVA, Kruskal-Wallis, Levene, Shapiro-Wilk) ve nedensellik ayrımını gözeten tam teşekküllü bir veri bilimi platformudur.

Koyu lacivert ve camgöbeği/neon yeşil tasarım diliyle geliştirilen arayüz; Türkiye'nin 81 ilini kapsayan gerçek GeoJSON haritası, 7/30/90 günlük zaman serisi projeksiyonları, şehir düelloları ve sektörel analizler sunar.

---

## 2. Özellikler

HavaAtlası modüler bir analitik mimariden oluşmaktadır:

1. **🏠 Genel Bakış (Overview):**
   - 4 Özet Metrik Kartı (Ortalama PM2.5, En Yüksek İl, En Düşük İl, 81/81 İl Kapsamı).
   - Gerçek 81 il sınırlarını içeren interaktif GeoJSON Koroplet Haritası.
   - En kirli ve en temiz iller sıralama çubuğu.
   - Son 7, 30 ve 90 günlük dinamik zaman serisi çizgisi ve 7 günlük hareketli ortalama (MA7) bandı.
   - Dinamik Veri Bilimi Yorum Paneli ve Hızlı Modül Erişim Kartları.
2. **🏙️ Şehir Karnesi (City Report Card):**
   - 81 il için detaylı hava kalitesi, DSÖ risk sınıfı (Düşük, Orta, Yüksek, Kritik) ve aşım katsayısı.
   - TÜİK resmi solunum yolu vefat sayıları ve 100.000 kişi başına oranları.
   - OSB verileri: OSBÜK (Ekim 2026) parsel ve hektar alanı dökümü.
   - Bölge ve Türkiye ortalamasıyla karşılaştırma grafiği.
3. **⚔️ Şehir Düellosu (City Duel & Hypothesis Testing):**
   - Kullanıcının seçtiği iki ili kafa kafaya çevre radarı ve sütun grafikleriyle karşılaştırma.
   - **Otomatik Hipotez Testi Motoru:** İki ilin zaman serisi dağılımlarında normallik (Shapiro-Wilk) ve varyans eşitliği (Levene) kontrolü yapılarak otomatik t-Testi veya Mann-Whitney U testi yürütülmesi, $p$-değeri ve Cohen's $d$ etki büyüklüğü ile Türkçe karar metni üretimi.
4. **🧮 Korelasyon & OLS Regresyon:**
   - Değişkenler arası Pearson ve Spearman korelasyon matrisi ısı haritaları.
   - Dağılım grafiği (Scatter Plot) üzerinde OLS regresyon doğrusu, eğim, $R^2$ ve standart hata analizi.
   - Korelasyon ve nedensellik ayrımına dair açık metodolojik uyarılar.
5. **🗺️ Bölgeler (Regional Breakdown & ANOVA):**
   - 7 coğrafi bölgenin kirlilik, sanayi ve solunum sağlığı özet tablosu.
   - Bölgesel Box-Plot (Kutu grafiği) varyans dağılımı.
   - Bölgeler arası Tek Yönlü ANOVA ($F$) ve Kruskal-Wallis ($H$) varyans analizi testi.
6. **📊 İl Grupları (City Groups):**
   - 81 il için çeyreklik (Q1/Q3) eşiklerine göre OSB ve PM2,5 grup sınıflandırması.
   - Kategori A (Düşük OSB, yüksek PM2,5), Kategori B (Yüksek OSB, yüksek PM2,5) ve Normal profil dağılımları.
7. **🏭 Sanayi Profili (Industrial Profile):**
   - OSB dizini analizi: OSBÜK (Ekim 2026) (toplam OSB, hektar ve dağılım).
   - İllerin sanayi kümelenmesi ve bölgesel partikül madde göstergeleri.

---

## 3. Ekran Görüntüsü ve Tasarım Referansı

Uygulama, profesyonel veri analitiği estetiğine sadık kalarak tasarlanmıştır:
- Koyu lacivert ve siyah arka plan (`#070c18`, `#0b1120`).
- Turkuaz (`#06b6d4`), elektrik mavisi (`#38bdf8`) ve neon yeşil (`#10b981`) vurgular.
- İnce kenarlıklı ve hafif parlayan kartlar.
- Tamamen şeffaf arka planlı, ince ızgaralı Plotly karanlık grafikleri.

---

## 4. Kullanılan Teknolojiler

- **Arayüz & Dashboard:** [Streamlit](https://streamlit.io/) (1.65.0)
- **Veri Görselleştirme:** [Plotly](https://plotly.com/) (7.1.0)
- **Veri Manipülasyonu:** [Pandas](https://pandas.pydata.org/) (3.0.6), [NumPy](https://numpy.org/)
- **İstatistik & Hipotez Testleri:** [SciPy](https://scipy.org/) (1.18.1), [Statsmodels](https://www.statsmodels.org/) (0.15.0)
- **Veri Kaynakları & Entegrasyon:** `requests`, `openpyxl`, `xlrd`
- **Birim Testleri:** [Pytest](https://pytest.org/) (9.1.1)

---

## 5. Veri Kaynakları ve Lisansları

| Kaynak | Veri Kapsamı | Yöntem / Dosya | Lisans / Kullanım |
| :--- | :--- | :--- | :--- |
| **Temiz Hava Hakkı Platformu** | 81 İl Yıllık PM2.5 Kirlilik Düzeyi | `data/hava_kirliligi.xlsx` (Kara Rapor 2025) | Açık kamuoyu çevre raporu |
| **TÜİK (TurkStat)** | İl Bazlı Ölüm ve Ölüm Nedenleri (2022-2025) | `data/tuik_saglik.xlsx` (Ölüm İstatistikleri) | Resmi İstatistik Programı (TÜİK Açık Veri) |
| **OSBÜK** | 81 İl OSB Dizini, Parsel ve Hektar Verisi | `data/sanayi.txt` | OSB verileri: OSBÜK (Ekim 2026) |
| **TÜİK ADNKS** | 81 İl Resmi Nüfus Sayımları | `data_sources/constants.py` | Resmi Nüfus İstatistikleri |
| **Copernicus CAMS & Open-Meteo** | Saatlik / Günlük PM2.5 Zaman Serisi | `air-quality-api.open-meteo.com` | CC-BY 4.0 (Copernicus Atmosphere Service) |
| **OpenAQ v3 API** | Küresel Hava Kalitesi İstasyon Verileri | `data_sources/openaq_connector.py` | OpenAQ Açık Veri Lisansı |
| **Dünya Sağlık Örgütü (WHO)** | Küresel Hava Kalitesi Kılavuz Limitleri (2021) | `data_sources/constants.py` | DSÖ Halk Sağlığı Kılavuzları |
| **Türkiye İl Sınırları GeoJSON** | 81 İl Coğrafi Vektör Sınırları | `data/tr-cities.json` | Açık Kaynak Coğrafi Veri |

---

## 6. Kurulum

### Gereksinimler
- Python 3.10 veya üzeri
- Windows, macOS veya Linux

### Adım Adım Kurulum

```bash
# 1. Depoyu klonlayın
git clone https://github.com/kullanici/havaatlasi.git
cd havaatlasi

# 2. Sanal ortam (venv) oluşturun ve etkinleştirin
python -m venv venv

# Windows için:
.\venv\Scripts\activate

# macOS / Linux için:
source venv/bin/activate

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt
```

### Çevre Değişkenleri (.env)
İsteğe bağlı olarak OpenAQ API anahtarı eklemek için:
```bash
copy .env.example .env
```
`.env` dosyası içerisine `OPENAQ_API_KEY=anahtariniz` değerini yazabilirsiniz. (Belirtilmediğinde sistem otomatik olarak doğrulanmış Kara Rapor ve Copernicus CAMS reanaliz verilerini kullanır).

---

## 7. Çalıştırma

Platformu yerel ortamda çalıştırmak için:

```bash
# Streamlit uygulamasını başlatın
streamlit run app/app.py
```
veya kök dizin üzerinden:
```bash
streamlit run app.py
```

Tarayıcınızda otomatik olarak açılacaktır:  
🌐 **`http://localhost:8501`**

### Testleri Çalıştırma

Tüm test paketini çalıştırmak ve doğrulamak için:

```bash
pytest tests/ -v
```

---

## 8. İstatistiksel Yöntemler ve Matematiksel Modeller

HavaAtlası'nda kullanılan istatistiksel modeller doğrudan Python tarafında hesaplanır:

1. **Normallik ve Varyans Homojenliği:**
   - Shapiro-Wilk Testi: $W = \frac{(\sum a_i x_{(i)})^2}{\sum (x_i - \bar{x})^2}$
   - Levene Testi: Varyans homojenliği ($p > 0.05$ ise varyanslar homojen kabul edilir).
2. **İki Grup Karşılaştırması (Düello):**
   - Normallik ve eşit varyans sağlanırsa: Student's t-Testi
   - Normallik sağlanıp eşit varyans yoksa: Welch's t-Testi ($t = \frac{\bar{x}_1 - \bar{x}_2}{\sqrt{s_1^2/n_1 + s_2^2/n_2}}$)
   - Normallik sağlanmazsa: Parametrik olmayan Mann-Whitney U Testi
   - Etki Büyüklüğü: Cohen's $d$ veya Rank-Biserial $r$.
3. **Çoklu Grup Varyans Analizi (Bölgeler):**
   - Tek Yönlü ANOVA ($F$-Testi) ve parametrik olmayan Kruskal-Wallis ($H$-Testi).
4. **Korelasyon ve Regresyon:**
   - Pearson ($r$) doğrusal korelasyonu ve Spearman ($\rho$) monotonik sıra korelasyonu.
   - En Küçük Kareler (OLS) Doğrusal Regresyonu ($y = \beta_0 + \beta_1 x + \epsilon$, $R^2$).

---

## 9. Proje Klasör Yapısı

```text
havakirliligi/
├── app/
│   ├── __init__.py
│   ├── app.py                     # Ana Streamlit uygulama giriş noktası
│   └── radar_intro.html           # Radar görselleştirme bileşeni
├── app_pages/
│   ├── __init__.py
│   ├── overview.py                # 1. Genel Bakış modülü
│   ├── report_card.py             # 2. Şehir Karnesi modülü
│   ├── duel.py                    # 3. Şehir Düellosu modülü
│   ├── correlation_page.py        # 4. Korelasyon ve Regresyon modülü
│   ├── regions_page.py            # 5. Coğrafi Bölgeler ve ANOVA modülü
│   ├── ai_forecast_page.py        # 6. İl Grupları ve Çeyreklik Analizi
│   └── industry_page.py           # 7. Sanayi Profili ve OSB Analizi
├── data/
│   ├── daily_air_quality_90d.csv  # 90 günlük Copernicus CAMS zaman serisi
│   ├── hava_kirliligi.xlsx        # Kara Rapor 2025 PM2.5 ölçümleri
│   ├── master_data.csv            # 81 il doğrulanmış analitik ana veri tablosu
│   ├── sanayi.txt                 # OSB verileri: OSBÜK (Ekim 2026)
│   ├── tr-cities.json             # 81 İl GeoJSON sınır haritası
│   └── tuik_saglik.xlsx           # TÜİK resmi ölüm istatistikleri (2022-2025)
├── data_sources/
│   ├── __init__.py
│   ├── constants.py               # İl kodları, bölgeler, koordinatlar ve nüfuslar
│   ├── local_official_data.py     # Kara Rapor, TÜİK ve OSB ayrıştırıcıları
│   ├── openmeteo_connector.py     # CAMS / Open-Meteo zaman serisi istemcisi
│   └── openaq_connector.py        # OpenAQ v3 API bağlayıcısı
├── data_processing/
│   ├── __init__.py
│   ├── cleaner.py                 # Aykırı değer, eksik veri ve Türkçe normalizasyon
│   └── aggregator.py              # Bölgesel ve DSÖ eşik agregasyonları
├── analytics/
│   ├── __init__.py
│   ├── descriptive.py             # Betimsel istatistik hesaplama motoru
│   ├── time_series.py             # Zaman serisi trend ve MA7 analizi
│   ├── correlation.py             # Pearson, Spearman ve OLS modelleri
│   ├── hypothesis_tests.py        # t-Testi, Mann-Whitney U, ANOVA, Kruskal-Wallis
│   └── interpreter.py             # Dinamik Veri Bilimi Yorum Motoru
├── visualization/
│   ├── __init__.py
│   ├── theme.py                   # Plotly karanlık teması ve renk skalaları
│   ├── map_charts.py              # 81 İl GeoJSON Choropleth haritası
│   ├── time_charts.py             # Zaman serisi ve hareketli ortalama grafikleri
│   ├── distribution_charts.py     # Boxplot, çubuk, ısı haritası ve radar grafikleri
│   └── components.py              # Özel lüks dark mode CSS ve HTML kartları
├── tests/
│   ├── __init__.py
│   ├── test_data_sources.py       # Veri kaynakları ve ayrıştırıcı testleri
│   ├── test_data_processing.py    # Temizleme ve agregasyon testleri
│   ├── test_analytics.py          # İstatistik motoru testleri
│   └── test_hypothesis_tests.py   # Hipotez testleri ve yorumlayıcı testleri
├── app.py                         # Kök dizin başlatıcısı
├── requirements.txt               # Bağımlılık listesi
├── .env.example                   # Ortam değişkenleri şablonu
├── .gitignore                     # Git yoksayma yapılandırması
├── LICENSE                        # MIT Açık Kaynak Lisansı
└── README.md                      # Kapsamlı Türkçe dokümantasyon
```

---

## 10. Veri Sınırlılıkları

1. **İstasyon Dağılımı ve Temsiliyet:** Bazı illerde ölçüm istasyonları trafik ve sanayi odaklıyken, bazı illerde kırsal arka plan istasyonları mevcuttur. Bu durum il geneli ortalamalarda varyans yaratabilir.
2. **Kış Enversiyonu:** Coğrafi çanak topoğrafyasına sahip illerde (örn. Iğdır, Düzce, Erzincan) kış aylarındaki sıcaklık enversiyonu kirliliği artırmaktadır; bu artış tek başına sanayi emisyonu kaynaklı değildir.
3. **Ölçüm Sıklığı:** Kara Rapor 2025 verileri yıllık ortalama PM2.5 konsantrasyonunu yansıtırken, zaman serisi grafikleri Copernicus CAMS reanaliz modellemesiyle desteklenmektedir.

---

## 11. Bilinen Sorunlar ve Geliştirme Planı

- [x] 81 il sınırlarını gösteren GeoJSON choropleth haritası entegrasyonu.
- [x] Tüm bileşenlerin tek bir master veri katmanına bağlanması.
- [x] İki grup ve çoklu grup için parametrik / non-parametrik hipotez testleri.
- [x] TÜİK resmi ölüm verileri ve OSB verilerinin (OSBÜK) tam ayrıştırılması.
- [ ] Çevre, Şehircilik ve İklim Değişikliği Bakanlığı Ulusal Hava Kalitesi İzleme Ağı (UHKİM) doğrudan web soketi desteği.
- [ ] Makine öğrenimi (SARIMA / Prophet / XGBoost) ile 7 günlük kirlilik tahmin modeli.

---

## 12. Lisans

Bu proje [MIT Lisansı](LICENSE) kapsamında açık kaynak olarak lisanslanmıştır. Kullanılan veri setleri ilgili kurum ve kuruluşların (TÜİK, OSBÜK, Temiz Hava Hakkı Platformu, Copernicus) açık veri politikalarına tabidir.
