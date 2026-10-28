"use client";

import CitySelect, { useCityParam } from "@/components/CitySelect";
import { CityCompareChart, DailySeriesChart } from "@/components/charts";
import { Card, Note, Stat, TierBadge } from "@/components/ui";
import { byName, meta, regionMean, tierOf } from "@/lib/data";
import { roundDisp, trNum, trSign } from "@/lib/format";

export default function ReportCard() {
  const [il, setIl] = useCityParam();
  const p = byName[il];
  const tier = tierOf(p.pm25);
  const bolgeFark = roundDisp(roundDisp(p.pm25) - roundDisp(regionMean(p.bolge)));

  return (
    <>
      <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
        <CitySelect id="report-city" label="İl seçimi" value={il} onChange={setIl} />
        <div className="text-right">
          <div className="text-xs text-muted">Coğrafi bölge &amp; plaka</div>
          <div className="text-base font-bold text-accent-2">{p.bolge} · Plaka {String(p.plaka).padStart(2, "0")}</div>
        </div>
      </div>

      <div className="mb-3 grid gap-3 sm:grid-cols-3">
        <Stat
          label={`PM2.5 yıllık ort. (CAMS 2025 model)`}
          value={<>{trNum(p.pm25, 1)} <span className="text-sm text-muted">µg/m³</span></>}
          sub={`${trSign(bolgeFark, 1)} µg/m³ (bölge ortalamasına göre)`}
          accent="text-white"
        />
        <Stat
          label="Kirlilik kademesi"
          value={<TierBadge tier={tier} />}
          sub={`DSÖ kılavuzunun (5 µg/m³) ${trNum(p.dso_limit_kat, 1)} katı`}
        />
        <Stat
          label="Solunum ölüm oranı"
          value={<>{trNum(p.solunum_olum_100k, 1)} <span className="text-sm text-muted">yüz binde</span></>}
          sub={`TÜİK ${meta.olum_yili} · Kaba hız, yaşa göre düzeltilmemiş`}
          accent="text-white"
        />
      </div>

      <div className="mb-5 grid gap-3 sm:grid-cols-3">
        <Stat
          label="Solunum ölümlerinin payı"
          value={`%${trNum(p.solunum_olum_payi, 1)}`}
          sub="Tüm ölümler içinde; yaş yapısını kısmen dengeler"
          accent="text-accent-2"
        />
        <Stat
          label="PM2.5'e atfedilebilir ölüm"
          value={`~${trNum(p.atfedilen_olum_tahmini, 0)}`}
          sub={`AirQ+ yaklaşık tahmin · tüm ölümler içindeki pay: %${trNum(p.atfedilen_olum_payi, 1)}`}
          accent="text-accent-2"
        />
        <Stat
          label="Kara Rapor istasyonu (2024)"
          value={p.pm25_istasyon_max_2024 === null ? "—" : <>{trNum(p.pm25_istasyon_max_2024, 1)} <span className="text-sm text-muted">µg/m³</span></>}
          sub={p.pm25_istasyon_max_2024 === null
            ? "Bu il, raporun yayımladığı ilk 10 istasyon arasında değil"
            : "CAMS modeli bu ilde istasyon ölçümünün altında kalıyor"}
          accent="text-amber-300"
        />
      </div>

      <div className="mb-5 grid gap-5 lg:grid-cols-[1.3fr_1fr]">
        <Card title="Bölge ve Türkiye ortalamasıyla karşılaştırma">
          <CityCompareChart il={il} />
        </Card>
        <Card title="İl künyesi">
          <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 text-sm">
            <dt className="text-muted">Nüfus (ADNKS {meta.nufus_yili})</dt><dd className="text-white">{trNum(p.nufus, 0)} kişi</dd>
            <dt className="text-muted">Bölge</dt><dd className="text-white">{p.bolge}</dd>
            <dt className="text-muted">Plaka</dt><dd className="text-white">{String(p.plaka).padStart(2, "0")}</dd>
            <dt className="text-muted">Toplam OSB</dt><dd className="text-white">{p.toplam_osb} adet</dd>
            <dt className="text-muted">Faal OSB</dt>
            <dd className="text-white">
              {p.faal_osb} adet ({p.toplam_osb > 0 ? `%${trNum((p.faal_osb / p.toplam_osb) * 100, 1)}` : "—"})
            </dd>
            <dt className="text-muted">PM10 (CAMS 2025)</dt><dd className="text-white">{trNum(p.pm10_cams, 1)} µg/m³</dd>
            <dt className="text-muted">Rakım</dt><dd className="text-white">{p.rakim === null ? "—" : `${trNum(p.rakim, 0)} m`}</dd>
          </dl>
        </Card>
      </div>

      <Card title={`${il} il özeti`} className="mb-5">
        <ul className="list-disc space-y-1.5 pl-5 text-sm text-ink-soft">
          {p.ozet.map((s) => <li key={s}>{s}</li>)}
        </ul>
        <p className="mt-3 text-[11.5px] text-muted">
          Not: PM2.5 verileri Copernicus CAMS atmosferik modeline dayanmaktadır; kaba ölüm hızı yaş standardizasyonu içermez.
        </p>
      </Card>

      <Card title={`${il} — günlük PM2.5 (CAMS)`} subtitle="İl merkezindeki günlük model ortalaması" className="mb-5">
        <DailySeriesChart il={il} height={260} />
      </Card>

      <Note>
        Atfedilebilir ölüm tahmini, Kara Rapor 2025 ile aynı AirQ+ yöntemini (göreli risk 1,08 / 10 µg/m³, karşı-olgu 5 µg/m³)
        tüm yaşlardaki ölümlere uygular; kesin bir sayı değil, büyüklük mertebesi göstergesidir.
      </Note>
    </>
  );
}
