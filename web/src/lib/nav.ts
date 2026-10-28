export interface NavPage {
  href: string;
  label: string;
}

export const NAV: { category: string; pages: NavPage[] }[] = [
  {
    category: "Keşfet",
    pages: [
      { href: "/", label: "Genel Bakış" },
      { href: "/sehir-karnesi/", label: "Şehir Karnesi" },
      { href: "/duello/", label: "Düello" },
    ],
  },
  {
    category: "Analiz",
    pages: [
      { href: "/bolgeler/", label: "Bölgeler" },
      { href: "/korelasyon/", label: "Korelasyon" },
      { href: "/sanayi/", label: "Sanayi Profili" },
      { href: "/il-gruplari/", label: "İl Grupları" },
    ],
  },
  {
    category: "Rehber",
    pages: [
      { href: "/eylem-rehberi/", label: "Eylem Rehberi" },
      { href: "/sozluk/", label: "Terimler Sözlüğü" },
      { href: "/asistan/", label: "Veri Asistanı" },
      { href: "/yontem/", label: "Veri ve Yöntem" },
      { href: "/surum-notlari/", label: "Sürüm Notları" },
    ],
  },
];
