import type { Metadata } from "next";
import { Suspense } from "react";
import { PageHeader } from "@/components/ui";
import ReportCard from "./ReportCard";

export const metadata: Metadata = { title: "Şehir Karnesi" };

export default function ReportCardPage() {
  return (
    <>
      <PageHeader
        title="Şehir Karnesi"
        subtitle="Her ilin hava kalitesi, sanayi ve solunum sağlığı göstergeleri."
      />
      <Suspense fallback={<div className="h-96 animate-pulse rounded-xl bg-panel" />}>
        <ReportCard />
      </Suspense>
    </>
  );
}
