// Türkçe sayı biçimlendirme. Python tarafındaki analytics/summaries.py:to_tr_num ile aynı
// kuralı izler: yarım yukarı yuvarlama (ROUND_HALF_UP), binlik ayırıcı nokta, ondalık virgül.

function roundHalfUp(value: number, decimals: number): number {
  const factor = 10 ** decimals;
  // 4 haneye yuvarlayıp ölçeklemek, ikili kayan nokta hatalarını (ör. 2.675) giderir
  const scaled = Number((Math.abs(value) * factor).toFixed(4));
  return (Math.sign(value) * Math.floor(scaled + 0.5)) / factor;
}

export function trNum(value: number | null | undefined, decimals = 1): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  const rounded = roundHalfUp(value, decimals);
  const sign = rounded < 0 ? "-" : "";
  const [intPart, frac] = Math.abs(rounded).toFixed(decimals).split(".");
  const grouped = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  return frac ? `${sign}${grouped},${frac}` : `${sign}${grouped}`;
}

export function trSign(value: number, decimals = 1): string {
  return `${value > 0 ? "+" : ""}${trNum(value, decimals)}`;
}

export function trP(p: number): string {
  return p < 0.001 ? "p < 0,001" : `p = ${trNum(p, 3)}`;
}

export function roundDisp(value: number, decimals = 1): number {
  return roundHalfUp(value, decimals);
}

/** Türkçe karakterleri sadeleştirir (arama ve eşleştirme için). */
export function normalizeTr(text: string): string {
  return text
    .replace(/İ/g, "i").replace(/I/g, "i").replace(/ı/g, "i")
    .replace(/[Ğğ]/g, "g").replace(/[Üü]/g, "u").replace(/[Şş]/g, "s")
    .replace(/[Öö]/g, "o").replace(/[Çç]/g, "c").replace(/µ/g, "u")
    .replace(/['"’`]/g, " ")
    .toLowerCase()
    .trim();
}

export function trCompare(a: string, b: string): number {
  return a.localeCompare(b, "tr");
}
