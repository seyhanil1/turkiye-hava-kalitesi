"use client";

import { useState } from "react";
import type { Data } from "plotly.js";
import Plot from "./Plot";
import { byName, daily, provinces, stats, tierOf } from "@/lib/data";
import { trNum } from "@/lib/format";

const PERIODS = [7, 30, 90] as const;

/** Türkiye geneli (nüfus ağırlıklı) veya tek il için günlük CAMS PM2.5 serisi. */
export function DailySeriesChart({ il, height = 300 }: { il?: string; height?: number }) {
  const [days, setDays] = useState<(typeof PERIODS)[number]>(30);
  const isCity = Boolean(il);
  const allDates = isCity ? daily.dates : daily.national.map((d) => d.date);
  const allVals = isCity ? daily.cities[il!] ?? [] : daily.national.map((d) => d.pm25);
  const start = Math.max(0, allDates.length - days);
  const dates = allDates.slice(start);
  const vals = allVals.slice(start);

  if (allDates.length === 0) {
    return <p className="text-sm text-muted">Günlük CAMS verisi bulunamadı.</p>;
  }

  const traces: Data[] = [];
  if (!isCity) {
    const nat = daily.national.slice(start);
    traces.push(
      { x: dates, y: nat.map((d) => d.max), mode: "lines", line: { width: 0 }, hoverinfo: "skip", showlegend: false },
      {
        x: dates, y: nat.map((d) => d.min), mode: "lines", line: { width: 0 }, fill: "tonexty",
        fillcolor: "rgba(56,189,248,0.12)", name: "İller arası min–maks", hoverinfo: "skip",
      },
    );
  }
  traces.push({
    x: dates, y: vals, mode: "lines+markers", name: isCity ? il! : "Nüfus ağırlıklı Türkiye ortalaması",
    line: { color: "#00e5db", width: 2.2 }, marker: { size: 4 },
    hovertemplate: "%{x|%d.%m.%Y}<br>%{y:.1f} µg/m³<extra></extra>",
  });

  return (
    <div>
      <div className="mb-2 inline-flex rounded-lg border border-line bg-panel-2 p-0.5">
        {PERIODS.map((p) => (
          <button
            key={p}
            type="button"
            onClick={() => setDays(p)}
            aria-pressed={days === p}
            className={`rounded-md px-2.5 py-1 text-xs font-semibold ${days === p ? "bg-accent/15 text-accent" : "text-muted hover:text-white"}`}
          >
            {p} gün
          </button>
        ))}
      </div>
      <Plot
        data={traces}
        height={height}
        layout={{
          margin: { l: 40, r: 10, t: 10, b: 35 },
          showlegend: !isCity,
          legend: { orientation: "h", y: 1.12, x: 0 },
          yaxis: { title: { text: "PM2.5 (µg/m³)", font: { size: 11, color: "#8faec9" } }, rangemode: "tozero" },
          xaxis: { tickformat: "%d.%m" },
          shapes: [{ type: "line", xref: "paper", x0: 0, x1: 1, y0: 15, y1: 15, line: { color: "#facc15", width: 1, dash: "dot" } }],
          annotations: [{
            xref: "paper", x: 1, y: 15, text: "DSÖ 24 saatlik (15)", showarrow: false,
            font: { size: 10, color: "#facc15" }, xanchor: "right", yanchor: "bottom",
          }],
        }}
      />
    </div>
  );
}

/** 7 bölgenin yıllık PM2.5 ortalaması (yatay çubuk) ve DSÖ kılavuz çizgisi. */
export function RegionBenchmarkChart({ height = 340 }: { height?: number }) {
  const rows = [...stats.regions.rows].sort((a, b) => a.ortalama - b.ortalama);
  const maxX = Math.max(20, Math.ceil((Math.max(...rows.map((r) => r.ortalama)) * 1.7) / 5) * 5);
  return (
    <Plot
      height={height}
      data={[{
        type: "bar",
        orientation: "h",
        x: rows.map((r) => r.ortalama),
        y: rows.map((r) => r.bolge),
        text: rows.map((r) => `${trNum(r.ortalama, 1)} µg/m³ · En yüksek: ${r.max_il} (${trNum(r.max_pm25, 1)})`),
        textposition: "outside",
        textfont: { color: "#e2e8f0", size: 11 },
        marker: { color: rows.map((r) => tierOf(r.ortalama).renk), opacity: 0.85 },
        hovertemplate: "%{y}: %{x:.2f} µg/m³<extra></extra>",
        cliponaxis: false,
      }]}
      layout={{
        margin: { l: 135, r: 20, t: 30, b: 35 },
        xaxis: { range: [0, maxX], title: { text: "Bölge ortalaması PM2.5 (µg/m³)", font: { size: 11, color: "#8faec9" } } },
        yaxis: { tickfont: { color: "#f8fafc", size: 12 } },
        shapes: [{ type: "line", x0: 5, x1: 5, yref: "paper", y0: 0, y1: 1, line: { color: "#ef4444", width: 2, dash: "dash" } }],
        annotations: [{
          x: 5, y: 1.02, yref: "paper", text: "DSÖ yıllık kılavuz (5 µg/m³)", showarrow: false,
          xanchor: "left", yanchor: "bottom", font: { color: "#ef4444", size: 11 },
        }],
      }}
    />
  );
}

/** İllerin bölgelere göre dağılımı: bölge başına kutu + kademe renginde il noktaları. */
export function RegionStripChart({ height = 420 }: { height?: number }) {
  const order = [...stats.regions.rows].sort((a, b) => b.ortalama - a.ortalama).map((r) => r.bolge);
  // Noktalar bölge içinde PM2.5 sırasına göre ortadan iki yana sabit dağılır (her açılışta aynı görünüm)
  const SPREAD = [0, -1, 1, -0.5, 0.5, -1.5, 1.5];
  const points = order.flatMap((bolge, i) => {
    const sub = provinces.filter((p) => p.bolge === bolge).sort((a, b) => a.pm25 - b.pm25);
    return sub.map((p, k) => ({ p, x: i + SPREAD[k % SPREAD.length] * 0.11 }));
  });
  const boxes: Data[] = order.map((bolge, i) => {
    const ys = provinces.filter((p) => p.bolge === bolge).map((p) => p.pm25);
    return {
      type: "box", name: bolge, x: ys.map(() => i), y: ys, boxpoints: false, width: 0.55,
      fillcolor: "rgba(56,189,248,0.07)", line: { color: "rgba(56,189,248,0.55)", width: 1.2 },
      hoverinfo: "skip", showlegend: false,
    };
  });
  return (
    <Plot
      height={height}
      data={[
        ...boxes,
        {
          type: "scatter", mode: "markers", showlegend: false,
          x: points.map((d) => d.x), y: points.map((d) => d.p.pm25),
          marker: {
            size: 7, color: points.map((d) => tierOf(d.p.pm25).renk), opacity: 0.9,
            line: { color: "#031322", width: 1 },
          },
          text: points.map((d) => `<b>${d.p.il}</b><br>${trNum(d.p.pm25, 1)} µg/m³ · ${tierOf(d.p.pm25).etiket}`),
          hovertemplate: "%{text}<extra></extra>",
        },
      ]}
      layout={{
        margin: { l: 50, r: 20, t: 20, b: 80 },
        xaxis: {
          tickmode: "array", tickvals: order.map((_, i) => i), ticktext: order, tickangle: -35,
          showgrid: false, zeroline: false, range: [-0.6, order.length - 0.4],
        },
        yaxis: { title: { text: "PM2.5 (µg/m³)", font: { size: 11, color: "#8faec9" } }, rangemode: "tozero" },
        shapes: [{ type: "line", xref: "paper", x0: 0, x1: 1, y0: 5, y1: 5, line: { color: "#ef4444", width: 1.2, dash: "dash" } }],
        annotations: [{
          xref: "paper", x: 1, y: 5, text: "DSÖ yıllık kılavuz (5)", showarrow: false,
          xanchor: "right", yanchor: "bottom", font: { size: 10, color: "#ef4444" },
        }],
      }}
    />
  );
}

/** Seçilen il, bölgesi ve Türkiye ortalaması karşılaştırması. */
export function CityCompareChart({ il, height = 300 }: { il: string; height?: number }) {
  const p = byName[il];
  const sub = provinces.filter((x) => x.bolge === p.bolge);
  const bolge = sub.reduce((a, x) => a + x.pm25, 0) / sub.length;
  const tr = provinces.reduce((a, x) => a + x.pm25, 0) / provinces.length;
  const labels = [il, `${p.bolge} Bölgesi`, "Türkiye (düz il ort.)"];
  const vals = [p.pm25, bolge, tr];
  return (
    <Plot
      height={height}
      data={[{
        type: "bar", x: labels, y: vals,
        text: vals.map((v) => `${trNum(v, 1)} µg/m³`), textposition: "outside", cliponaxis: false,
        marker: { color: ["#00e5db", "#38bdf8", "#64748b"] },
        hovertemplate: "%{x}: %{y:.2f} µg/m³<extra></extra>",
      }]}
      layout={{
        margin: { l: 45, r: 62, t: 25, b: 40 },
        yaxis: { range: [0, Math.max(...vals) * 1.3], title: { text: "PM2.5 (µg/m³)", font: { size: 11, color: "#8faec9" } } },
        shapes: [{ type: "line", xref: "paper", x0: 0, x1: 1, y0: 5, y1: 5, line: { color: "#ef4444", width: 1.5, dash: "dash" } }],
        annotations: [{ xref: "paper", x: 1.01, y: 5, text: "DSÖ<br>yıllık (5)", showarrow: false, xanchor: "left", yanchor: "middle", align: "left", font: { size: 10, color: "#ef4444" } }],
      }}
    />
  );
}
