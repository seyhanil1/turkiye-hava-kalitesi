import os, sys, re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

patterns = [
    r"%100\s*uyumlu",
    r"doğrulandı|dogrulandi|doğrulanmış|dogrulanmis",
    r"resmi\s+bülten",
    r"bültenle\s+örtüş",
    r"Bakanlık|Bakanlığı|bakanlik|bakanligi",
    r"resmi\s+veri|resmi\s+sicil|resmi\s+kayıt"
]

combined_regex = re.compile("|".join(patterns), re.IGNORECASE)

records = []
target_dirs = ['app', 'app_pages', 'visualization', 'data_sources', 'data_processing', 'analytics', 'src']

for td in target_dirs:
    for root, dirs, files in os.walk(td):
        for f in files:
            if f.endswith('.py'):
                p = os.path.join(root, f)
                with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                    for idx, line in enumerate(fl, 1):
                        l = line.strip()
                        if combined_regex.search(l):
                            records.append((p, idx, l))

with open('scratch/claims_report.txt', 'w', encoding='utf-8') as out:
    out.write(f"Total occurrences: {len(records)}\n")
    for p, idx, l in records:
        out.write(f"{p}:{idx} -> {l}\n")

print(f"Total occurrences found in code: {len(records)}")
