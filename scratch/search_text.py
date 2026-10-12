import os

root_dir = os.getcwd()
targets = ["insanlar", "toplum", "kazanım", "kazanim", "kurtarılan", "sağlık ve çevre"]

results = []
for root, dirs, files in os.walk(root_dir):
    if "venv" in root or ".git" in root or "__pycache__" in root:
        continue
    for f in files:
        if f.endswith(".py") or f.endswith(".html"):
            path = os.path.join(root, f)
            try:
                with open(path, "r", encoding="utf-8") as file:
                    for lno, line in enumerate(file, 1):
                        lower = line.lower()
                        for t in targets:
                            if t in lower:
                                results.append((path, lno, line.strip()))
                                break
            except Exception:
                pass

print(f"Found {len(results)} matches:")
for p, lno, l in results:
    rel = os.path.relpath(p, root_dir)
    print(f"{rel}:{lno} -> {l[:110]}")
