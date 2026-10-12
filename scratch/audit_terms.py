import os
import re

PATTERNS = [
    r'Canlı\s*Veri',
    r'canlı',
    r'anlık',
    r'şu an',
    r'bugün',
    r'güncel',
    r'mg/m[³3]',
    r'2026\s*\(Bugün\)',
    r'Güvenli\s*Eşik',
    r'güvenli\s*eşik',
    r'kurtarılan\s*can',
    r'Kurtarılan\s*Can',
    r'Kurtarılan\s*tahmini\s*can',
    r'toksik\s*afet',
    r'zafer',
    r'erken\s*ölüm\s*faturası',
    r'önceki\s*30\s*gün',
    r'son\s*30\s*gün'
]

results = {p: [] for p in PATTERNS}

for root, dirs, files in os.walk('.'):
    if 'venv' in root or '.git' in root or '__pycache__' in root or '.pytest_cache' in root or 'scratch' in root:
        continue
    for f in files:
        if f.endswith('.py') or f.endswith('.html') or f.endswith('.md'):
            filepath = os.path.join(root, f)
            try:
                with open(filepath, 'r', encoding='utf-8') as fh:
                    lines = fh.readlines()
                    for idx, line in enumerate(lines, 1):
                        for p in PATTERNS:
                            if re.search(p, line, re.IGNORECASE):
                                results[p].append((filepath, idx, line.strip()))
            except Exception as e:
                pass

with open('scratch/audit_results.txt', 'w', encoding='utf-8') as out:
    out.write("=== AUDIT SUMMARY ===\n")
    for p, matches in results.items():
        out.write(f"\nPattern: [{p}] -> {len(matches)} occurrences\n")
        for fpath, lnum, line in matches:
            out.write(f"  {fpath}:{lnum} | {line[:140]}\n")

print("Audit written to scratch/audit_results.txt")
