import json

full_path = r"C:\Users\Ali Altın\.gemini\antigravity\brain\9210a30e-36ac-4bf5-88c7-246efcfc58b8\.system_generated\logs\transcript_full.jsonl"

with open(full_path, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        if idx in (2126, 2127, 2128, 2129, 2130, 2131, 2167, 2168, 2169, 2170, 2172):
            data = json.loads(line)
            print(f"Line {idx}, type {data.get('type')}")
            for tc in data.get("tool_calls", []):
                print("  tc:", tc.get("name"), tc.get("args", {}).get("toolAction"))
            content = data.get("content", "")
            if content and "<svg" in content:
                print(f"  has <svg in content, length: {len(content)}")
                # let's see start of content
                print("  content snippet:", content[:200])
