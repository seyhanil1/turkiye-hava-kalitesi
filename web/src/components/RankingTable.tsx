"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { provinces, REGIONS, tierOf } from "@/lib/data";
import { trNum } from "@/lib/format";
import { TierBadge } from "./ui";

type Limit = "top" | "low" | "all";

export default function RankingTable() {
  const [limit, setLimit] = useState<Limit>("top");
  const [region, setRegion] = useState("Türkiye");

  const rows = useMemo(() => {
    const base = provinces.filter((p) => region === "Türkiye" || p.bolge === region);
    const sorted = [...base].sort((a, b) => (limit === "low" ? a.pm25 - b.pm25 : b.pm25 - a.pm25));
    return limit === "all" ? sorted : sorted.slice(0, 10);
  }, [limit, region]);

  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <div className="inline-flex rounded-lg border border-line bg-panel-2 p-0.5">
          {([["top", "İlk 10"], ["low", "En Düşük 10"], ["all", "Tümü"]] as [Limit, string][]).map(([k, label]) => (
            <button
              key={k}
              type="button"
              onClick={() => setLimit(k)}
              aria-pressed={limit === k}
              className={`rounded-md px-2.5 py-1 text-xs font-semibold ${limit === k ? "bg-accent/15 text-accent" : "text-muted hover:text-white"}`}
            >
              {label}
            </button>
          ))}
        </div>
        <label className="sr-only" htmlFor="rank-region">Bölge</label>
        <select
          id="rank-region"
          value={region}
          onChange={(e) => setRegion(e.target.value)}
          className="rounded-lg border border-line bg-panel-2 px-2 py-1 text-xs text-ink"
        >
          <option value="Türkiye">Türkiye Geneli</option>
          {REGIONS.map((r) => <option key={r} value={r}>{r}</option>)}
        </select>
      </div>
      <div className={`overflow-y-auto ${limit === "all" ? "max-h-[520px]" : ""}`}>
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-panel text-left text-[11px] uppercase tracking-wide text-muted">
            <tr>
              <th className="py-1.5 pr-2 font-semibold">#</th>
              <th className="py-1.5 pr-2 font-semibold">İl</th>
              <th className="py-1.5 pr-2 font-semibold">Kademe</th>
              <th className="py-1.5 text-right font-semibold">µg/m³</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((p, i) => {
              const t = tierOf(p.pm25);
              return (
                <tr key={p.il} className="border-t border-line-soft">
                  <td className="py-1.5 pr-2 text-muted">{i + 1}</td>
                  <td className="py-1.5 pr-2">
                    <Link href={`/sehir-karnesi/?il=${encodeURIComponent(p.il)}`} className="font-semibold text-white hover:text-accent">
                      {p.il}
                    </Link>{" "}
                    <span className="text-[11px] text-muted">({String(p.plaka).padStart(2, "0")})</span>
                  </td>
                  <td className="py-1.5 pr-2"><TierBadge tier={t} small /></td>
                  <td className="py-1.5 text-right font-bold" style={{ color: t.renk }}>{trNum(p.pm25, 1)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
