import json

full_path = r"C:\Users\Ali Altın\.gemini\antigravity\brain\9210a30e-36ac-4bf5-88c7-246efcfc58b8\.system_generated\logs\transcript_full.jsonl"

svg_edits = []
with open(full_path, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        if idx >= 2125:
            data = json.loads(line)
            s_idx = data.get("step_index", idx)
            for tc in data.get("tool_calls", []):
                args = tc.get("args", {})
                if "turkey_map.svg" in str(args):
                    svg_edits.append((idx, s_idx, tc.get("name"), args))

print(f"Total svg edits: {len(svg_edits)}")
for idx, s_idx, name, args in svg_edits:
    print(f"Line {idx}, Step {s_idx}: {name} - {args.get('Description', args.get('toolAction', ''))}")
