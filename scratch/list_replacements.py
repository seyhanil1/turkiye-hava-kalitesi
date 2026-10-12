import json

full_path = r"C:\Users\Ali Altın\.gemini\antigravity\brain\9210a30e-36ac-4bf5-88c7-246efcfc58b8\.system_generated\logs\transcript_full.jsonl"

replacements = []
with open(full_path, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        if idx >= 2125:
            data = json.loads(line)
            s_idx = data.get("step_index", idx)
            for tc in data.get("tool_calls", []):
                if tc.get("name") == "replace_file_content":
                    args = tc.get("args", {})
                    if "pixel_perfect_dashboard.py" in args.get("TargetFile", ""):
                        replacements.append((idx, s_idx, args))

print(f"Total replacements on pixel_perfect_dashboard.py: {len(replacements)}")
for i, (idx, s_idx, args) in enumerate(replacements):
    desc = args.get("Description", "")
    instr = args.get("Instruction", "")
    print(f"[{i}] Line {idx}, Step {s_idx}: {desc} | {instr}")
