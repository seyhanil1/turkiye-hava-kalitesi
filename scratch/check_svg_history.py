import json

full_path = r"C:\Users\Ali Altın\.gemini\antigravity\brain\9210a30e-36ac-4bf5-88c7-246efcfc58b8\.system_generated\logs\transcript_full.jsonl"

with open(full_path, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        if 2140 <= idx <= 2225:
            data = json.loads(line)
            for tc in data.get("tool_calls", []):
                args = tc.get("args", {})
                if "turkey_map" in str(args):
                    print(f"Line {idx}: {tc.get('name')} {args.get('toolAction')} {args.get('AbsolutePath')}")
            # Also check if content has turkey_map
            content = data.get("content", "")
            if "<svg" in content and "viewBox" in content:
                print(f"Line {idx}: contains SVG content in tool result! length: {len(content)}")
