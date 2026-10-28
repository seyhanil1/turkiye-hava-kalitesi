import type { Metadata } from "next";
import { PageHeader } from "@/components/ui";
import Chat from "./Chat";

export const metadata: Metadata = { title: "Veri Asistanı" };

export default function AssistantPage() {
  return (
    <>
      <PageHeader
        eyebrow="KURAL TABANLI · TARAYICIDA ÇALIŞIR"
        title="Veri Asistanı"
        subtitle="Sorularınızı platformdaki 81 il verisiyle yanıtlar. Yanıtlar önceden tanımlı kurallarla üretilir; yapay zeka modeli kullanılmaz."
      />
      <Chat />
    </>
  );
}
