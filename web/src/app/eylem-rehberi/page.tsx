import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Note, PageHeader } from "@/components/ui";

export const metadata: Metadata = { title: "Eylem Rehberi" };

const CARDS: { no: string; title: string; tag: string; items: ReactNode[] }[] = [
  {
    no: "01", title: "Bireysel maruziyetin azaltılması ve zamanlama", tag: "Bireysel korunma",
    items: [
      <>Kirliliğin arttığı <strong>sabah ve akşam iş/okul çıkışı saatlerinde</strong> dışarıda ağır fiziksel aktiviteden (koşu, antrenman) kaçının.</>,
      <>PM2.5 düzeyinin <strong>&apos;Yüksek&apos;, &apos;Çok Yüksek&apos; veya &apos;Kritik&apos;</strong> olduğu dönemlerde dışarı çıkması gereken risk grupları (yaşlılar, çocuklar, solunum hastaları) cerrahi maske yerine partikül tutucu <strong>FFP2/N95 maske</strong> tercih etmelidir.</>,
    ],
  },
  {
    no: "02", title: "İç mekân hava kalitesinin korunması", tag: "Yaşam alanı",
    items: [
      <>Dış ortam kirliliği yüksekken pencereleri uzun süre açık tutmayın; havalandırmayı kirliliğin görece düşük olduğu <strong>öğle saatlerinde kısa süreli</strong> yapın.</>,
      <>Yaşam alanlarında <strong>HEPA filtreli hava temizleyiciler</strong> kullanın; tütün dumanı, tütsü ve kimyasal oda kokusu gibi iç mekân partikül kaynaklarından kaçının.</>,
    ],
  },
  {
    no: "03", title: "Ulaşım tercihlerinin dönüştürülmesi", tag: "Ulaşım ve emisyon",
    items: [
      <>Bireysel araç yerine <strong>raylı sistem ve toplu taşıma</strong> kullanın; kısa mesafelerde yürüyüş ve bisikleti tercih edin.</>,
      <>Araçlarda uzun süre <strong>rölantide beklemekten</strong> kaçının; periyodik <strong>egzoz emisyon ölçümlerini</strong> ve bakımları aksatmayın.</>,
    ],
  },
  {
    no: "04", title: "Isınmada temiz enerji ve bina yalıtımı", tag: "Enerji ve ısınma",
    items: [
      <>Katı yakıt (kalitesiz kömür, linyit, biyokütle) yerine <strong>doğal gaz veya ısı pompası</strong> gibi düşük emisyonlu sistemlere geçin.</>,
      <>Binalarda <strong>çift cam ve ısı yalıtımı (mantolama)</strong> ile enerji ihtiyacını azaltın; baca ve kazan bakımlarını kış öncesi yaptırın.</>,
    ],
  },
  {
    no: "05", title: "Sanayi ve tarımsal emisyonların önlenmesi", tag: "Sektörel önlemler",
    items: [
      <>Tarım alanlarında <strong>anız yakılmamalıdır</strong>; anız yangınları atmosfere yoğun miktarda ince partikül ve zehirli gaz salar.</>,
      <>Sanayi tesislerinde, OSB&apos;lerde ve taş ocaklarında <strong>toz bastırma sistemleri ve baca filtreleri</strong> kesintisiz ve denetimli çalıştırılmalıdır.</>,
    ],
  },
  {
    no: "06", title: "Veri takibi ve erken uyarı", tag: "Karar desteği",
    items: [
      <>Dış mekân planlarından önce <strong>Çevre, Şehircilik ve İklim Değişikliği Bakanlığı&apos;nın istasyon ölçümlerini</strong> (sim.csb.gov.tr) kontrol edin. Bu sitedeki CAMS değerleri yıllık ve günlük model tahminidir, anlık uyarı için uygun değildir.</>,
      <>Kirlilik eşikleri aşıldığında yerel yönetimlerin ve valiliklerin <strong>hava kalitesi uyarılarına</strong> uyun.</>,
    ],
  },
];

export default function ActionGuidePage() {
  return (
    <>
      <PageHeader
        eyebrow="REHBER · EYLEM PLANI"
        title="Hava Kirliliğine Karşı Eylem Rehberi"
        subtitle="Bireysel korunma ve emisyon azaltımı için DSÖ 2021 Küresel Hava Kalitesi Kılavuzu'na dayalı pratik adımlar."
      />
      <div className="mb-5">
        <Note>
          <strong>Çift yönlü mücadele:</strong> Hava kirliliğiyle mücadele yalnızca bireysel korunmayı değil, kaynağında emisyon
          azaltımını da gerektirir.
        </Note>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {CARDS.map((c) => (
          <section key={c.no} className="rounded-xl border border-line bg-panel p-5">
            <div className="mb-3 flex items-start justify-between gap-3">
              <div className="flex items-center gap-3">
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-accent/30 bg-accent/10 font-mono text-sm font-bold text-accent">
                  {c.no}
                </span>
                <h2 className="text-base font-bold text-white">{c.title}</h2>
              </div>
              <span className="shrink-0 rounded-md border border-line px-2 py-0.5 text-[10px] font-semibold text-muted">{c.tag}</span>
            </div>
            <ul className="list-disc space-y-2 pl-5 text-[13.5px] leading-relaxed text-ink-soft">
              {c.items.map((item, i) => <li key={i}>{item}</li>)}
            </ul>
          </section>
        ))}
      </div>
      <p className="mt-6 text-xs text-muted">
        Bilgilendirme amaçlıdır, tıbbi tavsiye değildir. Akut solunum veya kalp-damar şikâyetlerinde en yakın sağlık kuruluşuna başvurun.
      </p>
    </>
  );
}
