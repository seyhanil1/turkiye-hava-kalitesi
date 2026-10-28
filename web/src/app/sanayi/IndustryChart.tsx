"use client";

import Plot from "@/components/Plot";
import { stats } from "@/lib/data";
import { trNum } from "@/lib/format";

export default function IndustryChart() {
  const rows = [...stats.regions.rows].sort((a, b) => a.toplam_osb - b.toplam_osb);
  const total = rows.reduce((a, r) => a + r.toplam_osb, 0);
  return (
    <Plot
      height={360}
      data={[{
        type: "bar",
        orientation: "h",
        x: rows.map((r) => r.toplam_osb),
        y: rows.map((r) => r.bolge),
        text: rows.map((r) => `${r.toplam_osb} OSB · PM2.5 ${trNum(r.ortalama, 1)} µg/m³ · %${trNum((r.toplam_osb / total) * 100, 1)}`),
        textposition: "auto",
        insidetextanchor: "start",
        textfont: { color: "#ffffff", size: 11 },
        marker: { color: "#0369a1", line: { color: "rgba(255,255,255,0.25)", width: 1 } },
        hovertemplate: "%{y}: %{x} OSB<extra></extra>",
      }]}
      layout={{
        margin: { l: 135, r: 20, t: 10, b: 40 },
        xaxis: { title: { text: "OSB sayısı", font: { size: 11, color: "#8faec9" } } },
        yaxis: { tickfont: { color: "#ffffff", size: 12 } },
      }}
    />
  );
}
