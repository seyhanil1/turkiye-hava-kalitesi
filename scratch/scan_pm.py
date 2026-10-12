import os
import re

patterns = [r'\bpm10\b', r'\bno2\b', r'PM10', r'NO₂', r'NO2', r'pm10_ratio']
compiled = [re.compile(p, re.IGNORECASE) for p in patterns]

found = {}
for root, dirs, files in os.walk('.'):
    if any(x in root for x in ['.git', '.gemini', 'venv', '__pycache__', '.pytest_cache', 'tests', 'scratch', 'assets']):
        continue
    for f in files:
        if f.endswith(('.png', '.jpg', '.jpeg', '.xlsx', '.ico', '.svg', '.jsonl', '.json', '.txt')):
            continue
        filepath = os.path.join(root, f).replace('\\', '/')
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
            for idx, line in enumerate(lines, 1):
                for c in compiled:
                    if c.search(line):
                        found.setdefault(filepath, []).append((idx, line.strip()))
                        break
        except Exception:
            pass

with open('scratch/pm_matches.txt', 'w', encoding='utf-8') as out:
    for path, matches in sorted(found.items()):
        out.write(f'=== {path} ({len(matches)} matches) ===\n')
        for idx, text in matches:
            out.write(f'  L{idx}: {text}\n')
        out.write('\n')

print(f'Done. Total files with matches: {len(found)}')
