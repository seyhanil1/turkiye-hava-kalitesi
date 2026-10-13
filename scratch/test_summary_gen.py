import pandas as pd
from decimal import Decimal, ROUND_HALF_UP

df = pd.read_csv('data/master_data.csv')

def to_tr_num(val: float, decimals: int = 1) -> str:
    if pd.isnull(val): return '—'
    dec_fmt = '1' if decimals == 0 else f'0.{"0"*(decimals-1)}1'
    dec = Decimal(f'{float(val):.4f}').quantize(Decimal(dec_fmt), rounding=ROUND_HALF_UP)
    if decimals == 0: return f'{int(dec):,}'.replace(',', '.')
    parts = f'{dec:.{decimals}f}'.split('.')
    int_part = f'{int(parts[0]):,}'.replace(',', '.')
    return f'{int_part},{parts[1]}'

def to_tr_sign(val: float, decimals: int = 1) -> str:
    sign = '+' if val > 0 else ''
    return f'{sign}{to_tr_num(val, decimals)}'

def generate_city_summary(df: pd.DataFrame, city_name: str) -> dict:
    il_row = df[df['il'] == city_name].iloc[0]
    bolge = il_row['bolge']

    pm_rank = int(df['pm25'].rank(ascending=True, method='min')[df['il'] == city_name].iloc[0])
    sentence_pm_rank = f"81 il içinde PM2,5'te {pm_rank}. sırada (1 = en düşük)."

    dso_kat = il_row['pm25'] / 5.0
    sentence_dso = f"PM2,5 değeri DSÖ yıllık kılavuzunun (5 µg/m³) {to_tr_num(dso_kat, 1)} katı."

    tr_ort = float(df['pm25'].mean())
    bolge_ort = float(df[df['bolge'] == bolge]['pm25'].mean())
    diff_tr = il_row['pm25'] - tr_ort
    diff_bolge = il_row['pm25'] - bolge_ort
    diff_tr_str = to_tr_sign(diff_tr, 1)
    diff_bolge_str = to_tr_sign(diff_bolge, 1)
    sentence_ort_fark = (
        f"Türkiye düz il ortalamasına ({to_tr_num(tr_ort, 1)} µg/m³) göre {diff_tr_str} µg/m³, "
        f"{bolge} Bölgesi ortalamasına ({to_tr_num(bolge_ort, 1)} µg/m³) göre {diff_bolge_str} µg/m³ fark göstermektedir."
    )

    q1_osb = float(df['toplam_osb'].quantile(0.25))
    q3_osb = float(df['toplam_osb'].quantile(0.75))
    q1_pm = float(df['pm25'].quantile(0.25))
    q3_pm = float(df['pm25'].quantile(0.75))

    osb_val = float(il_row['toplam_osb'])
    pm_val = float(il_row['pm25'])

    if osb_val <= q1_osb: osb_group = 'düşük grup'
    elif osb_val >= q3_osb: osb_group = 'yüksek grup'
    else: osb_group = 'orta grup'

    if pm_val <= q1_pm: pm_group = 'düşük grup'
    elif pm_val >= q3_pm: pm_group = 'yüksek grup'
    else: pm_group = 'orta grup'

    if osb_group == 'düşük grup' and pm_group == 'yüksek grup':
        sentence_osb = 'OSB sayısı düşük gruptayken PM2,5 yüksek gruptadır.'
    elif osb_group == 'yüksek grup' and pm_group == 'düşük grup':
        sentence_osb = 'OSB sayısı yüksek gruptayken PM2,5 düşük gruptadır.'
    else:
        sentence_osb = f'OSB sayısı {osb_group}ta, PM2,5 değeri {pm_group}tadır.'

    sol_rank = int(df['solunum_olum_100k'].rank(ascending=True, method='min')[df['il'] == city_name].iloc[0])
    nufus_rank = int(df['nufus'].rank(ascending=False, method='min')[df['il'] == city_name].iloc[0])

    sentence_sol_rank = f"81 il içinde solunum hastalıkları kaba ölüm hızında {sol_rank}. sırada (1 = en düşük, kaba hız)."
    sentence_nufus_rank = f"81 il içinde nüfus büyüklüğünde {nufus_rank}. sırada (1 = en yüksek)."

    sentences = [
        sentence_pm_rank,
        sentence_dso,
        sentence_ort_fark,
        sentence_osb,
        sentence_sol_rank,
        sentence_nufus_rank
    ]

    kunye = {
        'nufus': int(il_row['nufus']),
        'bolge': bolge,
        'plaka': int(il_row['plaka']),
        'toplam_osb': int(il_row['toplam_osb'])
    }

    return {
        'sentences': sentences,
        'kunye': kunye,
        'footnote': 'Not: PM2,5 model/istasyon karması; ölüm hızı kaba hızdır; il düzeyi veri bireysel sonuç vermez.'
    }

forbidden = ['avrupa', 'sanayi yok', 'çünkü', 'nedeniyle', 'kaynaklı', 'en temiz', 'en kirli']

for c in df['il'].unique():
    res = generate_city_summary(df, c)
    for s in res['sentences']:
        for fb in forbidden:
            assert fb not in s.lower(), f'{c} contains {fb}: {s}'

print('All 81 cities successfully validated with zero forbidden words!')
for c in ['İstanbul', 'Iğdır', 'Şanlıurfa', 'Bayburt']:
    print('---', c, '---')
    for s in generate_city_summary(df, c)['sentences']:
        print(' *', s)
