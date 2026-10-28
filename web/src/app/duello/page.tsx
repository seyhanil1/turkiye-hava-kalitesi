import type { Metadata } from "next";
import { Suspense } from "react";
import { PageHeader } from "@/components/ui";
import Duel from "./Duel";

export const metadata: Metadata = { title: "Şehir Düellosu" };

export default function DuelPage() {
  return (
    <>
      <PageHeader
        title="İki İl Kafa Kafaya"
        subtitle="İki ilin hava kalitesi, solunum sağlığı ve sanayi altyapısı göstergelerini karşılaştırın."
      />
      <Suspense fallback={<div className="h-96 animate-pulse rounded-xl bg-panel" />}>
        <Duel />
      </Suspense>
    </>
  );
}
