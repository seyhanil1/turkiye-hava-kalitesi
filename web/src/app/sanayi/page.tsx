import type { Metadata } from "next";
import { Card, Note, PageHeader, Stat } from "@/components/ui";
import { byName, provinces, stats } from "@/lib/data";
import { trNum, trSign } from "@/lib/format";
import IndustryChart from "./IndustryChart";
import IndustryTable from "./IndustryTable";

export const metadata: Metadata = { title: "Sanayi Profili" };

export default function IndustryPage() {
  const total = provinces.reduce((a, p) => a + p.toplam_osb, 0);
  const faal = provinces.reduce((a, p) => a + p.faal_osb, 0);
  const area = provinces.reduce((a, p) => a + p.osb_alani_hektar, 0);
  const top = [...provinces].sort((a, b) => b.toplam_osb - a.toplam_osb).slice(0, 5);
  const topMean = top.reduce((a, p) => a + p.pm25, 0) / top.length;
  const allMean = provinces.reduce((a, p) => a + p.pm25, 0) / provinces.length;
  const marmara = stats.regions.rows.find((r) => r.bolge === "Marmara");
  const gaziantep = byName["Gaziantep"];
  const c = stats.correlation;

  return (
    <>
      <PageHeader
        eyebrow="OSB ENVANTERİ · OSBÜK"
        title="Sanayi Profili ve OSB Dağılımı"
        subtitle="OSBÜK (Ekim 2026) kayıtlarına göre organize sanayi bölgeleri ve illerin PM2.5 düzeyleri."
      />

      <div className="mb-5 grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Stat label="Toplam OSB" value={`${total} adet`} sub="81 ilde faal ve planlama aşamasında" />
        <Stat label="Faal OSB" value={`${faal} adet`} sub={`Toplamın %${trNum((faal / total) * 100, 1)} kadarı`} accent="text-amber-300" />
        <Stat label="Planlama / altyapı" value={`${total - faal} adet`} sub="Henüz faal olmayan" accent="text-accent-2" />
        <Stat label="Toplam OSB alanı" value={`${trNum(area, 0)} ha`} sub="OSBÜK envanteri" accent="text-ink" />
      </div>

      <div className="mb-5 grid gap-5 lg:grid-cols-[1.4fr_1fr]">
        <Card title="Bölgelere göre OSB sayısı" subtitle="Çubuk metni: OSB sayısı · bölge PM2.5 ortalaması · Türkiye içindeki payı">
          <IndustryChart />
        </Card>
        <div className="flex flex-col gap-4">
          <Card title="Marmara">
            <p className="text-sm text-ink-soft">
              Marmara bölgesinde {marmara?.toplam_osb} OSB ({marmara?.faal_osb} faal) bulunuyor; en yoğun sanayi kümelenmesi bu
              bölgede. Bölge PM2.5 ortalaması {trNum(marmara?.ortalama ?? 0, 1)} µg/m³.
            </p>
          </Card>
          <Card title="Güneydoğu Anadolu">
            <p className="text-sm text-ink-soft">
              Gaziantep {gaziantep.toplam_osb} OSB ile bölgenin en büyük sanayi altyapısına sahip ili; CAMS 2025 yıllık PM2.5
              ortalaması {trNum(gaziantep.pm25, 1)} µg/m³. Kara Rapor 2025&apos;te Gaziantep-Beydilli istasyonu 36,4 µg/m³ ölçmüş.
            </p>
          </Card>
          <Card title="En çok OSB'li 5 il">
            <p className="text-sm text-ink-soft">
              {top.map((p) => p.il).join(", ")}: ortalama PM2.5 {trNum(topMean, 1)} µg/m³ (81 il ortalaması {trNum(allMean, 1)}).
              Bu iller aynı zamanda kalabalık büyükşehirler olduğu için fark sanayiye tek başına bağlanamaz.
            </p>
          </Card>
        </div>
      </div>

      <div className="mb-5">
        <Note>
          OSB alanı ile PM2.5 arasında Spearman ρ = {trSign(c.osb_pm25.spearman_rho, 2)}; ancak nüfus ve rakım hesaba katılan çoklu
          regresyonda OSB sayısının katsayısı{" "}
          {c.ols.terms[1].p < 0.05 ? "anlamlı kalıyor" : "istatistiksel olarak anlamlı değil"} (p = {trNum(c.ols.terms[1].p, 3)}).
          Ayrıntılar Korelasyon sayfasında.
        </Note>
      </div>

      <Card title="81 il OSB tablosu" subtitle="Sütun başlığına tıklayarak sıralayın">
        <IndustryTable />
      </Card>
    </>
  );
}
