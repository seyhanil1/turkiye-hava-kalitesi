import os
import re

search_terms = [
    'Yıllık +%3',
    '+%5',
    'Trend',
    'forecast',
    'projeksiyon',
    'Coğrafi Kapan',
    'Ağır Sanayi',
    'Sessiz Tehlike',
    'Pandas'
]

results = {term: [] for term in search_terms}
compiled = [(t, re.compile(re.escape(t), re.IGNORECASE)) for t in search_terms]

for root, dirs, files in os.walk('.'):
    if any(x in root for x in ['.git', '.gemini', 'venv', '__pycache__', '.pytest_cache', 'scratch']):
        continue
    for f in files:
        if f.endswith(('.png', '.jpg', '.jpeg', '.xlsx', '.ico', '.svg', '.jsonl', '.json')):
            continue
        filepath = os.path.join(root, f).replace('\\', '/')
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as fp:
                for idx, line in enumerate(fp, 1):
                    for term, pat in compiled:
                        if pat.search(line):
                            results[term].append((filepath, idx, line.strip()))
        except Exception:
            pass

with open('scratch/search_terms_results.txt', 'w', encoding='utf-8') as out:
    for term in search_terms:
        matches = results[term]
        out.write(f'=== ARAMA TERIMI: "{term}" ({len(matches)} eslesme) ===\n')
        for fp, lno, text in matches:
            out.write(f'  {fp}:{lno} -> {text}\n')
        out.write('\n')

print("Search completed. Results saved to scratch/search_terms_results.txt")
