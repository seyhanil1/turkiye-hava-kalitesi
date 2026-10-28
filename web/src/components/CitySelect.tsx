"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback } from "react";
import { byName, cityNames } from "@/lib/data";

/** URL'deki bir sorgu parametresini (varsayılan ?il=) geçerli il adıyla eşleştirir. */
export function useCityParam(key = "il", fallback = "İstanbul"): [string, (il: string) => void] {
  const params = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const raw = params.get(key);
  const city = raw && byName[raw] ? raw : fallback;

  const setCity = useCallback(
    (il: string) => {
      const next = new URLSearchParams(params.toString());
      next.set(key, il);
      router.replace(`${pathname}?${next.toString()}`, { scroll: false });
    },
    [params, router, pathname, key],
  );
  return [city, setCity];
}

export default function CitySelect({
  value, onChange, label, id, accent,
}: { value: string; onChange: (il: string) => void; label: string; id: string; accent?: string }) {
  return (
    <div>
      <label htmlFor={id} className="mb-1 block text-xs font-semibold text-muted">{label}</label>
      <select
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-lg border bg-panel-2 px-3 py-2 text-sm font-semibold text-white sm:w-72"
        style={{ borderColor: accent ?? "var(--border)" }}
      >
        {cityNames.map((c) => <option key={c} value={c}>{c}</option>)}
      </select>
    </div>
  );
}
