with open('app/app.py', 'r', encoding='utf-8') as f:
    c = f.read()

checks = [
    ('CATEGORIES = ["Keşfet", "Analiz", "Gelecek", "Rehber"]', 'Categories without Güven'),
    ('ERKEN VEFAT MALİYETLERİ (VSL)', 'VSL title'),
    ('~42.000 erken ölüm', '42.000 death text'),
    ('DOĞRUDAN SAĞLIK GİDERLERİ', 'Direct health title'),
    ('İŞ GÜCÜ &amp; VERİMLİLİK KAYBI', 'Labor loss title'),
    ('Hava Kirliliğinin Yıllık Tahmini Ekonomik Maliyet Dağılımı', 'Donut title'),
    ('toplam_maliyet * 0.78', '78 percent ratio'),
    ('toplam_maliyet * 0.16', '16 percent ratio'),
]

for pat, name in checks:
    if pat in c:
        print(f'[OK] {name}')
    else:
        print(f'[FAIL] {name}')

forbidden = ['"Güven"', '73.651', 'ürünleri', '🚑', '⚰️', '🔨']
for fb in forbidden:
    if fb in c:
        print(f'[FAIL FORBIDDEN] {fb} found in app/app.py')
    else:
        print(f'[OK CLEAN] {fb} not in app/app.py')
