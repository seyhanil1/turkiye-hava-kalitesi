"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { provinces } from "@/lib/data";
import { trCompare, trNum } from "@/lib/format";

type SortKey = "il" | "bolge" | "toplam_osb" | "faal_osb" | "faal_oran" | "pm25";

const COLUMNS: { key: SortKey; label: string; numeric: boolean }[] = [
  { key: "il", label: "İl", numeric: false },
  { key: "bolge", label: "Bölge", numeric: false },
  { key: "toplam_osb", label: "Toplam OSB", numeric: true },
  { key: "faal_osb", label: "Faal OSB", numeric: true },
  { key: "faal_oran", label: "Faal oran", numeric: true },
  { key: "pm25", label: "PM2.5 (µg/m³)", numeric: true },
];

export default function IndustryTable() {
  const [sort, setSort] = useState<{ key: SortKey; desc: boolean }>({ key: "toplam_osb", desc: true });
  const rows = useMemo(() => {
    const withRate = provinces.map((p) => ({ ...p, faal_oran: p.toplam_osb > 0 ? (p.faal_osb / p.toplam_osb) * 100 : 0 }));
    return withRate.sort((a, b) => {
      const va = a[sort.key];
      const vb = b[sort.key];
      const cmp = typeof va === "string" ? trCompare(va, vb as string) : (va as number) - (vb as number);
      return sort.desc ? -cmp : cmp;
    });
  }, [sort]);

  return (
    <div className="max-h-[560px] overflow-auto">
      <table className="w-full min-w-[640px] text-sm">
        <thead className="sticky top-0 bg-panel text-left text-[11px] uppercase tracking-wide text-muted">
          <tr>
            {COLUMNS.map((c) => (
              <th key={c.key} className={`py-2 pr-3 font-semibold ${c.numeric ? "text-right" : ""}`}>
                <button
                  type="button"
                  onClick={() => setSort((s) => ({ key: c.key, desc: s.key === c.key ? !s.desc : c.numeric }))}
                  className="uppercase hover:text-white"
                >
                  {c.label}{sort.key === c.key ? (sort.desc ? " ↓" : " ↑") : ""}
                </button>
              </th>
            ))}
            <th className="py-2 font-semibold">Profil</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((p) => (
            <tr key={p.il} className="border-t border-line-soft">
              <td className="py-1.5 pr-3">
                <Link href={`/sehir-karnesi/?il=${encodeURIComponent(p.il)}`} className="font-semibold text-white hover:text-accent">{p.il}</Link>
              </td>
              <td className="py-1.5 pr-3 text-ink-soft">{p.bolge}</td>
              <td className="py-1.5 pr-3 text-right">{p.toplam_osb}</td>
              <td className="py-1.5 pr-3 text-right">{p.faal_osb}</td>
              <td className="py-1.5 pr-3 text-right">%{trNum(p.faal_oran, 1)}</td>
              <td className="py-1.5 pr-3 text-right font-semibold text-accent">{trNum(p.pm25, 1)}</td>
              <td className="py-1.5 text-xs text-muted">{p.sanayi_tipi}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
