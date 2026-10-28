import type { Metadata } from "next";
import { Suspense } from "react";
import { Card, Note, PageHeader, Stat } from "@/components/ui";
import { provinces, stats } from "@/lib/data";
import { trNum } from "@/lib/format";
import GroupSelector, { Chips } from "./Groups";

export const metadata: Metadata = { title: "İl Grupları" };

export default function GroupsPage() {
  const q = stats.quantiles;
  const count = (k: string) => provinces.filter((p) => p.kategori === k).length;
  const rest = provinces.length - count("A") - count("B");

  return (
    <>
      <PageHeader
        title="İl Grupları"
        subtitle="81 ilin OSB sayısı ve PM2.5 değerine göre çeyreklik (Q1/Q3) gruplaması."
      />

      <div className="mb-5 grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Stat label="OSB sayısı eşikleri" value={`Q1: ${trNum(q.q1_osb, 0)} | Q3: ${trNum(q.q3_osb, 0)}`} sub={`Alt %25 ≤ ${trNum(q.q1_osb, 0)} · Üst %25 ≥ ${trNum(q.q3_osb, 0)}`} accent="text-accent-2" />
        <Stat label="PM2.5 eşikleri" value={`Q1: ${trNum(q.q1_pm25, 1)} | Q3: ${trNum(q.q3_pm25, 1)}`} sub="µg/m³ (CAMS 2025)" />
        <Stat label="Kategori A" value={`${count("A")} il`} sub="Düşük OSB, yüksek PM2.5" accent="text-amber-400" />
        <Stat label="Kategori B" value={`${count("B")} il`} sub="Yüksek OSB, yüksek PM2.5" accent="text-red-400" />
      </div>

      <Card className="mb-5">
        <Suspense fallback={<div className="h-16 animate-pulse rounded-lg bg-panel-2" />}>
          <GroupSelector />
        </Suspense>
      </Card>

      <div className="mb-5 grid gap-5 lg:grid-cols-2">
        <Card
          title={`Kategori A: Düşük OSB, yüksek PM2.5 (${count("A")} il)`}
          subtitle={`OSB sayısı ≤ ${trNum(q.q1_osb, 0)} (alt %25) ve PM2.5 ≥ ${trNum(q.q3_pm25, 1)} µg/m³ (üst %25)`}
        >
          <Chips kategori="A" />
        </Card>
        <Card
          title={`Kategori B: Yüksek OSB, yüksek PM2.5 (${count("B")} il)`}
          subtitle={`OSB sayısı ≥ ${trNum(q.q3_osb, 0)} (üst %25) ve PM2.5 ≥ ${trNum(q.q3_pm25, 1)} µg/m³ (üst %25)`}
        >
          <Chips kategori="B" />
        </Card>
        <Card
          title={`Yüksek kirlilik / orta sanayi (${count("YK")} il)`}
          subtitle={`PM2.5 ≥ ${trNum(q.q3_pm25, 1)} µg/m³, OSB sayısı orta aralıkta`}
          className="lg:col-span-2"
        >
          <Chips kategori="YK" />
        </Card>
      </div>

      <Note>
        A ve B dışında kalan {rest} il, uç çeyreklik eşiklerinin dışında kalan orta segmenttedir. Gruplama betimleyicidir;
        nedensellik veya gelecek tahmini içermez. PM2.5 değerleri CAMS 2025 yıllık model ortalamasıdır.
      </Note>
    </>
  );
}
