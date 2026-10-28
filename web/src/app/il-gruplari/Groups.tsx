"use client";

import Link from "next/link";
import CitySelect, { useCityParam } from "@/components/CitySelect";
import { byName, CATEGORY_LABELS, type Kategori, provinces } from "@/lib/data";
import { trNum } from "@/lib/format";

export const CATEGORY_COLORS: Record<Kategori, string> = {
  A: "#f59e0b",
  B: "#ef4444",
  YK: "#f97316",
  N: "#00e5db",
};

function Chips({ kategori }: { kategori: Kategori }) {
  const list = provinces.filter((p) => p.kategori === kategori).sort((a, b) => b.pm25 - a.pm25);
  const color = CATEGORY_COLORS[kategori];
  if (!list.length) return <p className="text-sm text-muted">Bu grupta il yok.</p>;
  return (
    <div className="flex flex-wrap gap-1.5">
      {list.map((p) => (
        <Link
          key={p.il}
          href={`/sehir-karnesi/?il=${encodeURIComponent(p.il)}`}
          className="rounded-full border px-2.5 py-1 text-xs hover:brightness-125"
          style={{ color, borderColor: `${color}80`, background: `${color}14` }}
        >
          {p.il} (PM2.5: {trNum(p.pm25, 1)} µg/m³, OSB: {p.toplam_osb} adet)
        </Link>
      ))}
    </div>
  );
}

export { Chips };

export default function GroupSelector() {
  const [il, setIl] = useCityParam("il", "Iğdır");
  const p = byName[il];
  const color = CATEGORY_COLORS[p.kategori];
  return (
    <div className="flex flex-wrap items-end gap-4">
      <CitySelect id="groups-city" label="İl seçin" value={il} onChange={setIl} />
      <div className="flex flex-wrap items-center gap-3 pb-1">
        <span className="rounded-full border px-3 py-1 text-sm font-bold" style={{ color, borderColor: color, background: `${color}1f` }}>
          {CATEGORY_LABELS[p.kategori]}
        </span>
        <span className="text-sm text-muted">
          PM2.5: <strong className="text-white">{trNum(p.pm25, 1)} µg/m³</strong> ({trNum(p.pm25 / 5, 1)}× DSÖ) · OSB:{" "}
          <strong className="text-white">{p.toplam_osb} adet</strong>
        </span>
      </div>
    </div>
  );
}
