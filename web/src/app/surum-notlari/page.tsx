import type { Metadata } from "next";
import { PageHeader } from "@/components/ui";

export const metadata: Metadata = { title: "Sürüm Notları" };

const RELEASES: { version: string; date: string; title: string; current?: boolean; items: [string, string][] }[] = [
  {
    version: "v3.0.0", date: "28 Ekim 2026", current: true,
    title: "Yeni web sitesi (Next.js)",
    items: [
      ["Yeni altyapı", "Platform Streamlit'ten statik bir Next.js sitesine taşındı. Sayfalar daha hızlı açılır ve sunucu gerektirmez."],
      ["Aynı hesaplamalar", "Tüm istatistikler Python'da hesaplanıp JSON olarak aktarılır; sitedeki sayılar test edilmiş Python koduyla birebir aynıdır."],
      ["Günlük harita", "Genel Bakış haritasında yıllık ortalama ile son 90 günün günlük değerleri arasında geçiş yapılabilir."],
      ["Otomatik güncelleme", "Günlük CAMS verisi her gece otomatik olarak yenilenir."],
    ],
  },
  {
    version: "v2.3.0", date: "27 Ekim 2026",
    title: "Veri güvenilirliği düzeltmeleri",
    items: [
      ["Yeni PM2.5 kaynağı", "Kaynağı doğrulanamayan il değerleri kaldırıldı; ana gösterge CAMS 2025 yıllık ortalaması (12 ay, 81 il) oldu. Kara Rapor 2025 istasyon değerleri doğrulama katmanı olarak eklendi."],
      ["Kademeler", "Kirlilik kademeleri DSÖ 2021 yıllık ara hedeflerine (10/15/25/35 µg/m³) göre yeniden tanımlandı."],
      ["Sabit istatistikler", "Koda elle yazılmış korelasyon, güven aralığı ve Moran's I değerleri kaldırıldı; tümü veriden hesaplanıyor. Veriye dayanmayan 5 yıllık projeksiyon kaldırıldı."],
      ["Yeni göstergeler", "Solunum ölüm payı ve PM2.5'e atfedilebilir ölüm tahmini (AirQ+) eklendi."],
      ["Sentetik veri", "API hatasında sahte zaman serisi üreten yedek kaldırıldı; Türkiye serisi nüfus ağırlıklı ortalama oldu."],
    ],
  },
  {
    version: "v2.2.0", date: "13 Ekim 2026",
    title: "İl Grupları modülü ve terminoloji",
    items: [
      ["İl Grupları", "81 il OSB sayısı ve PM2.5'e göre çeyreklik (Q1/Q3) eşikleriyle gruplandı."],
      ["Navigasyon", "Menü 3 kategori (Keşfet, Analiz, Rehber) ve 12 sayfa olarak düzenlendi."],
      ["Terminoloji", "Değer yargısı ve kanıtlanmamış nedensellik içeren ifadeler nötr veri tanımlarıyla değiştirildi."],
    ],
  },
  {
    version: "v2.1.0", date: "11 Ekim 2026",
    title: "Arayüz sadeleştirme",
    items: [
      ["Gruplu menü", "Sol menü mantıksal gruplara ayrıldı."],
      ["Genel Bakış", "Kartlardaki anlamı belirsiz küçük grafikler kaldırıldı; \"81 il ortalaması\" düz aritmetik ortalama olarak netleştirildi."],
      ["Harita", "Doğu ve güney illerindeki kırpılma giderildi."],
    ],
  },
];

export default function ChangelogPage() {
  return (
    <>
      <PageHeader title="Sürüm Notları" subtitle="HavaAtlası'nda yapılan arayüz, veri doğruluğu ve altyapı güncellemeleri." />
      <ol className="flex flex-col gap-4">
        {RELEASES.map((r) => (
          <li key={r.version} className={`rounded-xl border bg-panel p-5 ${r.current ? "border-accent/50" : "border-line"}`}>
            <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
              <div className="flex flex-wrap items-center gap-2">
                <span className={`rounded-md px-2 py-0.5 text-xs font-bold ${r.current ? "bg-accent/15 text-accent" : "bg-white/5 text-muted"}`}>
                  {r.version}{r.current ? " (güncel)" : ""}
                </span>
                <h2 className="text-base font-bold text-white">{r.title}</h2>
              </div>
              <span className="text-xs text-muted">{r.date}</span>
            </div>
            <ul className="list-disc space-y-1.5 pl-5 text-[13.5px] leading-relaxed text-ink-soft">
              {r.items.map(([k, v]) => <li key={k}><strong className="text-white">{k}:</strong> {v}</li>)}
            </ul>
          </li>
        ))}
      </ol>
    </>
  );
}
