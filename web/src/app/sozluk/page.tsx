import type { Metadata } from "next";
import { PageHeader, SourceNote } from "@/components/ui";
import Glossary from "./Glossary";

export const metadata: Metadata = { title: "Terimler Sözlüğü" };

export default function GlossaryPage() {
  return (
    <>
      <PageHeader
        eyebrow="METODOLOJİ · REFERANS"
        title="Hava Kalitesi ve Çevre Sözlüğü"
        subtitle="Platformda kullanılan teknik terimler, kirletici tanımları ve DSÖ standartları."
      />
      <Glossary />
      <SourceNote>
        Kaynaklar: WHO Global Air Quality Guidelines (2021); ECMWF CAMS belgeleri; Çevre, Şehircilik ve İklim Değişikliği Bakanlığı
        Hava Kalitesi Değerlendirme ve Yönetimi Yönetmeliği; Temiz Hava Hakkı Platformu Kara Rapor 2025.
      </SourceNote>
    </>
  );
}
