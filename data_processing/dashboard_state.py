"""
Merkezi Dashboard Veri Durumu (Single Source of Truth)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

Akış:
    veri kaynakları → temizleme → ortak model (DashboardData)
        → filtre durumu (FilterState, URL parametrelerinden)
        → build_view() → KPI, harita, sıralama, zaman serisi, veri bilimi notu

Bütün paneller aynı `DashboardView` nesnesinden beslenir; böylece aynı filtre
altında aynı il için farklı panellerde çelişkili değer gösterilmez.
Eksik değerler (NaN) asla sıfır kabul edilmez.
"""

from __future__ import annotations

import math
import unicodedata
from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from typing import Optional
from urllib.parse import urlencode

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Sabitler
# ---------------------------------------------------------------------------
PAGES = {
    "genel_bakis": "Genel Bakış",
    "sehir_karnesi": "Şehir Karnesi",
    "duello": "Düello",
    "korelasyon": "Korelasyon",
    "bolgeler": "Bölgeler",
    "yesil_donusum": "Yeşil Dönüşüm",
    "sanayi_profili": "Sanayi Profili",
    "ekonomi": "Ekonomi",
    # Menü dışı analiz sayfaları (kartlar / butonlar ile açılır)
    "analiz": "Veri Bilimi Analizi",
    "veri_kapsami": "Veri Kapsamı ve Kalitesi",
    "dso": "DSÖ Sınırları",
}

POLLUTANTS = {
    "pm25": {"label": "PM2.5", "unit": "µg/m³", "who_annual": 5.0, "who_24h": 15.0,
             # DSÖ 2021 yıllık kılavuz + ara hedefler (IT-4 … IT-1)
             "breaks": [5, 10, 15, 25, 35]},
    "pm10": {"label": "PM10", "unit": "µg/m³", "who_annual": 15.0, "who_24h": 45.0,
             "breaks": [15, 20, 30, 50, 70]},
    "no2": {"label": "NO₂", "unit": "µg/m³", "who_annual": 10.0, "who_24h": 25.0,
            "breaks": [10, 20, 30, 40, 60]},
}

CATEGORIES = [
    ("DSÖ kılavuzu altında", "#10e3a0"),
    ("Düşük", "#7ee05a"),
    ("Orta", "#f5d40f"),
    ("Yüksek", "#fb9a2c"),
    ("Çok yüksek", "#f4553c"),
    ("Aşırı", "#c0265c"),
]
NO_DATA_COLOR = "#2b3c52"

SOURCES = {
    "resmi": "Resmî istasyon ölçümü · 2025 yıllık ortalama (Kara Rapor)",
    "cams": "CAMS atmosfer modeli · il merkezi günlük ortalama",
}

REGIONS = ["Marmara", "Ege", "Akdeniz", "İç Anadolu", "Karadeniz",
           "Doğu Anadolu", "Güneydoğu Anadolu"]
DEFAULT_REGION = "Türkiye"
PERIODS = {"7": 7, "30": 30, "90": 90}
TOP_OPTIONS = ("10", "20", "all")
SORT_OPTIONS = ("desc", "asc", "name")


def tr_lower(text: str) -> str:
    """Türkçe kurallarına uygun küçük harf (İ→i, I→ı)."""
    return str(text).replace("İ", "i").replace("I", "ı").lower()


def tr_fold(text: str) -> str:
    """Arama için Türkçe karakterleri sadeleştirir (ş→s, ı→i …)."""
    t = tr_lower(text)
    t = t.translate(str.maketrans("çğıöşü", "cgiosu"))
    return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()


def search_provinces(query: str, provinces: list[str], limit: int = 8) -> list[str]:
    """Büyük/küçük harf ve Türkçe karakter duyarsız il araması (önek eşleşmesi önce)."""
    q = tr_fold(query.strip())
    if not q:
        return []
    starts = [p for p in provinces if tr_fold(p).startswith(q)]
    contains = [p for p in provinces if q in tr_fold(p) and p not in starts]
    return (sorted(starts, key=tr_fold) + sorted(contains, key=tr_fold))[:limit]


def category_index(value: float, pollutant: str) -> Optional[int]:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    for i, b in enumerate(POLLUTANTS[pollutant]["breaks"]):
        if value <= b:
            return i
    return len(CATEGORIES) - 1


def fmt_num(value: Optional[float], digits: int = 1) -> str:
    """Türkçe ondalık biçimi (36,3). Eksik veri için '—'."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "—"
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ---------------------------------------------------------------------------
# Veri modeli
# ---------------------------------------------------------------------------
@dataclass
class DashboardData:
    master: pd.DataFrame                    # 81 il yıllık resmi veri + sanayi + sağlık
    city_daily: Optional[pd.DataFrame]      # il bazlı günlük CAMS (date, il, pm25, pm10, no2)
    messages: list = field(default_factory=list)   # [(seviye, metin)]
    master_updated: Optional[str] = None
    cams_updated: Optional[str] = None

    @property
    def provinces(self) -> list[str]:
        return sorted(self.master["il"].tolist(), key=tr_fold)

    @property
    def date_bounds(self) -> Optional[tuple[date, date]]:
        if self.city_daily is None or self.city_daily.empty:
            return None
        return (self.city_daily["date"].min().date(), self.city_daily["date"].max().date())


@dataclass
class FilterState:
    page: str = "genel_bakis"
    pollutant: str = "pm25"
    source: str = "resmi"
    region: str = DEFAULT_REGION
    period: str = "30"
    start: Optional[date] = None
    end: Optional[date] = None
    top: str = "10"
    sort: str = "desc"
    city: Optional[str] = None
    errors: list = field(default_factory=list)

    def to_params(self, **overrides) -> dict:
        s = replace(self, **overrides) if overrides else self
        params = {"page": s.page}
        if s.pollutant != "pm25":
            params["kirletici"] = s.pollutant
        if s.source != "resmi":
            params["kaynak"] = s.source
        if s.region != DEFAULT_REGION:
            params["bolge"] = s.region
        if s.period == "custom" and s.start and s.end:
            params["baslangic"] = s.start.isoformat()
            params["bitis"] = s.end.isoformat()
        elif s.period != "30":
            params["donem"] = s.period
        if s.top != "10":
            params["ilk"] = s.top
        if s.sort != "desc":
            params["sirala"] = s.sort
        if s.city:
            params["il"] = s.city
        return params

    def href(self, **overrides) -> str:
        return "?" + urlencode(self.to_params(**overrides))


def _parse_date(raw: Optional[str]) -> Optional[date]:
    if not raw:
        return None
    try:
        return date.fromisoformat(str(raw)[:10])
    except ValueError:
        return None


def parse_state(params: dict, data: DashboardData) -> FilterState:
    """URL parametrelerini doğrular; geçersiz değerlerde varsayılana döner ve hatayı kaydeder."""
    get = lambda k: (params.get(k) or "").strip() if isinstance(params.get(k), str) else params.get(k)
    st = FilterState()
    errors: list[str] = []

    page = get("page") or "genel_bakis"
    st.page = page if page in PAGES else "genel_bakis"
    if page not in PAGES:
        errors.append(f"'{page}' adlı sayfa bulunamadı; Genel Bakış açıldı.")

    pol = get("kirletici") or "pm25"
    st.pollutant = pol if pol in POLLUTANTS else "pm25"

    src = get("kaynak") or "resmi"
    st.source = src if src in SOURCES else "resmi"
    if st.source == "cams" and data.date_bounds is None:
        errors.append("CAMS günlük verisi bulunamadı; resmî yıllık veriye geçildi.")
        st.source = "resmi"

    reg = get("bolge") or DEFAULT_REGION
    st.region = reg if reg in REGIONS else DEFAULT_REGION

    st.top = get("ilk") if get("ilk") in TOP_OPTIONS else "10"
    st.sort = get("sirala") if get("sirala") in SORT_OPTIONS else "desc"

    city = get("il")
    if city:
        if city in set(data.master["il"]):
            st.city = city
        else:
            errors.append(f"'{city}' veri setinde bulunan bir il değil.")

    bounds = data.date_bounds
    if bounds:
        lo, hi = bounds
        start, end = _parse_date(get("baslangic")), _parse_date(get("bitis"))
        if get("baslangic") or get("bitis"):
            if not (start and end):
                errors.append("Tarih biçimi geçersiz; son 30 gün kullanıldı.")
                st.period = "30"
            elif start > end:
                errors.append("Başlangıç tarihi bitiş tarihinden sonra olamaz; son 30 gün kullanıldı.")
                st.period = "30"
            else:
                c_start, c_end = max(start, lo), min(end, hi)
                if c_start > c_end:
                    errors.append(
                        f"Seçilen aralıkta veri yok. Mevcut veri: {lo:%d.%m.%Y} – {hi:%d.%m.%Y}.")
                    st.period, st.start, st.end = "custom", start, end
                else:
                    if (c_start, c_end) != (start, end):
                        errors.append(f"Tarih aralığı mevcut veriye göre {c_start:%d.%m.%Y} – "
                                      f"{c_end:%d.%m.%Y} olarak sınırlandı.")
                    st.period, st.start, st.end = "custom", c_start, c_end
        if st.period != "custom":
            per = get("donem") or st.period
            st.period = per if per in PERIODS else "30"
            st.end = hi
            st.start = max(lo, hi - timedelta(days=PERIODS[st.period] - 1))
    st.errors = errors
    return st


# ---------------------------------------------------------------------------
# Görünüm hesaplama
# ---------------------------------------------------------------------------
@dataclass
class DashboardView:
    state: FilterState
    pollutant_label: str
    unit: str
    source_label: str
    scope_label: str
    period_label: str
    cities: pd.DataFrame                 # il, bolge, plaka, lat, lon, value, n_days, cat
    kpi: dict
    ranking: pd.DataFrame
    series: pd.DataFrame                 # date, value, n
    series_label: str
    note: dict
    warnings: list


def _scope_master(data: DashboardData, state: FilterState) -> pd.DataFrame:
    df = data.master
    if state.region != DEFAULT_REGION:
        df = df[df["bolge"] == state.region]
    return df


def _cams_window(data: DashboardData, start: date, end: date, ils) -> pd.DataFrame:
    cd = data.city_daily
    if cd is None:
        return pd.DataFrame(columns=["date", "il", "pm25", "pm10", "no2"])
    mask = (cd["date"].dt.date >= start) & (cd["date"].dt.date <= end) & cd["il"].isin(ils)
    return cd[mask]


def build_view(data: DashboardData, state: FilterState) -> DashboardView:
    pol = state.pollutant
    meta = POLLUTANTS[pol]
    warnings = list(state.errors)
    scope = _scope_master(data, state)
    ils = scope["il"].tolist()

    base = scope[["il", "bolge", "plaka", "lat", "lon"]].copy()
    has_window = state.start is not None and state.end is not None
    window = _cams_window(data, state.start, state.end, ils) if has_window else pd.DataFrame()

    if state.source == "resmi":
        base["value"] = pd.to_numeric(scope[pol], errors="coerce").values
        base["n_days"] = np.nan
    else:
        if window.empty:
            base["value"] = np.nan
            base["n_days"] = 0
            warnings.append("Seçilen tarih aralığında CAMS verisi bulunmuyor.")
        else:
            agg = window.groupby("il")[pol].agg(["mean", "count"])
            base["value"] = base["il"].map(agg["mean"]).round(2)
            base["n_days"] = base["il"].map(agg["count"]).fillna(0)
    base["cat"] = [category_index(v, pol) for v in base["value"]]

    valid = base.dropna(subset=["value"])
    n_total, n_valid = len(base), len(valid)

    # --- Zaman serisi (her zaman CAMS günlük; kapsamdaki illerin günlük ortalaması)
    if not window.empty:
        series = (window.groupby("date")[pol].agg(["mean", "count"]).reset_index()
                  .rename(columns={"mean": "value", "count": "n"}))
        series["value"] = series["value"].round(2)
    else:
        series = pd.DataFrame(columns=["date", "value", "n"])
    series_label = (f"CAMS model · {state.region} kapsamındaki {len(ils)} il merkezinin günlük ortalaması")

    # --- Önceki eşit uzunlukta dönem (değişim yüzdesi için)
    prev_mean = None
    cur_mean_cams = float(series["value"].mean()) if len(series) else None
    if has_window and len(series):
        span = (state.end - state.start).days + 1
        p_end = state.start - timedelta(days=1)
        p_start = p_end - timedelta(days=span - 1)
        prev = _cams_window(data, p_start, p_end, ils)
        if not prev.empty and prev["date"].nunique() >= max(1, span // 2):
            prev_mean = float(prev.groupby("date")[pol].mean().mean())

    def city_spark(il: str) -> list:
        if window.empty:
            return []
        s = window[window["il"] == il].sort_values("date")[pol]
        return [round(float(v), 2) for v in s.tolist()]

    # --- KPI'lar
    kpi: dict = {"n_total": n_total, "n_valid": n_valid,
                 "n_country": len(data.master)}
    if n_valid:
        mean_val = float(valid["value"].mean())
        mx = valid.loc[valid["value"].idxmax()]
        mn = valid.loc[valid["value"].idxmin()]
        kpi.update({
            "mean": mean_val,
            "who_ratio": mean_val / meta["who_annual"],
            "max_il": mx["il"], "max": float(mx["value"]),
            "min_il": mn["il"], "min": float(mn["value"]),
            "max_vs_mean": float(mx["value"]) - mean_val,
            "min_vs_mean": float(mn["value"]) - mean_val,
            "spark_mean": [round(float(v), 2) for v in series["value"].tolist()],
            "spark_max": city_spark(mx["il"]),
            "spark_min": city_spark(mn["il"]),
            "above_who": int((valid["value"] > meta["who_annual"]).sum()),
        })
    if state.source == "cams" and prev_mean and cur_mean_cams is not None:
        kpi["delta_pct"] = (cur_mean_cams - prev_mean) / prev_mean * 100

    # --- Sıralama
    if state.sort == "asc":
        ranking = valid.sort_values("value", ascending=True)
    elif state.sort == "name":
        ranking = valid.sort_values("il", key=lambda s: s.map(tr_fold))
    else:
        ranking = valid.sort_values("value", ascending=False)
    ranking = ranking.reset_index(drop=True)
    ranking["rank"] = valid["value"].rank(ascending=False, method="min").reindex(
        ranking.index).values if False else ranking["value"].rank(
        ascending=False, method="min").astype(int)
    if state.top != "all":
        ranking = ranking.head(int(state.top))

    note = build_science_note(data, state, base)

    if state.source == "resmi":
        period_label = "2025 yıllık ortalama"
    elif has_window:
        period_label = f"{state.start:%d.%m.%Y} – {state.end:%d.%m.%Y}"
    else:
        period_label = "—"
    if n_valid < n_total:
        warnings.append(f"{n_total - n_valid} il için {meta['label']} verisi yok; bu iller "
                        "haritada taralı gösterilir ve hesaplamalara katılmaz.")

    return DashboardView(
        state=state, pollutant_label=meta["label"], unit=meta["unit"],
        source_label=SOURCES[state.source],
        scope_label=state.region if state.region != DEFAULT_REGION else "Türkiye geneli",
        period_label=period_label, cities=base, kpi=kpi, ranking=ranking,
        series=series, series_label=series_label, note=note, warnings=warnings,
    )


def build_science_note(data: DashboardData, state: FilterState, cities: pd.DataFrame) -> dict:
    """Sanayi yoğunluğu (OSB alanı / km² yerine il başına OSB alanı) ile kirletici arasındaki
    Spearman sıra korelasyonu — sonuç metni hesaplanan değerlerden üretilir."""
    from scipy import stats

    m = data.master.set_index("il")
    df = cities[["il", "value"]].dropna().copy()
    df["osb"] = df["il"].map(m["osb_alani_hektar"])
    df = df.dropna()
    label = POLLUTANTS[state.pollutant]["label"]
    if len(df) < 5 or df["osb"].nunique() < 3:
        return {"ok": False, "n": len(df), "label": label,
                "text": "Bu kapsamda korelasyon hesaplamak için yeterli il yok (en az 5 gerekir)."}
    rho, p = stats.spearmanr(df["osb"], df["value"])
    a = abs(rho)
    strength = ("çok zayıf" if a < 0.2 else "zayıf" if a < 0.4 else "orta" if a < 0.6
                else "güçlü" if a < 0.8 else "çok güçlü")
    direction = "pozitif" if rho > 0 else "negatif"
    signif = p < 0.05
    p_txt = "p < 0,001" if p < 0.001 else f"p = {fmt_num(p, 3)}"
    text = (f"Organize sanayi bölgesi alanı ile {label} arasında {strength} {direction} "
            f"bir ilişki var (Spearman ρ = {fmt_num(rho, 2)}, {p_txt}, n = {len(df)}). "
            + ("İlişki istatistiksel olarak anlamlı." if signif
               else "İlişki %5 düzeyinde anlamlı değil."))
    return {"ok": True, "rho": float(rho), "p": float(p), "n": len(df), "label": label,
            "strength": strength, "direction": direction, "significant": signif, "text": text}
