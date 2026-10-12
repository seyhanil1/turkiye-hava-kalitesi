import sys
sys.path.insert(0, ".")
import pandas as pd
from data_sources.local_official_data import normalize_text, PLAKA_ILLER

il_yuzolcumu_km2 = {
    'Adana': 14045, 'Adıyaman': 7606, 'Afyonkarahisar': 14718, 'Ağrı': 11498, 'Amasya': 5703,
    'Ankara': 25401, 'Antalya': 20790, 'Artvin': 7367, 'Aydın': 7904, 'Balıkesir': 14472,
    'Bilecik': 4306, 'Bingöl': 8253, 'Bitlis': 7094, 'Bolu': 8323, 'Burdur': 7134,
    'Bursa': 10886, 'Çanakkale': 9954, 'Çankırı': 7492, 'Çorum': 12796, 'Denizli': 11848,
    'Diyarbakır': 15204, 'Edirne': 6097, 'Elazığ': 9281, 'Erzincan': 11727, 'Erzurum': 25330,
    'Eskişehir': 13902, 'Gaziantep': 6844, 'Giresun': 6831, 'Gümüşhane': 6437, 'Hakkari': 7179,
    'Hatay': 5831, 'Isparta': 8871, 'Mersin': 15512, 'İstanbul': 5315, 'İzmir': 12015,
    'Kars': 10139, 'Kastamonu': 13157, 'Kayseri': 17109, 'Kırklareli': 6294, 'Kırşehir': 6530,
    'Kocaeli': 3625, 'Konya': 41001, 'Kütahya': 12013, 'Malatya': 12102, 'Manisa': 13228,
    'Kahramanmaraş': 14456, 'Mardin': 8806, 'Muğla': 12949, 'Muş': 8719, 'Nevşehir': 5391,
    'Niğde': 7365, 'Ordu': 5952, 'Rize': 3922, 'Sakarya': 4894, 'Samsun': 9364,
    'Siirt': 5473, 'Sinop': 5858, 'Sivas': 28488, 'Tekirdağ': 6342, 'Tokat': 10072,
    'Trabzon': 4664, 'Tunceli': 7685, 'Şanlıurfa': 19336, 'Uşak': 5363, 'Van': 21334,
    'Yozgat': 14085, 'Zonguldak': 3309, 'Aksaray': 7965, 'Bayburt': 3739, 'Karaman': 8868,
    'Kırıkkale': 4569, 'Batman': 4694, 'Şırnak': 7151, 'Bartın': 2080, 'Ardahan': 4967,
    'Iğdır': 3587, 'Yalova': 850, 'Karabük': 4113, 'Kilis': 1427, 'Osmaniye': 3195,
    'Düzce': 2592
}

df_san = pd.read_csv('data/sanayi.txt', sep='\t')
il_col = df_san.columns[1]
hektar_col = df_san.columns[6]

df_san['il_norm'] = df_san[il_col].astype(str).apply(normalize_text)

df_san['hektar_eski'] = pd.to_numeric(
    df_san[hektar_col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False),
    errors='coerce'
).fillna(0)

df_san['hektar_yeni'] = pd.to_numeric(
    df_san[hektar_col].astype(str).str.replace(',', '.', regex=False),
    errors='coerce'
).fillna(0)

il_map = {normalize_text(v): v for v in PLAKA_ILLER.values()}
df_san['il'] = df_san['il_norm'].map(il_map)

agg = df_san.groupby('il').agg(
    osb_sayisi=('il', 'count'),
    eski_ha=('hektar_eski', 'sum'),
    yeni_ha=('hektar_yeni', 'sum')
).reset_index()

df_81 = pd.DataFrame([{'plaka': k, 'il': v} for k, v in sorted(PLAKA_ILLER.items())])
df_res = pd.merge(df_81, agg, on='il', how='left').fillna(0)
df_res['osb_sayisi'] = df_res['osb_sayisi'].astype(int)
df_res['il_alani_km2'] = df_res['il'].map(il_yuzolcumu_km2)
df_res['il_alani_ha'] = df_res['il_alani_km2'] * 100
df_res['oran_yuzde'] = (df_res['yeni_ha'] / df_res['il_alani_ha']) * 100
df_res['ha_per_osb'] = df_res.apply(lambda r: (r['yeni_ha'] / r['osb_sayisi']) if r['osb_sayisi'] > 0 else 0.0, axis=1)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def check_flags(row):
    flags = []
    if row['oran_yuzde'] > 1.5:
        flags.append('BAYRAK: > %1.5 il alani')
    if row['ha_per_osb'] > 2500:
        flags.append('BAYRAK: > 2.500 ha/OSB')
    if row['osb_sayisi'] > 0 and row['ha_per_osb'] < 20:
        flags.append('BAYRAK: < 20 ha/OSB')
    return ', '.join(flags) if flags else 'Normal'

df_res['bayrak'] = df_res.apply(check_flags, axis=1)

for idx, r in df_res.iterrows():
    print(f"| {r['plaka']:02d} | {r['il']} | {r['osb_sayisi']} | {r['eski_ha']:,.1f} ha | {r['yeni_ha']:,.2f} ha | {r['il_alani_ha']:,.0f} ha | %{r['oran_yuzde']:.3f} | {r['ha_per_osb']:.1f} ha | {r['bayrak']} |")
