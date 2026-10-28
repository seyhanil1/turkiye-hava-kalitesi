"use client";

import Plot from "@/components/Plot";
import { stats } from "@/lib/data";

export function RegionOsbChart() {
  const rows = [...stats.regions.rows].sort((a, b) => b.toplam_osb - a.toplam_osb);
  return (
    <Plot
      height={420}
      data={[{
        type: "bar",
        x: rows.map((r) => r.bolge),
        y: rows.map((r) => r.toplam_osb),
        text: rows.map((r) => String(r.toplam_osb)),
        textposition: "outside",
        cliponaxis: false,
        marker: { color: "rgba(0,210,238,0.65)", line: { color: "#00d2ee", width: 1.5 } },
        hovertemplate: "%{x}: %{y} OSB<extra></extra>",
      }]}
      layout={{
        margin: { l: 50, r: 20, t: 20, b: 80 },
        xaxis: { tickangle: -35 },
        yaxis: { title: { text: "OSB sayısı", font: { size: 11, color: "#8faec9" } }, range: [0, Math.max(...rows.map((r) => r.toplam_osb)) * 1.15] },
      }}
    />
  );
}
