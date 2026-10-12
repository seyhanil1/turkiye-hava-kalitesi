import os, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

matches = []
for root, dirs, files in os.walk('.'):
    if any(x in root for x in ['.venv', 'venv', '.git', '__pycache__', '.pytest_cache']):
        continue
    for f in files:
        if f.endswith('.py'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                for idx, line in enumerate(fl, 1):
                    if '.replace(' in line:
                        matches.append((p, idx, line.strip()))

print(f"Total .replace occurrences: {len(matches)}")
target_chars = ['.', ',']
for p, idx, l in matches:
    if '.replace(' in l:
        # Check if replacing dot or comma
        if any(f".replace('{c}'" in l or f'.replace("{c}"' in l for c in target_chars):
            print(f"{p}:{idx} -> {l}")
