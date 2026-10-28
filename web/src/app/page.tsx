import Link from "next/link";
import TurkeyMap from "@/components/TurkeyMap";
import RankingTable from "@/components/RankingTable";
import { DailySeriesChart, RegionBenchmarkChart } from "@/components/charts";
import { Card, Note, PageHeader, Stat } from "@/components/ui";
import { byName, meta, national, provinces, tiers } from "@/lib/data";
import { trNum } from "@/lib/format";

export default function OverviewPage() {
  const whoCompliant = provinces.filter((p) => p.pm25 <= 5).length;
  const tierCounts = tiers.map((t) => ({
    tier: t,
    count: provinces.filter((p) => p.pm25 > (t.min_val === 0 ? -1 : t.min_val) && p.pm25 <= t.max_val).length,
  }));
  const totalAttributed = provinces.reduce((a, p) => a + p.atfedilen_olum_tahmini, 0);

  return (
    <>
      <PageHeader
        title="Havanın Hikâyesini Veriler Anlatıyor"
        subtitle={`Türkiye'nin 81 ili için ince partikül madde (PM2.5) göstergeleri · Yıllık değerler: Copernicus CAMS ${meta.cams_year}`}
      />

      <div className="mb-5 grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Stat
          label="81 ilin düz ortalaması"
          value={<>{trNum(national.mean, 1)} <span className="text-sm font-semibold text-muted">µg/m³</span></>}
          sub={`DSÖ kılavuzunun ${trNum(national.mean / 5, 1)} katı`}
          title="81 ilin aritmetik ortalaması; nüfus ağırlıklı değildir"
        />
        <Stat
          label="En yüksek il"
          value={<>{trNum(national.max.pm25, 1)} <span className="text-sm font-semibold text-muted">µg/m³</span></>}
          sub={<Link href={`/sehir-karnesi/?il=${encodeURIComponent(national.max.il)}`} className="hover:text-accent">{national.max.il}</Link>}
          accent="text-red-400"
        />
        <Stat
          label="En düşük il"
          value={<>{trNum(national.min.pm25, 1)} <span className="text-sm font-semibold text-muted">µg/m³</span></>}
          sub={<Link href={`/sehir-karnesi/?il=${encodeURIComponent(national.min.il)}`} className="hover:text-accent">{national.min.il}</Link>}
          accent="text-emerald-400"
        />
        <Stat
          label="DSÖ kılavuzunu karşılayan"
          value={`${whoCompliant} / ${provinces.length} il`}
          sub="Yıllık kılavuz değeri 5 µg/m³"
          accent="text-amber-300"
        />
      </div>

      <div className="mb-5 grid gap-5 xl:grid-cols-[1.7fr_1fr]">
        <Card title="Türkiye Hava Kalitesi Haritası (PM2.5)" subtitle="Bir ile tıklayarak karnesini açın.">
          <TurkeyMap />
        </Card>
        <Card title="Şehir Sıralaması" subtitle="Yıllık ortalama PM2.5 (CAMS 2025)">
          <RankingTable />
        </Card>
      </div>

      <div className="mb-5 grid gap-5 xl:grid-cols-2">
        <Card title="Seviyelere göre il sayısı" subtitle={meta.tiers.kaynak_aciklamasi}>
          <div className="mb-3 flex h-4 w-full overflow-hidden rounded-full bg-panel-2">
            {tierCounts.map(({ tier, count }) => (
              <div
                key={tier.id}
                style={{ width: `${(count / provinces.length) * 100}%`, background: tier.renk }}
                title={`${tier.etiket}: ${count} il`}
              />
            ))}
          </div>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-5">
            {tierCounts.map(({ tier, count }) => (
              <div key={tier.id} className="rounded-md border-l-4 bg-panel-2 px-2.5 py-2" style={{ borderColor: tier.renk }}>
                <div className="text-[11px] font-bold" style={{ color: tier.renk }}>{tier.etiket}</div>
                <div className="text-lg font-extrabold text-white">{count} <span className="text-xs font-normal text-muted">il</span></div>
                <div className="text-[10px] text-muted">{tier.tam_ad.match(/\(([^·)]+)/)?.[1]?.trim()}</div>
              </div>
            ))}
          </div>
          <div className="mt-4 rounded-md bg-panel-2 px-3 py-2 text-[12.5px] text-ink-soft">
            PM2.5&apos;e atfedilebilir ölüm tahmini (AirQ+, RR 1,08): yılda yaklaşık{" "}
            <strong className="text-white">{trNum(totalAttributed, 0)}</strong>. CAMS istasyon ölçümlerinden düşük
            tahmin ettiği için bu değer Kara Rapor 2025&apos;in istasyon tabanlı tahmininden (62.644) düşüktür.
          </div>
        </Card>
        <Card title="Türkiye geneli günlük PM2.5" subtitle="81 il merkezinin nüfus ağırlıklı CAMS günlük ortalaması">
          <DailySeriesChart />
        </Card>
      </div>

      <Card title="7 coğrafi bölge karşılaştırması" subtitle="Bölgedeki illerin yıllık ortalama PM2.5 değerlerinin ortalaması" className="mb-5">
        <RegionBenchmarkChart />
      </Card>

      <Card title="Model ile istasyon ölçümleri" subtitle="Kara Rapor 2025'te yayımlanan en yüksek 10 istasyonun 2024 yıllık PM2.5 ortalaması ve CAMS 2025 il değeri">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[520px] text-sm">
            <thead className="text-left text-[11px] uppercase tracking-wide text-muted">
              <tr>
                <th className="py-1.5 pr-3 font-semibold">İstasyon</th>
                <th className="py-1.5 pr-3 text-right font-semibold">İstasyon (2024)</th>
                <th className="py-1.5 pr-3 text-right font-semibold">CAMS il (2025)</th>
                <th className="py-1.5 text-right font-semibold">Oran</th>
              </tr>
            </thead>
            <tbody>
              {meta.stations.map((s) => {
                const cams = byName[s.il].pm25;
                return (
                  <tr key={s.istasyon} className="border-t border-line-soft">
                    <td className="py-1.5 pr-3 text-white">{s.istasyon}</td>
                    <td className="py-1.5 pr-3 text-right font-bold text-amber-300">{trNum(s.pm25_istasyon_2024, 1)}</td>
                    <td className="py-1.5 pr-3 text-right text-ink-soft">{trNum(cams, 1)}</td>
                    <td className="py-1.5 text-right text-muted">{trNum(s.pm25_istasyon_2024 / cams, 1)}x</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <div className="mt-3">
          <Note tone="warn">
            CAMS modeli il merkezindeki ~10 km&apos;lik bir alanın ortalamasını verir; trafik, konut ısınması ve kapalı havzalardaki
            yerel kirliliği yakalayamaz. Bu yüzden model değerleri alt sınır olarak, il sıralamaları ise yaklaşık olarak yorumlanmalıdır.
          </Note>
        </div>
      </Card>
    </>
  );
}
