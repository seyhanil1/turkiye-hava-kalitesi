import json

full_path = r"C:\Users\Ali Altın\.gemini\antigravity\brain\9210a30e-36ac-4bf5-88c7-246efcfc58b8\.system_generated\logs\transcript_full.jsonl"

with open(full_path, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        if idx in (2167, 2168, 2169, 2170):
            data = json.loads(line)
            tc = data.get("tool_calls", [{}])[0] if data.get("tool_calls") else {}
            args = tc.get("args", {})
            print(f"Line {idx}, step {data.get('step_index')}, {tc.get('name')}, {args}")
            content = data.get("content", "")
            if content:
                print("Content length:", len(content))
                lines = content.split("\n")
                print("First 5 lines:", lines[:5])
                print("Last 5 lines:", lines[-5:])
