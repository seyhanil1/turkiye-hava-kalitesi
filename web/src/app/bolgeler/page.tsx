import type { Metadata } from "next";
import { RegionBenchmarkChart, RegionStripChart } from "@/components/charts";
import { RegionOsbChart } from "./RegionOsbChart";
import { Card, Note, PageHeader, SourceNote } from "@/components/ui";
import { stats } from "@/lib/data";
import { trNum } from "@/lib/format";

export const metadata: Metadata = { title: "Bölgeler" };

function SigBadge({ significant }: { significant: boolean }) {
  return (
    <span
      className={`mt-1.5 inline-block rounded border px-2 py-0.5 text-[10px] font-semibold ${
        significant ? "border-emerald-400/30 bg-emerald-400/10 text-emerald-300" : "border-amber-300/30 bg-amber-300/10 text-amber-300"
      }`}
    >
      {significant ? "Fark anlamlı (p < 0,05)" : "Fark anlamsız (p > 0,05)"}
    </span>
  );
}

export default function RegionsPage() {
  const { rows, anova } = stats.regions;
  const means = rows.map((r) => r.ortalama);

  return (
    <>
      <PageHeader
        title="Bölgesel Hava Kalitesi"
        subtitle="Türkiye'nin 7 coğrafi bölgesinde PM2.5 dağılımı, sanayi ve sağlık göstergeleri ile bölgeler arası varyans analizi."
      />

      <Card title="7 coğrafi bölge karşılaştırması ve DSÖ aşımı" className="mb-5">
        <RegionBenchmarkChart />
        <SourceNote>
          Kesikli kırmızı çizgi DSÖ yıllık kılavuz değeridir (5 µg/m³). Bölge ortalamaları bu değerin{" "}
          {trNum(Math.min(...means) / 5, 1)} ila {trNum(Math.max(...means) / 5, 1)} katıdır. Değerler, CAMS 2025 yıllık il
          ortalamalarının bölge içindeki düz ortalamasıdır.
        </SourceNote>
      </Card>

      <Card title="Bölge özet tablosu" className="mb-5">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[720px] text-sm">
            <thead className="text-left text-[11px] uppercase tracking-wide text-muted">
              <tr>
                <th className="py-2 pr-3 font-semibold">Bölge</th>
                <th className="py-2 pr-3 text-right font-semibold">İl sayısı</th>
                <th className="py-2 pr-3 text-right font-semibold">Ort. PM2.5</th>
                <th className="py-2 pr-3 text-right font-semibold">Medyan</th>
                <th className="py-2 pr-3 text-right font-semibold">Std. sapma</th>
                <th className="py-2 pr-3 text-right font-semibold">Toplam OSB</th>
                <th className="py-2 text-right font-semibold">Solunum ölüm hızı (yüz binde)</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.bolge} className="border-t border-line-soft">
                  <td className="py-2 pr-3 font-semibold text-white">{r.bolge}</td>
                  <td className="py-2 pr-3 text-right">{r.il_sayisi}</td>
                  <td className="py-2 pr-3 text-right font-bold text-accent">{trNum(r.ortalama, 2)}</td>
                  <td className="py-2 pr-3 text-right">{trNum(r.medyan, 2)}</td>
                  <td className="py-2 pr-3 text-right">{trNum(r.std, 2)}</td>
                  <td className="py-2 pr-3 text-right">{r.toplam_osb}</td>
                  <td className="py-2 text-right">{trNum(r.solunum_100k, 1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <SourceNote>
          Bölgesel solunum ölüm hızları TÜİK kaba ölüm verisidir (yaş standardizasyonu içermez); yaşlı nüfusu fazla
          bölgelerde yapısal olarak yüksek çıkar.
        </SourceNote>
      </Card>

      <div className="mb-5 grid gap-5 lg:grid-cols-[1.2fr_1fr]">
        <Card title="İllerin bölgelere göre PM2.5 dağılımı">
          <RegionStripChart />
        </Card>
        <Card title="Bölgelere göre toplam OSB">
          <RegionOsbChart />
        </Card>
      </div>

      <Card title="Bölgeler arası varyans analizi (ANOVA ve Kruskal-Wallis)">
        <p className="text-sm font-bold text-accent">{anova.h0}</p>
        <p className="mb-4 mt-1 text-sm text-ink-soft">{anova.h1}</p>
        <div className="mb-4 grid gap-3 sm:grid-cols-3">
          <div className="rounded-lg border border-line-soft bg-panel-2 p-3">
            <div className="text-[11px] text-muted">Tek yönlü ANOVA</div>
            <div className="text-lg font-bold text-white">F = {trNum(anova.anova_f, 2)}</div>
            <div className="text-xs text-ink-soft">p = {trNum(anova.anova_p, 3)}</div>
            <SigBadge significant={anova.anova_significant} />
          </div>
          <div className="rounded-lg border border-line-soft bg-panel-2 p-3">
            <div className="text-[11px] text-muted">Kruskal-Wallis</div>
            <div className="text-lg font-bold text-white">H = {trNum(anova.kruskal_h, 2)}</div>
            <div className="text-xs text-ink-soft">p = {trNum(anova.kruskal_p, 3)}</div>
            <SigBadge significant={anova.kruskal_significant} />
          </div>
          <div className="rounded-lg border border-line-soft bg-panel-2 p-3">
            <div className="text-[11px] text-muted">Levene varyans homojenliği</div>
            <div className="text-lg font-bold text-white">p = {trNum(anova.levene_p, 3)}</div>
            <span className="mt-1.5 inline-block rounded border border-sky-400/30 bg-sky-400/10 px-2 py-0.5 text-[10px] font-semibold text-sky-300">
              {anova.equal_variance ? "Varyanslar eşit" : "Heterojen varyans"}
            </span>
          </div>
        </div>
        <Note>
          <strong>İstatistiksel değerlendirme:</strong> {anova.interpretation}
        </Note>
      </Card>
    </>
  );
}
