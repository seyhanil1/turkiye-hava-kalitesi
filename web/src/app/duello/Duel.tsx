"use client";

import CitySelect, { useCityParam } from "@/components/CitySelect";
import { Card, Note } from "@/components/ui";
import { byName, type Province } from "@/lib/data";
import { roundDisp, trNum } from "@/lib/format";

const A = "#38bdf8";
const B = "#10b981";

/** İki değerin mutlak ve göreli farkı; "kazandı/kaybetti" dili kullanılmaz. */
function DiffChip({ a, b, unit, nameA, nameB, decimals = 1 }: {
  a: number; b: number; unit: string; nameA: string; nameB: string; decimals?: number;
}) {
  const va = roundDisp(a, decimals);
  const vb = roundDisp(b, decimals);
  const diff = roundDisp(va - vb, decimals);
  const denom = Math.max(va, vb);
  const rel = denom > 0 ? (Math.abs(diff) / denom) * 100 : 0;
  if (rel < 5) {
    return <span className="rounded-md bg-slate-800 px-2 py-0.5 text-xs font-semibold text-slate-400">≈ Benzer (%{trNum(rel, 1)})</span>;
  }
  const color = diff > 0 ? A : B;
  const name = diff > 0 ? nameA : nameB;
  return (
    <span className="rounded-md border px-2 py-0.5 text-xs font-semibold" style={{ color, borderColor: `${color}4d`, background: `${color}1f` }}>
      ▲ {name} +{trNum(Math.abs(diff), decimals)} {unit} (+%{trNum(rel, 1)})
    </span>
  );
}

function CityHeader({ p, color }: { p: Province; color: string }) {
  return (
    <div className="rounded-xl border p-4" style={{ borderColor: color, background: `linear-gradient(180deg, ${color}1a, transparent)` }}>
      <div className="flex items-center justify-between">
        <div className="text-xl font-extrabold" style={{ color }}>{p.il}</div>
        <span className="rounded-full border px-2.5 py-0.5 text-xs font-bold" style={{ color, borderColor: color }}>
          Plaka {String(p.plaka).padStart(2, "0")}
        </span>
      </div>
      <div className="mt-1 text-sm text-ink-soft">
        Bölge: <strong className="text-white">{p.bolge}</strong> · Nüfus: <strong className="text-white">{trNum(p.nufus, 0)}</strong>
      </div>
    </div>
  );
}

/** İki ilin aynı göstergedeki değerleri; çubuk uzunluğu ikisinden büyük olana göre ölçeklenir. */
function CompareBars({ title, a, b, nameA, nameB, fmt }: {
  title: string; a: number; b: number; nameA: string; nameB: string; fmt: (v: number) => string;
}) {
  const max = Math.max(a, b) || 1;
  return (
    <div>
      <div className="mb-2 text-sm font-semibold text-ink">{title}</div>
      {([[nameA, a, A], [nameB, b, B]] as const).map(([name, v, color]) => (
        <div key={name} className="mb-1.5 grid grid-cols-[7rem_1fr_auto] items-center gap-3 text-sm">
          <span className="truncate text-ink-soft">{name}</span>
          <div className="h-2.5 rounded-full bg-panel-2">
            <div className="h-2.5 rounded-full" style={{ width: `${(v / max) * 100}%`, background: color }} />
          </div>
          <span className="font-semibold tabular-nums" style={{ color }}>{fmt(v)}</span>
        </div>
      ))}
    </div>
  );
}

/** 0–100 yüzdelik şeridinde iki ilin konumu (yüksek = daha olumlu). */
function PercentileRow({ label, pa, pb, va, vb, nameA, nameB }: {
  label: string; pa: number; pb: number; va: string; vb: string; nameA: string; nameB: string;
}) {
  const lo = Math.min(pa, pb);
  const hi = Math.max(pa, pb);
  return (
    <div className="mb-6 last:mb-0">
      <div className="mb-2 flex flex-wrap items-baseline justify-between gap-x-4 text-sm">
        <span className="font-semibold text-ink">{label}</span>
        <span className="text-xs text-muted">
          <span style={{ color: A }}>{nameA}: {trNum(pa, 0)}. yüzdelik ({va})</span>
          {" · "}
          <span style={{ color: B }}>{nameB}: {trNum(pb, 0)}. yüzdelik ({vb})</span>
        </span>
      </div>
      <div className="relative h-3 rounded-full bg-panel-2">
        <div className="absolute top-1/2 h-1 -translate-y-1/2 rounded-full bg-slate-500/60" style={{ left: `${lo}%`, width: `${hi - lo}%` }} />
        {([[pa, A, nameA], [pb, B, nameB]] as const).map(([v, color, name]) => (
          <span
            key={name}
            title={`${name}: ${trNum(v, 0)}. yüzdelik`}
            className="absolute top-1/2 h-4 w-4 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-[#031322]"
            style={{ left: `${v}%`, background: color }}
          />
        ))}
      </div>
      <div className="mt-1 flex justify-between text-[10px] text-muted">
        <span>0 (en olumsuz)</span><span>50</span><span>100 (en olumlu)</span>
      </div>
    </div>
  );
}

export default function Duel() {
  const [ilA, setA] = useCityParam("a", "İstanbul");
  const [ilB, setB] = useCityParam("b", "Ankara");
  const a = byName[ilA];
  const b = byName[ilB];

  const osbM = (p: Province) => p.toplam_osb / (p.nufus / 1_000_000);
  const faal = (p: Province) => (p.toplam_osb > 0 ? (p.faal_osb / p.toplam_osb) * 100 : 0);

  const pmDiff = roundDisp(roundDisp(a.pm25) - roundDisp(b.pm25));
  const pmRel = Math.max(roundDisp(a.pm25), roundDisp(b.pm25)) > 0
    ? (Math.abs(pmDiff) / Math.max(roundDisp(a.pm25), roundDisp(b.pm25))) * 100 : 0;
  const solDiff = roundDisp(roundDisp(a.solunum_olum_100k) - roundDisp(b.solunum_olum_100k));
  const dir = (d: number) => (d < 0 ? "daha düşük" : d > 0 ? "daha yüksek" : "eşit");

  const rows: { label: string; va: string; vb: string; chip: React.ReactNode; who: string }[] = [
    {
      label: "PM2.5 (µg/m³, CAMS 2025)", va: `${trNum(a.pm25, 1)} µg/m³`, vb: `${trNum(b.pm25, 1)} µg/m³`,
      chip: <DiffChip a={a.pm25} b={b.pm25} unit="µg/m³" nameA={ilA} nameB={ilB} />,
      who: `${trNum(a.pm25 / 5, 1)}x vs ${trNum(b.pm25 / 5, 1)}x`,
    },
    {
      label: "TÜİK solunum ölüm hızı (yüz binde)", va: trNum(a.solunum_olum_100k, 1), vb: trNum(b.solunum_olum_100k, 1),
      chip: <DiffChip a={a.solunum_olum_100k} b={b.solunum_olum_100k} unit="yüz binde" nameA={ilA} nameB={ilB} />, who: "—",
    },
    {
      label: "Solunum ölümlerinin payı (%)", va: `%${trNum(a.solunum_olum_payi, 1)}`, vb: `%${trNum(b.solunum_olum_payi, 1)}`,
      chip: <DiffChip a={a.solunum_olum_payi} b={b.solunum_olum_payi} unit="puan" nameA={ilA} nameB={ilB} />, who: "—",
    },
    {
      label: "Toplam OSB sayısı", va: `${a.toplam_osb} adet`, vb: `${b.toplam_osb} adet`,
      chip: <DiffChip a={a.toplam_osb} b={b.toplam_osb} unit="adet" nameA={ilA} nameB={ilB} decimals={0} />, who: "—",
    },
    {
      label: "Milyon kişi başına OSB", va: trNum(osbM(a), 1), vb: trNum(osbM(b), 1),
      chip: <DiffChip a={osbM(a)} b={osbM(b)} unit="adet/milyon" nameA={ilA} nameB={ilB} />, who: "—",
    },
    {
      label: "Faal OSB oranı (%)", va: `%${trNum(faal(a), 1)}`, vb: `%${trNum(faal(b), 1)}`,
      chip: <DiffChip a={faal(a)} b={faal(b)} unit="puan" nameA={ilA} nameB={ilB} />, who: "—",
    },
  ];


  return (
    <>
      <div className="mb-4 grid gap-4 sm:grid-cols-2">
        <CitySelect id="duel-a" label="1. il (mavi)" value={ilA} onChange={setA} accent={A} />
        <CitySelect id="duel-b" label="2. il (yeşil)" value={ilB} onChange={setB} accent={B} />
      </div>

      {ilA === ilB ? (
        <Note tone="warn">Karşılaştırma için iki farklı il seçin.</Note>
      ) : (
        <>
          <div className="mb-5 grid gap-4 sm:grid-cols-2">
            <CityHeader p={a} color={A} />
            <CityHeader p={b} color={B} />
          </div>

          <Card title="Kafa kafaya gösterge tablosu" className="mb-4">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[640px] text-sm">
                <thead className="text-left text-[11px] uppercase tracking-wide text-muted">
                  <tr>
                    <th className="py-2 pr-3 font-semibold">Gösterge</th>
                    <th className="py-2 pr-3 font-semibold" style={{ color: A }}>{ilA}</th>
                    <th className="py-2 pr-3 font-semibold" style={{ color: B }}>{ilB}</th>
                    <th className="py-2 pr-3 font-semibold">Mutlak ve göreli fark</th>
                    <th className="py-2 font-semibold">DSÖ kılavuz katı</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((r) => (
                    <tr key={r.label} className="border-t border-line-soft">
                      <td className="py-2 pr-3 font-semibold text-ink">{r.label}</td>
                      <td className="py-2 pr-3 font-bold" style={{ color: A }}>{r.va}</td>
                      <td className="py-2 pr-3 font-bold" style={{ color: B }}>{r.vb}</td>
                      <td className="py-2 pr-3">{r.chip}</td>
                      <td className="py-2 text-muted">{r.who}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          <div className="mb-5">
            <Note>
              <strong>Özet:</strong> {ilA} ilinde yıllık ortalama PM2.5 {ilB} iline göre{" "}
              <strong>{trNum(Math.abs(pmDiff), 1)} µg/m³ {dir(pmDiff)}</strong> seviyededir (
              {pmRel < 5 ? "benzer düzeyde" : `%${trNum(pmRel, 1)} farkla`}). TÜİK solunum yolu ölüm hızında {ilA}, {ilB} iline
              kıyasla <strong>yüz binde {trNum(Math.abs(solDiff), 1)} {dir(solDiff)}</strong> düzeydedir.
            </Note>
          </div>

          <Card title="81 il içindeki yüzdelik konum" subtitle="0–100; yüksek değer daha olumlu (daha düşük PM2.5 veya ölüm hızı)" className="mb-5">
            <PercentileRow
              label="Hava temizliği (düşük PM2.5)" nameA={ilA} nameB={ilB}
              pa={a.pct_hava} pb={b.pct_hava} va={`${trNum(a.pm25, 1)} µg/m³`} vb={`${trNum(b.pm25, 1)} µg/m³`}
            />
            <PercentileRow
              label="Solunum sağlığı (düşük ölüm hızı)" nameA={ilA} nameB={ilB}
              pa={a.pct_solunum} pb={b.pct_solunum}
              va={`${trNum(a.solunum_olum_100k, 1)} / yüz bin`} vb={`${trNum(b.solunum_olum_100k, 1)} / yüz bin`}
            />
          </Card>

          <Card title="Temel göstergeler" className="mb-5">
            <div className="grid gap-6 md:grid-cols-3">
              <CompareBars title="PM2.5 (µg/m³)" a={a.pm25} b={b.pm25} nameA={ilA} nameB={ilB} fmt={(v) => trNum(v, 1)} />
              <CompareBars title="Solunum ölüm hızı (yüz binde)" a={a.solunum_olum_100k} b={b.solunum_olum_100k} nameA={ilA} nameB={ilB} fmt={(v) => trNum(v, 1)} />
              <CompareBars title="Toplam OSB" a={a.toplam_osb} b={b.toplam_osb} nameA={ilA} nameB={ilB} fmt={(v) => `${v} adet`} />
            </div>
          </Card>

          <Note>
            PM2.5 değerleri CAMS model tahminidir. Solunum ölüm hızı kaba hızdır, yaşa göre standardize edilmemiştir. OSB verisi OSBÜK
            (Ekim 2026) kayıtlarındandır. İl düzeyindeki karşılaştırmalar bireysel risk veya tekil tesisler için nedensellik göstermez.
          </Note>
        </>
      )}
    </>
  );
}
