"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { NAV } from "@/lib/nav";

const SOURCES = [
  { label: "CAMS", title: "Copernicus CAMS atmosfer modeli (Open-Meteo) — ana PM2.5 kaynağı" },
  { label: "Kara Rapor", title: "Temiz Hava Hakkı Platformu, Kara Rapor 2025 (2024 istasyon verisi)" },
  { label: "TÜİK", title: "TÜİK ölüm ve nüfus istatistikleri" },
  { label: "OSBÜK", title: "OSB envanteri (Ekim 2026)" },
  { label: "DSÖ", title: "DSÖ 2021 Küresel Hava Kalitesi Kılavuzu" },
];

function isActive(pathname: string, href: string) {
  const norm = (p: string) => (p.endsWith("/") ? p : `${p}/`);
  return href === "/" ? pathname === "/" : norm(pathname) === href;
}

export default function Sidebar({ period }: { period: string }) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  const nav = (
    <nav className="flex flex-col gap-5" aria-label="Sayfalar">
      {NAV.map((group) => (
        <div key={group.category}>
          <div className="mb-1.5 px-2 text-[11px] font-bold uppercase tracking-wider text-muted">{group.category}</div>
          <ul className="flex flex-col gap-0.5">
            {group.pages.map((page) => {
              const active = isActive(pathname, page.href);
              return (
                <li key={page.href}>
                  <Link
                    href={page.href}
                    onClick={() => setOpen(false)}
                    aria-current={active ? "page" : undefined}
                    className={`block rounded-lg px-2.5 py-1.5 text-sm transition-colors ${
                      active
                        ? "border border-accent/40 bg-accent/10 font-semibold text-accent"
                        : "border border-transparent text-ink-soft hover:bg-white/5 hover:text-white"
                    }`}
                  >
                    {page.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      ))}
      <div>
        <div className="mb-1.5 px-2 text-[11px] font-bold uppercase tracking-wider text-muted">Veri Kaynakları</div>
        <div className="flex flex-wrap gap-1 px-2">
          {SOURCES.map((s) => (
            <span key={s.label} title={s.title} className="rounded border border-line bg-panel px-1.5 py-0.5 text-[10px] text-muted">
              {s.label}
            </span>
          ))}
        </div>
      </div>
    </nav>
  );

  return (
    <>
      {/* Mobil üst çubuk */}
      <div className="sticky top-0 z-30 flex items-center justify-between border-b border-line bg-bg/95 px-4 py-3 backdrop-blur lg:hidden">
        <Link href="/" className="text-lg font-extrabold text-white">
          Hava<span className="text-accent">Atlası</span>
        </Link>
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          aria-controls="mobile-nav"
          className="rounded-lg border border-line px-3 py-1.5 text-sm text-ink-soft"
        >
          {open ? "Kapat" : "Menü"}
        </button>
      </div>
      {open && (
        <div id="mobile-nav" className="border-b border-line bg-panel px-4 py-4 lg:hidden">
          {nav}
        </div>
      )}

      {/* Masaüstü kenar menüsü */}
      <aside className="sticky top-0 hidden h-screen w-60 shrink-0 flex-col gap-6 overflow-y-auto border-r border-line bg-[#021626] px-3 py-6 lg:flex">
        <Link href="/" className="px-2">
          <div className="text-xl font-extrabold text-white">
            Hava<span className="text-accent">Atlası</span>
          </div>
          <div className="mt-1 text-[11px] leading-snug text-muted">{period}</div>
        </Link>
        {nav}
      </aside>
    </>
  );
}
