"use client";

import { useState } from "react";
import { normalizeTr } from "@/lib/format";

const TERMS: { term: string; cat: string; desc: string }[] = [
  { term: "PM2.5 (İnce Partikül Madde)", cat: "Kirletici", desc: "Çapı 2,5 mikrometre veya daha küçük ince partiküllerdir (saç telinin yaklaşık 30'da biri). Akciğer alveollerine ve kan dolaşımına ulaşabildiği için sağlık açısından en zararlı hava kirleticisi kabul edilir." },
  { term: "PM10 (Kaba Partikül Madde)", cat: "Kirletici", desc: "Çapı 10 mikrometre veya daha küçük partiküllerdir; PM2.5'i de kapsar. Doğal toz, yol tozu ve deniz tuzu gibi kaynakları da içerdiğinden insan kaynaklı kirliliği PM2.5 kadar iyi yansıtmaz. DSÖ yıllık kılavuz değeri 15 µg/m³'tür." },
  { term: "SO₂ (Kükürt Dioksit)", cat: "Gaz kirletici", desc: "Yüksek kükürtlü kömür ve fuel-oil yakılmasıyla oluşan, asit yağmurlarına yol açan boğucu bir gazdır." },
  { term: "O₃ (Yer Seviyesi Ozon)", cat: "İkincil kirletici", desc: "Doğrudan salınmaz; güneş ışığı altında azot oksitler (NOx) ve uçucu organik bileşiklerin tepkimesiyle oluşur. Akciğerleri tahriş eder." },
  { term: "CO (Karbon Monoksit)", cat: "Gaz kirletici", desc: "Yakıtların eksik yanmasıyla oluşan renksiz ve kokusuz zehirli bir gazdır; kanda oksijen taşınmasını engeller." },
  { term: "µg/m³ (Mikrogram / Metreküp)", cat: "Ölçü birimi", desc: "Bir metreküp havadaki kirletici kütlesini gösteren konsantrasyon birimidir. 1 mikrogram, gramın milyonda biridir." },
  { term: "DSÖ Kılavuz Değeri", cat: "Standart", desc: "Dünya Sağlık Örgütü'nün (2021) epidemiyolojik kanıtlara dayanarak önerdiği değerdir. PM2.5 için yıllık 5 µg/m³, 24 saatlik 15 µg/m³'tür. DSÖ'ye göre PM2.5 için risksiz bir alt sınır yoktur." },
  { term: "DSÖ Ara Hedefleri (IT-1 – IT-4)", cat: "Standart", desc: "Kılavuz değerine hemen ulaşamayan ülkeler için tanımlanan kademeli hedeflerdir. PM2.5 yıllık ara hedefleri: IT-1 35, IT-2 25, IT-3 15, IT-4 10 µg/m³." },
  { term: "24 saatlik ve yıllık ortalama", cat: "İstatistik", desc: "24 saatlik ortalama kısa süreli (akut) maruziyeti, yıllık ortalama ise uzun dönem (kronik) maruziyetin kalp ve akciğer sağlığına etkisini değerlendirmek için kullanılır. İkisi aynı eşiklerle karşılaştırılamaz." },
  { term: "Sıcaklık İnversiyonu (Terselme)", cat: "Meteoroloji", desc: "Soğuk hava kütlesinin yere yakın sıkışıp üzerindeki sıcak katmanın bir kapak gibi davranmasıdır. Kirleticilerin dikey dağılımını engeller; kış aylarında çanak biçimli havzalarda sık görülür." },
  { term: "CAMS (Copernicus Atmosphere Monitoring Service)", cat: "Veri kaynağı", desc: "AB Copernicus programı kapsamında ECMWF'nin işlettiği atmosfer modelleme sistemidir. Uydu gözlemleri ve kimyasal taşınım modellerini birleştirir. Bu sitedeki PM2.5 değerleri CAMS'in yaklaşık 10 km çözünürlüklü model tahminleridir, istasyon ölçümü değildir." },
  { term: "Kara Rapor", cat: "Veri kaynağı", desc: "Temiz Hava Hakkı Platformu'nun, Çevre Bakanlığı istasyon verilerini derleyerek her yıl yayımladığı hava kalitesi raporudur. Kara Rapor 2025, 2024 yılı ölçümlerini kapsar." },
  { term: "ÇŞİDB (Çevre, Şehircilik ve İklim Değişikliği Bakanlığı)", cat: "Kurum", desc: "Türkiye'de Ulusal Hava Kalitesi İzleme Ağı'nı işleten, ölçüm istasyonlarını kuran ve emisyon izinlerini düzenleyen kamu kurumudur." },
  { term: "OSB (Organize Sanayi Bölgesi) / OSBÜK", cat: "Sanayi", desc: "Sanayi tesislerinin planlı biçimde toplandığı bölgelerdir. OSBÜK, OSB'lerin üst kuruluşudur; bu sitedeki OSB verileri OSBÜK envanterinden (Ekim 2026) alınmıştır." },
  { term: "Kaba ölüm hızı", cat: "Epidemiyoloji", desc: "Belirli bir nedenden ölümlerin toplam nüfusa oranıdır (yüz binde). Yaşa göre düzeltilmediği için yaşlı nüfusu fazla bölgelerde yapısal olarak yüksek çıkar." },
  { term: "Atfedilebilir ölüm (AirQ+)", cat: "Epidemiyoloji", desc: "Kirliliğin kılavuz değerine (5 µg/m³) inmesi durumunda önlenebilecek tahmini ölüm sayısıdır. DSÖ'nün AirQ+ yöntemi, her 10 µg/m³ PM2.5 artışı için tüm doğal nedenli ölümlerde 1,08 göreli risk kullanır." },
  { term: "HavaAtlası Kirlilik Kademeleri", cat: "Sınıflandırma", desc: "Yıllık ortalama PM2.5 için 5 düzey: Düşük (≤10), Orta (10,1–15), Yüksek (15,1–25), Çok Yüksek (25,1–35), Kritik (>35 µg/m³). Eşikler DSÖ 2021 yıllık ara hedeflerinden alınmıştır; adlar bu platforma özgüdür ve DSÖ'nün resmi bir risk ölçeği değildir." },
];

export default function Glossary() {
  const [q, setQ] = useState("");
  const nq = normalizeTr(q);
  const list = nq ? TERMS.filter((t) => normalizeTr(`${t.term} ${t.cat} ${t.desc}`).includes(nq)) : TERMS;

  return (
    <div>
      <label htmlFor="glossary-search" className="sr-only">Sözlükte ara</label>
      <input
        id="glossary-search"
        type="search"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Terim ara: PM2.5, DSÖ, CAMS, inversiyon…"
        className="mb-4 w-full rounded-lg border border-line bg-panel-2 px-3 py-2 text-sm text-white placeholder:text-muted sm:w-96"
      />
      {list.length === 0 ? (
        <p className="text-sm text-muted">Aranan terim bulunamadı.</p>
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {list.map((t) => (
            <section key={t.term} className="rounded-xl border border-accent/20 bg-panel p-4">
              <div className="mb-2 flex items-start justify-between gap-3">
                <h2 className="text-[15px] font-bold text-white">{t.term}</h2>
                <span className="shrink-0 rounded-md border border-accent/30 bg-accent/10 px-2 py-0.5 text-[11px] font-bold text-accent">{t.cat}</span>
              </div>
              <p className="text-[13.5px] leading-relaxed text-ink-soft">{t.desc}</p>
            </section>
          ))}
        </div>
      )}
    </div>
  );
}
