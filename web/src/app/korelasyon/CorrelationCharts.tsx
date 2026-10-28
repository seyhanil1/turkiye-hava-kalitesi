"use client";

import { useState } from "react";
import Plot from "@/components/Plot";
import { provinces, stats, tierOf } from "@/lib/data";
import { trNum } from "@/lib/format";

type VarKey = "osb_alani_hektar" | "toplam_osb" | "rakim" | "nufus";

export function ScatterChart() {
  const [x, setX] = useState<VarKey>("osb_alani_hektar");
  const s = stats.correlation.scatter[x];
  const q = stats.quantiles;
  const xs = provinces.map((p) => (x === "rakim" ? p.rakim ?? 500 : p[x]));
  const xMin = Math.min(...xs);
  const xMax = Math.max(...xs);
  const outlier = (p: (typeof provinces)[number]) => p.toplam_osb <= q.q1_osb && p.pm25 >= q.q3_pm25;

  return (
    <div>
      <label htmlFor="scatter-x" className="mb-1 block text-xs font-semibold text-muted">X ekseni değişkeni</label>
      <select
        id="scatter-x"
        value={x}
        onChange={(e) => setX(e.target.value as VarKey)}
        className="mb-3 rounded-lg border border-line bg-panel-2 px-3 py-1.5 text-sm text-white"
      >
        {(Object.keys(stats.correlation.scatter) as VarKey[]).map((k) => (
          <option key={k} value={k}>
            {stats.correlation.scatter[k].label} ({stats.correlation.scatter[k].unit})
          </option>
        ))}
      </select>
      <Plot
        height={430}
        data={[
          {
            x: xs, y: provinces.map((p) => p.pm25), mode: "markers", name: "İller",
            marker: {
              size: provinces.map((p) => (outlier(p) ? 11 : 8)),
              color: provinces.map((p) => (outlier(p) ? "#ef4444" : "#00d2ee")),
              opacity: 0.8, line: { color: "#ffffff", width: 0.5 },
            },
            text: provinces.map((p, i) =>
              `<b>${p.il}</b> (${p.bolge})<br>PM2.5: ${trNum(p.pm25, 1)} µg/m³<br>${s.label}: ${trNum(xs[i], x === "osb_alani_hektar" ? 1 : 0)} ${s.unit}<br>Kademe: ${tierOf(p.pm25).etiket}`),
            hoverinfo: "text",
          },
          {
            x: [xMin, xMax], y: [s.intercept + s.slope * xMin, s.intercept + s.slope * xMax], mode: "lines",
            name: `OLS trendi (eğim = ${trNum(s.slope, 4)}, R² = ${trNum(s.r2, 3)})`,
            line: { color: "#facc15", width: 2, dash: "dash" }, hoverinfo: "skip",
          },
        ]}
        layout={{
          margin: { l: 55, r: 20, t: 40, b: 50 },
          legend: { orientation: "h", y: 1.1, x: 0 },
          xaxis: { title: { text: `${s.label} (${s.unit})`, font: { size: 11, color: "#cbd5e1" } }, tickformat: ",d" },
          yaxis: { title: { text: "PM2.5 (µg/m³)", font: { size: 11, color: "#cbd5e1" } } },
        }}
      />
      <p className="text-[11.5px] text-muted">
        Kırmızı noktalar: OSB sayısı alt çeyrekte (≤ {trNum(q.q1_osb, 0)}) olup PM2.5&apos;i üst çeyrekte (≥ {trNum(q.q3_pm25, 1)}) olan iller.
        Pearson r = {trNum(s.r, 2)}, p = {trNum(s.p, 3)}.
      </p>
    </div>
  );
}

const QUAD: Record<string, { label: string; color: string }> = {
  HH: { label: "Yüksek-Yüksek (sıcak nokta)", color: "#ef4444" },
  LL: { label: "Düşük-Düşük (soğuk nokta)", color: "#10b981" },
  HL: { label: "Yüksek-Düşük (aykırı)", color: "#f59e0b" },
  LH: { label: "Düşük-Yüksek (aykırı)", color: "#8b5cf6" },
};

export function MoranChart() {
  const m = stats.correlation.moran;
  const zs = m.points.map((p) => p.z);
  const zMin = Math.min(...zs);
  const zMax = Math.max(...zs);
  return (
    <Plot
      height={430}
      data={[
        ...Object.entries(QUAD).map(([code, meta]) => {
          const pts = m.points.filter((p) => p.q === code);
          return {
            x: pts.map((p) => p.z), y: pts.map((p) => p.wz), mode: "markers" as const,
            name: `${meta.label} (${pts.length})`,
            marker: { size: 9, color: meta.color, opacity: 0.85, line: { color: "#ffffff", width: 0.5 } },
            text: pts.map((p) => `<b>${p.il}</b> (${p.bolge})<br>PM2.5: ${trNum(p.pm25, 1)} µg/m³<br>z: ${trNum(p.z, 2)} · Wz: ${trNum(p.wz, 2)}`),
            hoverinfo: "text" as const,
          };
        }),
        {
          x: [zMin, zMax], y: [m.I * zMin, m.I * zMax], mode: "lines" as const,
          name: `Moran doğrusu (eğim = ${trNum(m.I, 2)})`, line: { color: "#cbd5e1", width: 1.8 }, hoverinfo: "skip" as const,
        },
      ]}
      layout={{
        margin: { l: 55, r: 20, t: 50, b: 50 },
        legend: { orientation: "h", y: 1.15, x: 0, font: { size: 10.5 } },
        xaxis: { title: { text: "Standartlaştırılmış PM2.5 (z)", font: { size: 11, color: "#cbd5e1" } } },
        yaxis: { title: { text: "Mekânsal gecikme (Wz)", font: { size: 11, color: "#cbd5e1" } } },
        shapes: [
          { type: "line", xref: "paper", x0: 0, x1: 1, y0: 0, y1: 0, line: { color: "#093452", dash: "dash" } },
          { type: "line", yref: "paper", y0: 0, y1: 1, x0: 0, x1: 0, line: { color: "#093452", dash: "dash" } },
        ],
      }}
    />
  );
}
