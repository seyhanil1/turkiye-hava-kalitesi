import json

full_path = r"C:\Users\Ali Altın\.gemini\antigravity\brain\9210a30e-36ac-4bf5-88c7-246efcfc58b8\.system_generated\logs\transcript_full.jsonl"

edits = []
with open(full_path, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        if 2125 <= idx <= 2631:
            data = json.loads(line)
            s_idx = data.get("step_index", idx)
            for tc in data.get("tool_calls", []):
                name = tc.get("name", "")
                if name in ("replace_file_content", "write_to_file"):
                    args = tc.get("args", {})
                    tgt = args.get("TargetFile", "")
                    edits.append((idx, s_idx, name, tgt, args.get("Instruction", ""), args))

print(f"Total file edits between prompt 9 and current prompt: {len(edits)}")
for idx, s_idx, name, tgt, instr, args in edits:
    print(f"Line {idx}, Step {s_idx}: {name} -> {tgt} ({instr})")
