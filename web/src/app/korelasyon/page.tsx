import type { Metadata } from "next";
import { Card, Note, PageHeader, Stat } from "@/components/ui";
import { stats } from "@/lib/data";
import { trNum, trP, trSign } from "@/lib/format";
import { MoranChart, ScatterChart } from "./CorrelationCharts";

export const metadata: Metadata = { title: "Korelasyon ve Regresyon" };

function strength(r: number) {
  const a = Math.abs(r);
  const dir = r > 0 ? "pozitif" : "negatif";
  if (a < 0.1) return "İlişki yok denecek kadar zayıf";
  if (a < 0.3) return `Zayıf ${dir}`;
  if (a < 0.5) return `Orta düzeyde ${dir}`;
  return `Güçlü ${dir}`;
}

export default function CorrelationPage() {
  const c = stats.correlation;
  const biv = c.osb_pm25;
  const ols = c.ols;
  const significant = ols.terms.slice(1).filter((t) => t.p < 0.05).map((t) => t.name.replace(/ \(β.\)$/, ""));
  const moranSig = c.moran.p < 0.05 && c.moran.I > 0;

  return (
    <>
      <PageHeader
        title="Korelasyon ve Regresyon Analizi"
        subtitle="Sanayi, rakım ve nüfusun PM2.5 ile istatistiksel ve mekânsal ilişkisi."
      />

      <div className="mb-5">
        <Note tone="warn">
          <strong>Korelasyon nedensellik değildir.</strong> İl düzeyindeki ilişkiler (ekolojik korelasyon) bireysel maruziyete
          genellenemez. Örneklem: 81 il · PM2.5: CAMS 2025 yıllık model ortalaması.
        </Note>
      </div>

      <Card
        title="OSB alanı ile PM2.5 ilişkisi"
        subtitle="81 ilin hektar bazında OSB alanı ile yıllık ortalama PM2.5 arasındaki ilişki"
        className="mb-5"
      >
        <div className="mb-4 grid grid-cols-2 gap-3 lg:grid-cols-4">
          <Stat label="Spearman sıra korelasyonu" value={`ρ = ${trSign(biv.spearman_rho, 2)}`} sub={strength(biv.spearman_rho)} />
          <Stat
            label="Pearson korelasyonu"
            value={`r = ${trSign(biv.pearson_r, 2)}`}
            sub={biv.pearson_p < 0.05 ? "İstatistiksel olarak anlamlı" : "İstatistiksel olarak anlamlı değil"}
            accent="text-accent-2"
          />
          <Stat
            label="%95 bootstrap güven aralığı (ρ)"
            value={`[${trNum(biv.ci_lo, 2)}; ${trNum(biv.ci_hi, 2)}]`}
            sub="1.000 iterasyon"
            accent="text-amber-300"
          />
          <Stat label="Anlamlılık (Spearman)" value={trP(biv.spearman_p)} sub={`n = ${biv.n} il`} accent="text-emerald-400" />
        </div>
        <Note>
          <strong>Bulgular:</strong> OSB alanı ile PM2.5 arasında Spearman ρ = {trSign(biv.spearman_rho, 2)}. Ancak nüfus ile
          PM2.5 arasındaki ilişki de ρ = {trSign(c.nufus_pm25.spearman_rho, 2)} düzeyindedir: OSB&apos;si büyük iller aynı zamanda
          kalabalık büyükşehirlerdir. Tek değişkenli korelasyon sanayinin kendi etkisini nüfus, trafik ve ısınmadan ayıramaz;
          aşağıdaki çoklu regresyon bu etkenleri birlikte ele alır.
        </Note>
      </Card>

      <Card title="Etkileşimli saçılım grafiği" subtitle="PM2.5'in seçilen değişkene göre dağılımı ve doğrusal trend" className="mb-5">
        <ScatterChart />
      </Card>

      <Card
        title="Çoklu regresyon modeli (OLS)"
        subtitle="PM2.5 = β₀ + β₁(OSB) + β₂(Rakım) + β₃(Nüfus / 100 bin)"
        className="mb-5"
      >
        <div className="mb-4 grid gap-3 sm:grid-cols-3">
          <Stat label="Belirlilik katsayısı (R²)" value={`%${trNum(ols.r2 * 100, 1)}`} sub={`R² = ${trNum(ols.r2, 4)}`} />
          <Stat label="Düzeltilmiş R²" value={trSign(ols.adj_r2, 4)} sub="Serbestlik derecesi düzeltmesi" accent="text-accent-2" />
          <Stat label="Gözlem / değişken" value={`N = ${ols.n} (k = ${ols.k})`} sub={`Artık serbestlik derecesi = ${ols.df_resid}`} accent="text-amber-300" />
        </div>
        <div className="mb-4 overflow-x-auto">
          <table className="w-full min-w-[620px] text-sm">
            <thead className="text-left text-[11px] uppercase tracking-wide text-muted">
              <tr>
                <th className="py-2 pr-3 font-semibold">Değişken</th>
                <th className="py-2 pr-3 text-right font-semibold">Katsayı</th>
                <th className="py-2 pr-3 text-right font-semibold">Std. hata</th>
                <th className="py-2 pr-3 text-right font-semibold">t</th>
                <th className="py-2 pr-3 text-right font-semibold">p</th>
                <th className="py-2 font-semibold">Durum</th>
              </tr>
            </thead>
            <tbody>
              {ols.terms.map((t) => (
                <tr key={t.name} className="border-t border-line-soft">
                  <td className="py-2 pr-3 font-semibold text-white">{t.name}</td>
                  <td className="py-2 pr-3 text-right">{trSign(t.coef, 4)}</td>
                  <td className="py-2 pr-3 text-right">{trNum(t.se, 4)}</td>
                  <td className="py-2 pr-3 text-right">{trSign(t.t, 2)}</td>
                  <td className="py-2 pr-3 text-right">{t.p < 0.0001 ? "< 0,0001" : trNum(t.p, 4)}</td>
                  <td className={`py-2 ${t.p < 0.05 ? "text-emerald-400" : "text-muted"}`}>
                    {t.p < 0.05 ? "Anlamlı (p < 0,05)" : "Anlamsız (p ≥ 0,05)"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <Note>
          <strong>Yorum:</strong> Model, PM2.5 varyansının %{trNum(ols.r2 * 100, 1)} kadarını açıklıyor (düzeltilmiş R² ={" "}
          {trSign(ols.adj_r2, 4)}). Diğer değişkenler sabitken %5 düzeyinde anlamlı olan:{" "}
          <strong>{significant.length ? significant.join(", ") : "hiçbir bağımsız değişken"}</strong>. Model emisyon
          kaynaklarını (konut ısınması, trafik, termik santral) ve meteorolojiyi içermediğinden katsayılar nedensel etki olarak
          yorumlanmamalıdır.
        </Note>
      </Card>

      <Card
        title="Mekânsal otokorelasyon: Global Moran's I"
        subtitle="İl merkezleri arası ters mesafe ağırlık matrisi (satır standardize) ve 999 permütasyonlu test"
      >
        <div className="mb-3 flex flex-wrap items-center gap-3">
          <span className="rounded-md border border-accent/40 bg-accent/15 px-3 py-1 text-sm font-extrabold text-accent">
            Moran&apos;s I = {trSign(c.moran.I, 2)}, {trP(c.moran.p)}
          </span>
          <span className="text-sm text-ink-soft">
            {moranSig
              ? "Komşu iller benzer kirlilik düzeyine sahip; kirlilik coğrafi olarak kümeleniyor."
              : "Komşu illerin kirlilik düzeyleri rastgele dağılımdan istatistiksel olarak ayrışmıyor."}
          </span>
        </div>
        <MoranChart />
      </Card>
    </>
  );
}
