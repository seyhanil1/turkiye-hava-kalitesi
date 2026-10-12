import json

full_path = r"C:\Users\Ali Altın\.gemini\antigravity\brain\9210a30e-36ac-4bf5-88c7-246efcfc58b8\.system_generated\logs\transcript_full.jsonl"

with open(full_path, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        data = json.loads(line)
        for tc in data.get("tool_calls", []):
            if "turkey_map.svg" in str(tc.get("args", {})):
                if tc.get("name") in ("write_to_file", "replace_file_content"):
                    print(f"Line {idx}: {tc.get('name')} {tc.get('args', {}).get('Description')}")
