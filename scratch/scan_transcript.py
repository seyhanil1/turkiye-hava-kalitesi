import json

full_path = r"C:\Users\Ali Altın\.gemini\antigravity\brain\9210a30e-36ac-4bf5-88c7-246efcfc58b8\.system_generated\logs\transcript_full.jsonl"

steps = []
with open(full_path, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        data = json.loads(line)
        step_idx = data.get("step_index", idx)
        for tc in data.get("tool_calls", []):
            name = tc.get("name", "")
            args_obj = tc.get("args", {})
            args_str = json.dumps(args_obj, ensure_ascii=False)
            if "pixel_perfect_dashboard" in args_str or "turkey_map" in args_str:
                steps.append((idx, step_idx, name, args_obj.get("toolAction", ""), args_obj))

print(f"Total matching calls in full transcript: {len(steps)}")
for idx, s_idx, name, action, args in steps:
    tgt = args.get("TargetFile", args.get("AbsolutePath", ""))
    print(f"Line {idx}, Step {s_idx}: {name} - {action} | Target: {tgt}")
