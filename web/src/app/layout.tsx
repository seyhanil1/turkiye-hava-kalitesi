import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import Sidebar from "@/components/Sidebar";
import { meta } from "@/lib/data";
import "./globals.css";

const jakarta = Plus_Jakarta_Sans({
  variable: "--font-jakarta",
  subsets: ["latin", "latin-ext"],
});

export const metadata: Metadata = {
  title: {
    default: "HavaAtlası | Türkiye Hava Kalitesi",
    template: "%s | HavaAtlası",
  },
  description:
    "Türkiye'nin 81 ili için PM2.5 hava kalitesi (Copernicus CAMS), Kara Rapor istasyon ölçümleri, OSB envanteri ve TÜİK sağlık istatistikleri.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  const period = `Yıllık: CAMS ${meta.cams_year} (12 ay) · Günlük: ${meta.daily_start} – ${meta.daily_end}`;
  return (
    <html lang="tr" className={`${jakarta.variable} h-full antialiased`}>
      <body className="min-h-full">
        <div className="flex min-h-screen flex-col lg:flex-row">
          <Sidebar period={period} />
          <main className="min-w-0 flex-1 px-4 py-6 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-7xl">{children}</div>
            <footer className="mx-auto mt-12 max-w-7xl border-t border-line pt-4 text-[11.5px] leading-relaxed text-muted">
              PM2.5 değerleri istasyon ölçümü değil, Copernicus CAMS model tahminidir ve yerel kirliliği düşük gösterebilir.
              Veriler son olarak {meta.generated_at.slice(0, 10)} tarihinde güncellendi. Kaynaklar: Copernicus CAMS / Open-Meteo,
              Temiz Hava Hakkı Platformu Kara Rapor 2025, TÜİK, OSBÜK, DSÖ 2021.
            </footer>
          </main>
        </div>
      </body>
    </html>
  );
}
