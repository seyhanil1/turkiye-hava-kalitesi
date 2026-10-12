import json
import shutil

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

print(f"Total replacements: {len(replacements)}")

# Read current file
with open("visualization/pixel_perfect_dashboard.py", "r", encoding="utf-8") as f:
    content = f.read()

# Apply in reverse
success = True
for i in range(len(replacements) - 1, -1, -1):
    idx, s_idx, args = replacements[i]
    target = args.get("TargetContent")
    replacement = args.get("ReplacementContent")
    desc = args.get("Description", "")
    
    if replacement not in content:
        print(f"FAILED to find replacement for edit [{i}] (Step {s_idx}): {desc}")
        # Let's inspect where it differs
        success = False
        break
    else:
        # Replace replacement with target
        content = content.replace(replacement, target, 1)
        print(f"Reverted [{i}] (Step {s_idx}): {desc}")

if success:
    with open("scratch/pixel_perfect_dashboard_reverted.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS! Reverted content saved to scratch/pixel_perfect_dashboard_reverted.py")
else:
    print("Revert failed at some step.")
