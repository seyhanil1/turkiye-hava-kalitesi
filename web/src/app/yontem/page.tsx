import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Card, PageHeader, TierBadge } from "@/components/ui";
import { meta, tiers } from "@/lib/data";
import { trNum } from "@/lib/format";

export const metadata: Metadata = { title: "Veri ve Yöntem" };

function Item({ title, children }: { title: string; children: ReactNode }) {
  return (
    <li>
      <strong className="text-white">{title}:</strong> {children}
    </li>
  );
}

export default function MethodologyPage() {
  return (
    <>
      <PageHeader
        title="Veri Kaynakları ve Hesaplama Yöntemi"
        subtitle="Platformun veri kaynakları, hesaplamaları, varsayımları ve bilinen sınırlamaları."
      />

      <Card title="1. Veri kaynakları (ölçüm ve model)" className="mb-5">
        <ul className="list-disc space-y-2.5 pl-5 text-sm leading-relaxed text-ink-soft">
          <Item title={`Yıllık PM2.5 (ana gösterge)`}>
            Her il için Copernicus CAMS atmosfer modelinin (Open-Meteo Air Quality API) il merkezi noktasındaki{" "}
            <strong>{meta.cams_year} yılı 8.760 saatlik değerlerinin ortalamasıdır</strong> (kış dahil 12 ay; veri tamlığı %75&apos;in
            altında kalan il değeri boş bırakılır). Aynı yöntemle yıllık PM10 da hesaplanır. Bu değerler istasyon ölçümü değil,
            yaklaşık 10 km çözünürlüklü <strong>model tahminidir</strong> ve yerel ısınma, trafik ve kapalı havza kirliliğini
            genellikle <strong>olduğundan düşük</strong> gösterir.
          </Item>
          <Item title="İstasyon karşılaştırması">
            Temiz Hava Hakkı Platformu Kara Rapor 2025, Çevre Bakanlığı istasyonlarının 2024 verisiyle yalnızca en yüksek 10
            istasyonun yıllık PM2.5 ortalamasını yayımlamıştır (en yüksek: Iğdır 46,8 µg/m³). Bu değerler doğrulama katmanı olarak
            gösterilir. Rapora göre PM2.5 ölçüm altyapısı olan 189 istasyonun yalnızca 113&apos;ünden yeterli veri alınabilmiştir.
          </Item>
          <Item title="Günlük seri">
            Son yaklaşık 90 gün için il merkezlerinin CAMS günlük ortalamaları (en az 18 saati dolu günler); şu an{" "}
            {meta.daily_start} – {meta.daily_end}. &quot;Türkiye geneli&quot; serisi 81 ilin nüfus ağırlıklı ortalamasıdır. Veri
            alınamazsa sentetik değer üretilmez.
          </Item>
          <Item title="Nüfus">TÜİK Adrese Dayalı Nüfus Kayıt Sistemi (ADNKS 2023).</Item>
          <Item title="Ölüm istatistikleri">
            TÜİK Ölüm ve Ölüm Nedeni İstatistikleri (2024). Solunum sistemi hastalıklarından ölümler kaba hızdır; yaşa göre
            standardize edilmemiştir.
          </Item>
          <Item title="Sanayi">OSBÜK (Ekim 2026) OSB envanteri: il bazında toplam ve faal OSB sayısı, alan ve parsel.</Item>
          <Item title="Kaldırılan veri">
            Önceki sürümlerde &quot;Kara Rapor 2025&quot; olarak etiketlenen il değerleri, raporun yayımlanmış PM2.5 ve PM10
            bulgularıyla uyuşmadığı ve kaynağı doğrulanamadığı için kaldırılmıştır.
          </Item>
        </ul>
      </Card>

      <Card title="2. Kirlilik kademeleri" subtitle={meta.tiers.kaynak_aciklamasi} className="mb-5">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[560px] text-sm">
            <thead className="text-left text-[11px] uppercase tracking-wide text-muted">
              <tr>
                <th className="py-2 pr-3 font-semibold">Kademe</th>
                <th className="py-2 pr-3 font-semibold">Yıllık PM2.5</th>
                <th className="py-2 font-semibold">Açıklama</th>
              </tr>
            </thead>
            <tbody>
              {tiers.map((t) => (
                <tr key={t.id} className="border-t border-line-soft">
                  <td className="py-2 pr-3"><TierBadge tier={t} /></td>
                  <td className="py-2 pr-3 font-semibold text-white">
                    {t.min_val === 0 ? `≤ ${t.max_val}` : t.max_val >= 900 ? `> ${t.min_val}` : `${trNum(t.min_val + 0.1, 1)} – ${t.max_val}`} µg/m³
                  </td>
                  <td className="py-2 text-ink-soft">{t.aciklama}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <Card title="3. İstatistiksel hesaplamalar" className="mb-5">
        <ul className="list-disc space-y-2.5 pl-5 text-sm leading-relaxed text-ink-soft">
          <Item title="81 il ortalaması">81 ilin PM2.5 değerlerinin ağırlıksız aritmetik ortalamasıdır; her il eşit ağırlıktadır.</Item>
          <Item title="Bölge ortalamaları">Bölgedeki illerin PM2.5 değerlerinin aritmetik ortalamasıdır.</Item>
          <Item title="Korelasyon">Pearson ve Spearman katsayıları, iki yönlü p değerleri ve Spearman için 1.000 tekrarlı bootstrap güven aralığı.</Item>
          <Item title="Çoklu regresyon (OLS)">PM2.5&apos;in OSB sayısı, ortalama rakım ve nüfus (100 bin kişi) ile doğrusal ilişkisi.</Item>
          <Item title="Mekânsal otokorelasyon">İl merkezleri arası ters mesafe ağırlık matrisiyle (satır standardize) Global Moran&apos;s I ve 999 permütasyonlu tek yönlü test.</Item>
          <Item title="Bölgeler arası fark">Tek yönlü ANOVA, Kruskal-Wallis ve Levene testleri. Testler farklı sonuç verirse bu açıkça belirtilir.</Item>
          <Item title="Atfedilebilir ölüm">
            Kara Rapor 2025 ile aynı AirQ+ log-doğrusal yaklaşımı: her 10 µg/m³ için göreli risk {trNum(meta.airq.rr_per_10, 2)}, karşı-olgu
            düzeyi {meta.airq.counterfactual} µg/m³; atfedilebilir pay = 1 − 1/RR^((PM2.5−5)/10). TÜİK il verisinde 30+ yaş ayrımı
            olmadığından tüm ölümler kullanılır (yukarı yönlü sapma); CAMS&apos;in düşük tahmin eğilimi ise aşağı yönlü sapma yaratır.
          </Item>
          <Item title="Solunum ölüm payı">Solunum ölümlerinin tüm ölümler içindeki yüzdesi; kaba hızın aksine illerin genel ölüm düzeyini ve yaş yapısını kısmen dengeler.</Item>
        </ul>
        <p className="mt-3 text-xs text-muted">
          Tüm hesaplamalar Python (pandas, SciPy, NumPy) ile yapılır ve sonuçlar siteye statik JSON olarak aktarılır; kaynak kod ve
          testler GitHub deposundadır.
        </p>
      </Card>

      <Card title="4. Bilinen sınırlamalar">
        <ul className="list-disc space-y-2.5 pl-5 text-sm leading-relaxed text-ink-soft">
          <Item title="Model sapması">
            CAMS (~10 km) bölgesel arka plan kirliliğini yakalar ama trafik, konut ısınması ve kapalı havzalardaki birikimi düşük
            tahmin eder. Örnek: Iğdır için CAMS yıllık ortalaması ~12 µg/m³ iken Kara Rapor 2025&apos;te Iğdır istasyonu 46,8 µg/m³.
            Mutlak değerleri alt sınır, il sıralamalarını yaklaşık olarak yorumlayın.
          </Item>
          <Item title="Yaş standardizasyonu">TÜİK il verisi yaş grubu içermediğinden ölüm hızları yaşa göre düzeltilemez.</Item>
          <Item title="Ekolojik yanılgı">İl düzeyindeki ilişkiler bireysel maruziyete veya tekil tesislere nedensellik olarak yansıtılamaz.</Item>
        </ul>
      </Card>
    </>
  );
}
