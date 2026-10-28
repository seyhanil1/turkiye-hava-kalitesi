"use client";

import CitySelect, { useCityParam } from "@/components/CitySelect";
import Plot from "@/components/Plot";
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

function MiniBar({ title, a, b, nameA, nameB, fmt }: {
  title: string; a: number; b: number; nameA: string; nameB: string; fmt: (v: number) => string;
}) {
  return (
    <Card title={title}>
      <Plot
        height={230}
        data={[{
          type: "bar", x: [nameA, nameB], y: [a, b], marker: { color: [A, B] },
          text: [fmt(a), fmt(b)], textposition: "outside", cliponaxis: false, hoverinfo: "skip",
        }]}
        layout={{ margin: { l: 35, r: 10, t: 25, b: 30 }, yaxis: { range: [0, Math.max(a, b) * 1.3 || 1] } }}
      />
    </Card>
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

  const cats = ["Solunum sağlığı (düşük ölüm hızı)", "Hava temizliği (düşük PM2.5)"];

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
            <Plot
              height={260}
              data={[
                ...cats.map((c, i) => ({
                  x: [i === 0 ? a.pct_solunum : a.pct_hava, i === 0 ? b.pct_solunum : b.pct_hava], y: [c, c],
                  mode: "lines" as const, line: { color: "#334155", width: 4 }, showlegend: false, hoverinfo: "skip" as const,
                })),
                {
                  x: [a.pct_solunum, a.pct_hava], y: cats, mode: "text+markers" as const, name: ilA,
                  marker: { size: 14, color: A }, text: [`${trNum(a.solunum_olum_100k, 1)} / yüz binde`, `${trNum(a.pm25, 1)} µg/m³`],
                  textposition: "top center" as const, textfont: { color: A, size: 11 },
                  hovertemplate: `${ilA}: %{x:.0f}. yüzdelik<extra></extra>`,
                },
                {
                  x: [b.pct_solunum, b.pct_hava], y: cats, mode: "text+markers" as const, name: ilB,
                  marker: { size: 14, color: B }, text: [`${trNum(b.solunum_olum_100k, 1)} / yüz binde`, `${trNum(b.pm25, 1)} µg/m³`],
                  textposition: "bottom center" as const, textfont: { color: B, size: 11 },
                  hovertemplate: `${ilB}: %{x:.0f}. yüzdelik<extra></extra>`,
                },
              ]}
              layout={{
                margin: { l: 210, r: 20, t: 20, b: 40 },
                xaxis: { range: [0, 105], title: { text: "Yüzdelik (0–100)", font: { size: 11, color: "#8faec9" } } },
                legend: { orientation: "h", y: 1.15, x: 0 },
              }}
            />
          </Card>

          <div className="mb-5 grid gap-4 md:grid-cols-3">
            <MiniBar title="PM2.5 (µg/m³)" a={a.pm25} b={b.pm25} nameA={ilA} nameB={ilB} fmt={(v) => trNum(v, 1)} />
            <MiniBar title="Solunum ölüm hızı (yüz binde)" a={a.solunum_olum_100k} b={b.solunum_olum_100k} nameA={ilA} nameB={ilB} fmt={(v) => trNum(v, 1)} />
            <MiniBar title="Toplam OSB" a={a.toplam_osb} b={b.toplam_osb} nameA={ilA} nameB={ilB} fmt={(v) => `${v} adet`} />
          </div>

          <Note>
            PM2.5 değerleri CAMS model tahminidir. Solunum ölüm hızı kaba hızdır, yaşa göre standardize edilmemiştir. OSB verisi OSBÜK
            (Ekim 2026) kayıtlarındandır. İl düzeyindeki karşılaştırmalar bireysel risk veya tekil tesisler için nedensellik göstermez.
          </Note>
        </>
      )}
    </>
  );
}
