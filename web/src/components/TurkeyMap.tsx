"use client";

import { useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { byName, daily, mapData, tierOf, tiers } from "@/lib/data";
import { trNum } from "@/lib/format";

// Günlük değerler yıllık kademelerle karşılaştırılamaz; bu yüzden ayrı, sürekli bir renk ölçeği kullanılır.
// Referans: DSÖ 24 saatlik kılavuz değeri 15 µg/m³.
const DAILY_STOPS: [number, string][] = [
  [0, "#0c4a6e"],
  [5, "#0ea5e9"],
  [15, "#facc15"],
  [30, "#f97316"],
  [50, "#ef4444"],
];

function dailyColor(v: number): string {
  for (let i = 1; i < DAILY_STOPS.length; i++) {
    if (v <= DAILY_STOPS[i][0]) return DAILY_STOPS[i - 1][1];
  }
  return DAILY_STOPS[DAILY_STOPS.length - 1][1];
}

function formatDate(iso: string) {
  const [y, m, d] = iso.split("-");
  return `${d}.${m}.${y}`;
}

type Mode = "annual" | "daily";

export default function TurkeyMap() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("annual");
  const [dayIdx, setDayIdx] = useState(daily.dates.length - 1);
  const [playing, setPlaying] = useState(false);
  const [hover, setHover] = useState<{ il: string; x: number; y: number; w: number } | null>(null);
  const wrapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!playing) return;
    const id = setInterval(() => {
      setDayIdx((i) => (i + 1 >= daily.dates.length ? 0 : i + 1));
    }, 350);
    return () => clearInterval(id);
  }, [playing]);

  const values = useMemo(() => {
    const out: Record<string, number | null> = {};
    for (const p of mapData.provinces) {
      out[p.il] = mode === "annual" ? byName[p.il].pm25 : daily.cities[p.il]?.[dayIdx] ?? null;
    }
    return out;
  }, [mode, dayIdx]);

  const colorOf = (v: number | null) =>
    v === null ? "#2b3c52" : mode === "annual" ? tierOf(v).renk : dailyColor(v);

  const hovered = hover ? byName[hover.il] : null;
  const hoveredVal = hover ? values[hover.il] : null;
  const hasDaily = daily.dates.length > 0;

  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <div className="inline-flex rounded-lg border border-line bg-panel-2 p-0.5" role="tablist">
          {(["annual", "daily"] as Mode[]).map((m) => (
            <button
              key={m}
              type="button"
              role="tab"
              aria-selected={mode === m}
              disabled={m === "daily" && !hasDaily}
              onClick={() => { setMode(m); setPlaying(false); }}
              className={`rounded-md px-3 py-1 text-xs font-semibold transition-colors ${
                mode === m ? "bg-accent/15 text-accent" : "text-muted hover:text-white"
              } disabled:opacity-40`}
            >
              {m === "annual" ? "Yıllık ortalama (2025)" : "Günlük (son 90 gün)"}
            </button>
          ))}
        </div>
        {mode === "daily" && hasDaily && (
          <span className="text-xs font-semibold text-white">{formatDate(daily.dates[dayIdx])}</span>
        )}
      </div>

      <div
        ref={wrapRef}
        className="relative"
        onMouseLeave={() => setHover(null)}
      >
        <svg viewBox={`0 0 ${mapData.width} ${mapData.height}`} className="h-auto w-full" role="img" aria-label="Türkiye illeri PM2.5 haritası">
          {mapData.provinces.map((p) => (
            <path
              key={p.il}
              d={p.d}
              fill={colorOf(values[p.il])}
              fillOpacity={hover?.il === p.il ? 1 : 0.82}
              stroke={hover?.il === p.il ? "#ffffff" : "#031322"}
              strokeWidth={hover?.il === p.il ? 1.6 : 0.6}
              className="cursor-pointer transition-[fill] duration-200"
              onMouseMove={(e) => {
                const box = wrapRef.current?.getBoundingClientRect();
                if (box) setHover({ il: p.il, x: e.clientX - box.left, y: e.clientY - box.top, w: box.width });
              }}
              onClick={() => router.push(`/sehir-karnesi/?il=${encodeURIComponent(p.il)}`)}
            >
              <title>{`${p.il}: ${values[p.il] === null ? "veri yok" : `${trNum(values[p.il], 1)} µg/m³`}`}</title>
            </path>
          ))}
        </svg>

        {hover && hovered && (
          <div
            className="pointer-events-none absolute z-10 min-w-44 rounded-lg border border-line bg-[#021626]/95 px-3 py-2 text-xs shadow-xl"
            style={{
              left: Math.min(hover.x + 14, hover.w - 190),
              top: hover.y + 14,
            }}
          >
            <div className="text-sm font-bold text-white">
              {hovered.il} <span className="font-normal text-muted">({String(hovered.plaka).padStart(2, "0")})</span>
            </div>
            <div className="text-muted">{hovered.bolge}</div>
            <div className="mt-1 text-ink-soft">
              {mode === "annual" ? "Yıllık PM2.5" : "Günlük PM2.5"}:{" "}
              <strong className="text-white">{hoveredVal === null ? "veri yok" : `${trNum(hoveredVal, 1)} µg/m³`}</strong>
            </div>
            {mode === "annual" && (
              <div className="font-semibold" style={{ color: tierOf(hovered.pm25).renk }}>{tierOf(hovered.pm25).etiket}</div>
            )}
            {hovered.pm25_istasyon_max_2024 !== null && (
              <div className="mt-1 text-[11px] text-amber-300">
                Kara Rapor istasyonu: {trNum(hovered.pm25_istasyon_max_2024, 1)} µg/m³
              </div>
            )}
            <div className="mt-1 text-[10px] text-muted">Karne için tıklayın</div>
          </div>
        )}
      </div>

      {mode === "daily" && hasDaily && (
        <div className="mt-3 flex items-center gap-3">
          <button
            type="button"
            onClick={() => setPlaying((v) => !v)}
            className="rounded-md border border-line bg-panel-2 px-3 py-1 text-xs font-semibold text-accent"
            aria-label={playing ? "Animasyonu duraklat" : "Günleri oynat"}
          >
            {playing ? "Duraklat" : "Oynat"}
          </button>
          <input
            type="range"
            min={0}
            max={daily.dates.length - 1}
            value={dayIdx}
            onChange={(e) => { setPlaying(false); setDayIdx(Number(e.target.value)); }}
            className="flex-1 accent-[#00e5db]"
            aria-label="Gün seçimi"
          />
        </div>
      )}

      {/* Lejant */}
      <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-ink-soft">
        {mode === "annual"
          ? tiers.map((t) => (
              <span key={t.id} className="inline-flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-sm" style={{ background: t.renk }} />
                {t.etiket} ({t.min_val === 0 ? `≤${t.max_val}` : t.max_val >= 900 ? `>${t.min_val}` : `${trNum(t.min_val + 0.1, 1)}–${t.max_val}`})
              </span>
            ))
          : DAILY_STOPS.map(([v, c], i) => (
              <span key={v} className="inline-flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-sm" style={{ background: c }} />
                {i + 1 < DAILY_STOPS.length ? `${v}–${DAILY_STOPS[i + 1][0]}` : `>${v}`} µg/m³
              </span>
            ))}
      </div>
      <p className="mt-1 text-[11px] text-muted">
        {mode === "annual"
          ? "Kademeler DSÖ 2021 yıllık ara hedeflerine dayanır; tüm iller DSÖ kılavuz değerinin (5 µg/m³) üzerindedir."
          : "Günlük değerler yıllık kademelerle karşılaştırılamaz; DSÖ 24 saatlik kılavuz değeri 15 µg/m³'tür."}
      </p>
    </div>
  );
}
