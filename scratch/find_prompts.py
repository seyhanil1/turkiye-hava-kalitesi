import json

full_path = r"C:\Users\Ali Altın\.gemini\antigravity\brain\9210a30e-36ac-4bf5-88c7-246efcfc58b8\.system_generated\logs\transcript_full.jsonl"
with open(full_path, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        data = json.loads(line)
        if data.get("type") == "USER_INPUT":
            content = data.get("content", "")
            s_idx = data.get("step_index", idx)
            first_line = content.split("\n")[0] if content else ""
            print(f"Line {idx}, Step {s_idx}: {first_line[:100]}")
