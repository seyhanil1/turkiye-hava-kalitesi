import json

full_path = r"C:\Users\Ali Altın\.gemini\antigravity\brain\9210a30e-36ac-4bf5-88c7-246efcfc58b8\.system_generated\logs\transcript_full.jsonl"

with open(full_path, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        if idx == 439:
            data = json.loads(line)
            tc = data.get("tool_calls", [{}])[0]
            code = tc.get("args", {}).get("CodeContent", "")
            with open("scratch/scratch_build_map_original.py", "w", encoding="utf-8") as out:
                out.write(code)
            print("Successfully extracted scratch/scratch_build_map_original.py! Length:", len(code))
