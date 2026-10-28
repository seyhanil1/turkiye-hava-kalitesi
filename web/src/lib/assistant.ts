// Yerel, kural tabanlı veri asistanı (harici API yok). Python sürümündeki
// app_pages/chat_assistant_page.py:generate_local_response kurallarının TypeScript karşılığıdır.
import { byName, provinces, stats, type Province } from "./data";
import { normalizeTr, trNum } from "./format";

const f1 = (v: number) => trNum(v, 1);
const pad = (n: number) => String(n).padStart(2, "0");
const has = (text: string, keys: string[]) => keys.some((k) => text.includes(k));
const sortBy = (key: keyof Province, desc: boolean) =>
  [...provinces].sort((a, b) => ((a[key] as number) - (b[key] as number)) * (desc ? -1 : 1));

/** Metinde geçen il adlarını, metindeki sıralarıyla döndürür (uzun adlar önce taranır). */
export function detectCities(prompt: string): string[] {
  let work = normalizeTr(prompt);
  const map = new Map(provinces.map((p) => [normalizeTr(p.il), p.il]));
  const names = [...map.keys()].sort((a, b) => b.length - a.length);
  const found: [number, string][] = [];
  for (const n of names) {
    const re = new RegExp(`(?<![a-z0-9])${n.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}(?![a-z0-9])`);
    const m = re.exec(work);
    if (m) {
      found.push([m.index, map.get(n)!]);
      work = work.slice(0, m.index) + " ".repeat(n.length) + work.slice(m.index + n.length);
    }
  }
  return found.sort((a, b) => a[0] - b[0]).map(([, c]) => c);
}

export const WELCOME = [
  "Merhaba! Ben **HavaAtlası Veri Asistanı**.",
  "",
  "81 ilin PM2.5 değerleri (CAMS 2025 model), OSB envanteri ve TÜİK solunum sağlığı verileri üzerinden, tamamen tarayıcınızda çalışan kurallarla yanıt veriyorum. Yapay zeka modeli kullanmıyorum.",
  "",
  "Önerilen soruları tek tıkla sorabilir ya da bir il veya konu yazabilirsiniz.",
].join("\n");

export const QUICK_QUESTIONS: { label: string; prompt: string }[] = [
  { label: "Sanayisi az ama kirli iller", prompt: "Sanayisi az olmasına rağmen havası en kirli iller hangileri ve sebebi ne?" },
  { label: "DSÖ kılavuzunu karşılayan il var mı?", prompt: "DSÖ'nün 5 µg/m³ kılavuz değerini karşılayan temiz bir ilimiz var mı?" },
  { label: "İstanbul ile Ankara", prompt: "İstanbul ile Ankara'nın hava kalitesi ve sanayi yükünü kıyasla." },
  { label: "En çok OSB'li illerde kirlilik", prompt: "Organize Sanayi Bölgesi (OSB) sayısı en yüksek illerde kirlilik ne durumda?" },
  { label: "Kirlilik ve solunum ölümleri", prompt: "Hava kirliliği ile solunum yolu ölümleri arasında doğrudan bir paralellik var mı?" },
  { label: "En temiz ve en kirli bölgeler", prompt: "Türkiye'nin havası en temiz ve en kirli coğrafi bölgeleri hangileridir?" },
];

function compare(c1: string, c2: string): string {
  const a = byName[c1];
  const b = byName[c2];
  const note = a.pm25 > b.pm25
    ? `**${c1}**, ${c2} iline kıyasla PM2.5 bazında **${f1(a.pm25 - b.pm25)} µg/m³** daha yüksek değere sahiptir.`
    : `**${c2}**, ${c1} iline kıyasla PM2.5 bazında **${f1(b.pm25 - a.pm25)} µg/m³** daha yüksek değere sahiptir.`;
  return [
    `⚖️ **${c1} ve ${c2}: karşılaştırmalı hava kalitesi ve sanayi analizi**`,
    "",
    `| Gösterge | **${c1}** | **${c2}** |`,
    "| :--- | :---: | :---: |",
    `| Coğrafi bölge | ${a.bolge} | ${b.bolge} |`,
    `| PM2.5 (CAMS 2025) | \`${f1(a.pm25)} µg/m³\` | \`${f1(b.pm25)} µg/m³\` |`,
    `| DSÖ kılavuzuna oran (5 µg/m³) | **${f1(a.pm25 / 5)}x** (${a.dso_risk}) | **${f1(b.pm25 / 5)}x** (${b.dso_risk}) |`,
    `| Organize sanayi bölgesi (OSB) | ${a.toplam_osb} adet | ${b.toplam_osb} adet |`,
    `| Sanayi parsel sayısı | ${trNum(a.toplam_parsel, 0)} | ${trNum(b.toplam_parsel, 0)} |`,
    `| Solunum kaynaklı ölüm (yüz binde) | \`${f1(a.solunum_olum_100k)}\` | \`${f1(b.solunum_olum_100k)}\` |`,
    "",
    `💡 **Değerlendirme:** ${note}`,
  ].join("\n");
}

export function answer(prompt: string): string {
  const p = normalizeTr(prompt);
  const cities = detectCities(prompt);

  // 1. İki veya daha fazla il: yan yana karşılaştırma
  if (cities.length >= 2) return compare(cities[0], cities[1]);

  // Sanayisi az ama kirli iller
  if ((p.includes("sanayisi az") || p.includes("sanayisiz") || (p.includes("sanayi") && p.includes("az")))
    && has(p, ["kirli", "kirlilik", "hava", "sebebi"])) {
    const q1 = stats.quantiles.q1_osb;
    const low = provinces.filter((x) => x.toplam_osb <= q1).sort((a, b) => b.pm25 - a.pm25);
    const lines = low.slice(0, 4).map((x) =>
      `- **${x.il}** (${x.bolge}): PM2.5 \`${f1(x.pm25)} µg/m³\` (DSÖ kılavuzunun ${f1(x.pm25 / 5)} katı) · **yalnızca ${x.toplam_osb} OSB**`);
    const station = low.filter((x) => x.pm25_istasyon_max_2024 !== null)
      .sort((a, b) => (b.pm25_istasyon_max_2024 ?? 0) - (a.pm25_istasyon_max_2024 ?? 0))
      .map((x) => `- **${x.il}**: istasyon \`${f1(x.pm25_istasyon_max_2024!)} µg/m³\` — CAMS modeli \`${f1(x.pm25)} µg/m³\``);
    return [
      `🏔️ **Sanayisi az olmasına rağmen havası en kirli iller (OSB sayısı ≤ ${trNum(q1, 0)}, CAMS 2025):**`,
      "", ...lines, "",
      ...(station.length ? ["📍 **Kara Rapor 2025 istasyon ölçümleri (2024) bu illerde modelden belirgin yüksek:**", ...station, ""] : []),
      "🔍 **Sanayi dışı olası nedenler:**",
      "1. **Topoğrafik çanak (havza):** Etrafı dağlarla çevrili havzalarda rüzgar sirkülasyonu kısıtlıdır; kirli hava havzada kalır.",
      "2. **Kış sıcaklık terselmesi (inversiyon):** Soğuk hava yere yakın sıkışır ve bacalardan, egzozlardan çıkan partiküllerin dağılmasını engeller.",
      "3. **Sınır ötesi toz taşınımı:** Güney ve doğu illeri kurak bölgelerden gelen mineral toza açıktır.",
      "4. **Konut ısınmasında katı yakıt:** Kömür ve linyit ısınması yer seviyesinde yoğun partikül birikimine yol açar.",
      "",
      "⚠️ **Not:** ~10 km çözünürlüklü CAMS modeli bu yerel etkileri tam yakalayamaz; il sıralaması istasyon ölçümlerinden farklı olabilir.",
    ].join("\n");
  }

  // DSÖ kılavuzunu karşılayan il var mı?
  if (has(p, ["dso", "5 ug", "kilavuz"]) && has(p, ["karsilayan", "karsiliyor", "uyumlu", "var mi"])) {
    const asc = sortBy("pm25", false);
    const min = asc[0];
    const max = asc[asc.length - 1];
    const avg = provinces.reduce((s, x) => s + x.pm25, 0) / provinces.length;
    const ok = provinces.filter((x) => x.pm25 <= 5).length;
    return [
      "🌍 **DSÖ yıllık kılavuz değeri (5 µg/m³) uyumluluk analizi**",
      "",
      ok === 0
        ? "❌ **Hayır, 81 ilin hiçbiri DSÖ'nün 5 µg/m³ yıllık kılavuz değerini karşılamıyor.**"
        : `✅ **${ok} il DSÖ'nün 5 µg/m³ yıllık kılavuz değerini karşılıyor.**`,
      "",
      `- **Uyum oranı:** ${ok} / 81 il`,
      `- **81 il ortalaması:** \`${f1(avg)} µg/m³\` (kılavuzun **${f1(avg / 5)} katı**)`,
      `- **En düşük il:** **${min.il}** (\`${f1(min.pm25)} µg/m³\`, ${f1(min.pm25 / 5)} katı)`,
      `- **En yüksek il:** **${max.il}** (\`${f1(max.pm25)} µg/m³\`, ${f1(max.pm25 / 5)} katı)`,
      "",
      "_Değerler CAMS 2025 yıllık model ortalamasıdır; istasyon ölçümleri genellikle daha yüksektir (ör. Kara Rapor 2025'te Iğdır istasyonu 46,8 µg/m³)._",
    ].join("\n");
  }

  // Kirlilik ve solunum ölümleri paralelliği
  if ((p.includes("solunum") || p.includes("vefat")) && (p.includes("paralellik") || p.includes("dogrudan") || (p.includes("iliski") && p.includes("kirlilik")))) {
    return [
      "🫁 **Hava kirliliği ile solunum yolu ölümleri arasındaki ilişki**",
      "",
      "⚠️ **Cevap: İl düzeyinde doğrudan ve doğrusal bir paralellik görünmüyor.**",
      "",
      "1. **Yaş yapısı:** Solunum yolu ölümleri (KOAH, zatürre vb.) ileri yaşlarda belirgin artar. Kaba solunum ölüm hızı, toplam ölüm hızıyla güçlü biçimde ilişkilidir; yani büyük ölçüde illerin yaş yapısını yansıtır.",
      `2. **Genç nüfuslu iller:** Hakkari'de kaba solunum ölüm hızı ${f1(byName["Hakkari"].solunum_olum_100k)}, Edirne'de ${f1(byName["Edirne"].solunum_olum_100k)} (yüz binde); fark esas olarak yaş yapısından kaynaklanır.`,
      "3. **Uzun dönem maruziyet:** Kronik solunum hastalıkları anlık kirlilikten çok uzun yıllar süren birikimli maruziyetle ilişkilidir.",
      "4. **Ekolojik yanılgı:** İl ortalamaları bireylerin mesleki veya iç ortam maruziyetini yansıtmaz.",
      "",
      "💡 **Özet:** Hava kirliliği kanıtlanmış bir risk etkenidir; ancak il bazındaki kaba ölüm hızlarında yaş yapısı birincil belirleyicidir. Daha uygun göstergeler için Şehir Karnesi'ndeki *solunum ölüm payı* ve *atfedilebilir ölüm tahminine* bakın.",
    ].join("\n");
  }

  // OSB sayısı en yüksek illerde kirlilik
  if ((p.includes("osb sayisi en yuksek") || p.includes("organize sanayi bolgesi") || p.includes("en cok osb")) && (p.includes("kirlilik") || p.includes("ne durumda"))) {
    const top = sortBy("toplam_osb", true).slice(0, 5);
    const avgTop = top.reduce((s, x) => s + x.pm25, 0) / top.length;
    const avg = provinces.reduce((s, x) => s + x.pm25, 0) / provinces.length;
    return [
      "🏭 **OSB sayısı en yüksek illerde kirlilik durumu:**",
      "",
      ...top.map((x, i) => `${i + 1}. **${x.il}** (${x.bolge}): **${x.toplam_osb} OSB** (${trNum(x.toplam_parsel, 0)} parsel) · PM2.5 \`${f1(x.pm25)} µg/m³\``),
      "",
      `📊 Bu 5 ilin PM2.5 ortalaması \`${f1(avgTop)} µg/m³\`, 81 il ortalaması \`${f1(avg)} µg/m³\`.`,
      "",
      "⚠️ **Yorum sınırı:** OSB sayısı yüksek iller aynı zamanda nüfusu ve trafiği yüksek büyükşehirlerdir; il düzeyindeki bu karşılaştırma sanayinin etkisini nüfus, ısınma, trafik ve topoğrafyadan ayıramaz.",
    ].join("\n");
  }

  // Korelasyon / ilişki
  if (has(p, ["kirlilik ve osb", "osb ve kirlilik", "osb iliskisi", "sanayi iliskisi", "korelasyon", "baglanti"])
    || (p.includes("iliski") && has(p, ["osb", "sanayi", "kirlilik"]))) {
    const c = stats.correlation;
    const pStr = c.osb_pm25.spearman_p < 0.001 ? "p < 0,001" : `p = ${trNum(c.osb_pm25.spearman_p, 3)}`;
    return [
      "📊 **OSB alanı ile PM2.5 ilişkisi**",
      "",
      `- **Spearman sıra korelasyonu (ρ):** \`${trNum(c.osb_pm25.spearman_rho, 2)}\` (${pStr}, n = 81)`,
      `- **Karşılaştırma — nüfus ile PM2.5 (ρ):** \`${trNum(c.nufus_pm25.spearman_rho, 2)}\``,
      `- **Çoklu regresyonda OSB sayısı:** ${c.ols.terms[1].p < 0.05 ? "anlamlı" : "nüfus ve rakım kontrol edilince anlamlı değil"} (p = ${trNum(c.ols.terms[1].p, 3)})`,
      "",
      "🔍 **Değerlendirme:** OSB'si büyük iller aynı zamanda kalabalık büyükşehirlerdir; nüfus, trafik ve konut ısınması PM2.5 ile en az OSB kadar güçlü ilişkilidir. İl düzeyindeki korelasyon bir ilişkiyi betimler, nedensellik göstermez.",
    ].join("\n");
  }

  // Bölgesel sıralama
  if (has(p, ["en temiz bolge", "temiz bolge", "bolgeler", "bolge siralamasi", "cografi bolge", "en temiz ve en kirli", "en kirli ve en temiz"])
    || (p.includes("bolge") && has(p, ["temiz", "kirli", "iyi", "hangisi", "siralama"]))) {
    const rows = [...stats.regions.rows].sort((a, b) => a.ortalama - b.ortalama);
    const clean = rows[0];
    const dirty = rows[rows.length - 1];
    const cleanCity = provinces.filter((x) => x.bolge === clean.bolge).sort((a, b) => a.pm25 - b.pm25)[0];
    return [
      "🌍 **7 coğrafi bölgenin hava kalitesi sıralaması (CAMS 2025):**",
      "",
      `🌿 **En temiz bölge:** **${clean.bolge}** (ortalama \`${f1(clean.ortalama)} µg/m³\`) · en düşük il: **${cleanCity.il}** (\`${f1(cleanCity.pm25)} µg/m³\`)`,
      `🚨 **En kirli bölge:** **${dirty.bolge}** (ortalama \`${f1(dirty.ortalama)} µg/m³\`)`,
      "",
      ...rows.map((r, i) => `${i + 1}. **${r.bolge}:** \`${f1(r.ortalama)} µg/m³\` (DSÖ kılavuzunun ${f1(r.ortalama / 5)} katı)`),
      "",
      `_Bölgeler arası fark: ${stats.regions.anova.interpretation}_`,
    ].join("\n");
  }

  // Solunum riski en yüksek iller
  if (has(p, ["solunum riski", "solunum olumu", "solunum vefati", "solunum", "akciger", "nefes", "vefat", "olum orani"])) {
    const top = sortBy("solunum_olum_100k", true).slice(0, 3);
    const avg = provinces.reduce((s, x) => s + x.solunum_olum_100k, 0) / provinces.length;
    return [
      "🫁 **TÜİK kaba solunum ölüm hızı en yüksek 3 il:**",
      "",
      ...top.map((x, i) => `${i + 1}. **${x.il}** (${x.bolge}): \`${f1(x.solunum_olum_100k)} / yüz bin\` · yıllık ~${trNum(x.solunum_olum, 0)} ölüm · PM2.5 \`${f1(x.pm25)} µg/m³\``),
      "",
      `_(81 il ortalaması: ~${f1(avg)} / yüz bin)_`,
      "",
      "💡 Bu kaba hızlar yaşa göre düzeltilmemiştir; yaşlı nüfusu fazla illerde yapısal olarak yüksektir.",
    ].join("\n");
  }

  // DSÖ limitini en çok aşanlar
  if (has(p, ["dso limitini en cok asanlar", "dso limit", "dso asimi", "dso yu en cok", "dso hedef", "rehber sinir", "5 ug", "dso siniri"])
    || (p.includes("dso") && has(p, ["asan", "en cok", "kat", "limit", "sinir"]))) {
    const top = sortBy("pm25", true).slice(0, 3);
    const ok = provinces.filter((x) => x.pm25 <= 5).length;
    return [
      "🚨 **DSÖ yıllık kılavuz değerini (5 µg/m³) en çok aşan iller:**",
      "",
      ...top.map((x, i) => `${i + 1}. **${x.il}** (${x.bolge}): \`${f1(x.pm25)} µg/m³\` · kılavuzun **${f1(x.pm25 / 5)} katı** · kademe: **${x.dso_risk}** · ${x.toplam_osb} OSB`),
      "",
      `📌 **Uyum durumu:** ${ok} / 81 il DSÖ'nün 5 µg/m³ yıllık kılavuz değerini karşılıyor.`,
    ].join("\n");
  }

  // Sanayi baskısı en yüksek iller
  if (has(p, ["sanayi baskisi", "parsel", "en cok osb", "sanayi illeri", "sanayi yogunlugu", "osb", "sanayi"])) {
    const top = sortBy("toplam_parsel", true).slice(0, 4);
    return [
      "🏭 **Sanayi parsel sayısı en yüksek iller (OSBÜK):**",
      "",
      ...top.map((x, i) => `${i + 1}. **${x.il}** (${x.bolge}): **${x.toplam_osb} OSB** · **${trNum(x.toplam_parsel, 0)} parsel** · ${trNum(x.osb_alani_hektar, 0)} hektar · PM2.5 \`${f1(x.pm25)} µg/m³\``),
    ].join("\n");
  }

  // Tek il: karne
  if (cities.length === 1) {
    const x = byName[cities[0]];
    return [
      `🏙️ **${x.il} ili hava kalitesi karnesi**`,
      "",
      `- **PM2.5 (CAMS 2025):** \`${f1(x.pm25)} µg/m³\``,
      `- **Kademe:** **${x.dso_risk}** (DSÖ 5 µg/m³ yıllık kılavuzunun **${f1(x.pm25 / 5)} katı**)`,
      ...(x.pm25_istasyon_max_2024 !== null ? [`- **Kara Rapor 2025 istasyonu:** \`${f1(x.pm25_istasyon_max_2024)} µg/m³\``] : []),
      `- **Organize sanayi bölgesi (OSB):** **${x.toplam_osb} adet** (${trNum(x.toplam_parsel, 0)} parsel)`,
      `- **Bölge ve plaka:** ${x.bolge} · ${pad(x.plaka)}`,
      `- **Solunum kaynaklı ölüm:** \`${f1(x.solunum_olum_100k)} / yüz bin\` (~${trNum(x.solunum_olum, 0)} ölüm, kaba hız)`,
      "",
      `[${x.il} karnesinin tamamı](/sehir-karnesi/?il=${encodeURIComponent(x.il)})`,
    ].join("\n");
  }

  // En kirli
  if (has(p, ["kirli", "riskli", "kotu", "tehlikeli", "en yuksek"])) {
    const top = sortBy("pm25", true).slice(0, 3);
    return ["🚨 **PM2.5 değeri en yüksek 3 il (CAMS 2025):**", "",
      ...top.map((x, i) => `${i + 1}. **${x.il}** (${x.bolge}): \`${f1(x.pm25)} µg/m³\` · DSÖ kılavuzunun **${f1(x.pm25 / 5)} katı** · ${x.toplam_osb} OSB`)].join("\n");
  }

  // En temiz
  if (has(p, ["temiz", "iyi", "ferah", "en dusuk", "saglikli"])) {
    const top = sortBy("pm25", false).slice(0, 3);
    return ["🌿 **PM2.5 değeri en düşük 3 il (CAMS 2025):**", "",
      ...top.map((x, i) => `${i + 1}. **${x.il}** (${x.bolge}): \`${f1(x.pm25)} µg/m³\` · DSÖ kılavuzunun **${f1(x.pm25 / 5)} katı**`)].join("\n");
  }

  return [
    "Sorunuzu verilerle eşleştiremedim. Şu kalıplarla soru sorabilirsiniz:",
    "",
    ...QUICK_QUESTIONS.map((q) => `- *${q.prompt}*`),
    "- *Bursa il profili* veya *Iğdır hava kalitesi*",
  ].join("\n");
}
