// Statik veri katmanı: ../scripts/export_web_data.py tarafından üretilen JSON dosyaları.
import provincesJson from "@/data/provinces.json";
import statsJson from "@/data/stats.json";
import dailyJson from "@/data/daily.json";
import mapJson from "@/data/map.json";
import metaJson from "@/data/meta.json";
import { trCompare } from "./format";

export type Kategori = "A" | "B" | "YK" | "N";

export interface Province {
  il: string;
  plaka: number;
  bolge: string;
  lat: number;
  lon: number;
  nufus: number;
  pm25: number;
  pm10_cams: number;
  pm25_istasyon_max_2024: number | null;
  toplam_osb: number;
  faal_osb: number;
  osb_alani_hektar: number;
  toplam_parsel: number;
  solunum_olum: number;
  toplam_olum: number;
  solunum_olum_100k: number;
  toplam_olum_100k: number;
  solunum_olum_payi: number;
  atfedilen_olum_payi: number;
  atfedilen_olum_tahmini: number;
  dso_risk: string;
  dso_limit_kat: number;
  sanayi_tipi: string;
  rakim: number | null;
  pm_rank: number;
  sol_rank: number;
  nufus_rank: number;
  pct_hava: number;
  pct_solunum: number;
  kategori: Kategori;
  ozet: string[];
}

export interface Tier {
  id: string;
  etiket: string;
  tam_ad: string;
  min_val: number;
  max_val: number;
  renk: string;
  bg: string;
  border: string;
  aciklama: string;
}

export interface ScatterStat {
  label: string;
  unit: string;
  slope: number;
  intercept: number;
  r: number;
  r2: number;
  p: number;
}

export interface Stats {
  quantiles: { q1_osb: number; q3_osb: number; q1_pm25: number; q3_pm25: number };
  correlation: {
    osb_pm25: {
      n: number; pearson_r: number; pearson_p: number; spearman_rho: number; spearman_p: number;
      ci_lo: number; ci_hi: number;
    };
    nufus_pm25: { spearman_rho: number; spearman_p: number };
    scatter: Record<string, ScatterStat>;
    ols: {
      n: number; k: number; df_resid: number; r2: number; adj_r2: number;
      terms: { name: string; coef: number; se: number; t: number; p: number }[];
    };
    moran: {
      I: number; p: number; permutations: number;
      points: { il: string; bolge: string; pm25: number; z: number; wz: number; q: "HH" | "LL" | "HL" | "LH" }[];
    };
  };
  regions: {
    rows: {
      bolge: string; il_sayisi: number; ortalama: number; medyan: number; std: number;
      toplam_osb: number; faal_osb: number; solunum_100k: number; max_il: string; max_pm25: number;
    }[];
    anova: {
      anova_f: number; anova_p: number; anova_significant: boolean;
      kruskal_h: number; kruskal_p: number; kruskal_significant: boolean;
      levene_p: number; equal_variance: boolean; h0: string; h1: string; interpretation: string;
    };
  };
}

export interface Daily {
  dates: string[];
  cities: Record<string, (number | null)[]>;
  national: { date: string; pm25: number; min: number; max: number; ma7: number }[];
}

export interface MapData {
  width: number;
  height: number;
  provinces: { il: string; d: string; cx: number; cy: number }[];
}

export interface Meta {
  generated_at: string;
  cams_year: number;
  olum_yili: number;
  nufus_yili: number;
  daily_start: string;
  daily_end: string;
  sources: Record<string, string>;
  tiers: { kaynak_aciklamasi: string; pm25: Tier[] };
  who: Record<string, number | string>;
  airq: { rr_per_10: number; counterfactual: number };
  stations: { il: string; istasyon: string; pm25_istasyon_2024: number; kaynak: string }[];
}

export const provinces = provincesJson as Province[];
export const stats = statsJson as unknown as Stats;
export const daily = dailyJson as Daily;
export const mapData = mapJson as MapData;
export const meta = metaJson as unknown as Meta;

export const tiers = meta.tiers.pm25;
export const REGIONS = ["Marmara", "Ege", "Akdeniz", "İç Anadolu", "Karadeniz", "Doğu Anadolu", "Güneydoğu Anadolu"];
export const cityNames = provinces.map((p) => p.il).sort(trCompare);
export const byName: Record<string, Province> = Object.fromEntries(provinces.map((p) => [p.il, p]));

/** Yıllık PM2.5 değerinin kademe kaydı (üst sınır dahil; Python pm25_kademe ile aynı). */
export function tierOf(value: number): Tier {
  return tiers.find((t) => value <= t.max_val) ?? tiers[tiers.length - 1];
}

export const national = {
  mean: provinces.reduce((a, p) => a + p.pm25, 0) / provinces.length,
  max: provinces.reduce((a, p) => (p.pm25 > a.pm25 ? p : a)),
  min: provinces.reduce((a, p) => (p.pm25 < a.pm25 ? p : a)),
};

export function regionMean(bolge: string): number {
  const sub = provinces.filter((p) => p.bolge === bolge);
  return sub.reduce((a, p) => a + p.pm25, 0) / sub.length;
}

export const CATEGORY_LABELS: Record<Kategori, string> = {
  A: "Kategori A: Düşük OSB, Yüksek Kirlilik",
  B: "Kategori B: Yüksek OSB, Yüksek Kirlilik",
  YK: "Kategori Dışı (Yüksek Kirlilik / Orta Sanayi)",
  N: "Kategori Dışı (Orta Segment / Dengeli)",
};
