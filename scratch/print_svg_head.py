import json

full_path = r"C:\Users\Ali Altın\.gemini\antigravity\brain\9210a30e-36ac-4bf5-88c7-246efcfc58b8\.system_generated\logs\transcript_full.jsonl"

with open(full_path, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        if idx == 2168:
            data = json.loads(line)
            content = data.get("content", "")
            lines = content.split("\n")
            for l in lines[4:30]:
                print(l)
