import os, sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

terms = [
    'tedavi katsayısı',
    'tedavi katsayisi',
    'tedavi maliyet',
    'tedavi gideri',
    'Sağlık Bakanlığı',
    'Saglik Bakanligi',
    'Sanayi Bakanlığı',
    'Sanayi Bakanligi',
    'İstatistik Bülteni',
    'Istatistik Bulteni',
    '2024 Bülten',
    '2024 Bulten'
]

hits = {t: [] for t in terms}

for root, dirs, files in os.walk('.'):
    if any(x in root for x in ['.venv', 'venv', '.git', '__pycache__', '.pytest_cache', 'scratch']):
        continue
    for f in files:
        if f.endswith(('.py', '.md', '.txt', '.json')):
            if f == 'sanayi.txt': continue
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                for idx, line in enumerate(fl, 1):
                    for t in terms:
                        if t.lower() in line.lower():
                            hits[t].append((p, idx, line.strip()))

for t in terms:
    print(f'=== Terim: "{t}" ({len(hits[t])} eşleşme) ===')
    for p, idx, l in hits[t]:
        print(f'  {p}:{idx} -> {l}')
