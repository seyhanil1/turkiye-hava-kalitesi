import type { ReactNode } from "react";
import type { Tier } from "@/lib/data";

export function PageHeader({ title, subtitle, eyebrow }: { title: string; subtitle?: ReactNode; eyebrow?: string }) {
  return (
    <header className="mb-6">
      {eyebrow && (
        <span className="mb-2 inline-block rounded-md border border-accent/30 bg-accent/10 px-2.5 py-1 text-[11px] font-bold tracking-wide text-accent">
          {eyebrow}
        </span>
      )}
      <h1 className="text-2xl font-extrabold tracking-tight text-white">{title}</h1>
      {subtitle && <p className="mt-1 text-sm text-ink-soft">{subtitle}</p>}
    </header>
  );
}

export function Card({ children, className = "", title, subtitle }: {
  children: ReactNode; className?: string; title?: ReactNode; subtitle?: ReactNode;
}) {
  return (
    <section className={`rounded-xl border border-line bg-panel p-4 sm:p-5 ${className}`}>
      {title && <h2 className="text-base font-bold text-white">{title}</h2>}
      {subtitle && <p className="mt-0.5 text-xs text-muted">{subtitle}</p>}
      {(title || subtitle) && <div className="mb-3" />}
      {children}
    </section>
  );
}

export function Stat({ label, value, sub, accent = "text-accent", title }: {
  label: ReactNode; value: ReactNode; sub?: ReactNode; accent?: string; title?: string;
}) {
  return (
    <div className="rounded-lg border border-line-soft bg-panel-2 p-3" title={title}>
      <div className="text-[11px] font-semibold uppercase tracking-wide text-muted">{label}</div>
      <div className={`mt-1 text-xl font-extrabold ${accent}`}>{value}</div>
      {sub && <div className="mt-0.5 text-[11px] text-ink-soft">{sub}</div>}
    </div>
  );
}

export function TierBadge({ tier, small = false }: { tier: Tier; small?: boolean }) {
  return (
    <span
      className={`inline-block whitespace-nowrap rounded-md border font-bold ${small ? "px-1.5 py-0.5 text-[10px]" : "px-2 py-0.5 text-xs"}`}
      style={{ color: tier.renk, background: tier.bg, borderColor: tier.border }}
    >
      {tier.etiket}
    </span>
  );
}

export function Note({ children, tone = "info" }: { children: ReactNode; tone?: "info" | "warn" }) {
  const border = tone === "warn" ? "border-l-amber-400" : "border-l-accent";
  return (
    <div className={`rounded-md border border-line border-l-4 ${border} bg-panel-2 px-4 py-3 text-[13px] leading-relaxed text-ink-soft`}>
      {children}
    </div>
  );
}

export function Pill({ children, color = "#00e5db" }: { children: ReactNode; color?: string }) {
  return (
    <span
      className="inline-block rounded-full border px-2.5 py-0.5 text-xs font-semibold"
      style={{ color, borderColor: `${color}66`, background: `${color}1f` }}
    >
      {children}
    </span>
  );
}

export function SourceNote({ children }: { children: ReactNode }) {
  return <p className="mt-2 text-[11.5px] leading-relaxed text-muted">{children}</p>;
}
