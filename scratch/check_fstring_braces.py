import re

with open('visualization/pixel_perfect_dashboard.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f'Total lines: {len(lines)}')

# Let's find all lines where single { or } exists in the main html f-string
# Known Python interpolation variables
KNOWN_VARS = {
    'turkey_map_svg', 'cities_json', 'ts_json', 'pm25_ort_str', 'max_il', 'max_val_str',
    'min_il', 'min_val_str', 'il_count', 'active_pollutant', 'active_period', 'active_region',
    'active_page', 'regional_bar_chart_html', 'clusters_card_html', 'hero_bg_uri'
}

issues = []

for i in range(412, len(lines)):
    line = lines[i]
    if '"""' in line and i > 4300:
        break
    clean = line.replace('{{', '').replace('}}', '')
    singles = re.findall(r'\{[^{}]*\}|\{|\}', clean)
    for s in singles:
        content = s.strip('{}').strip()
        # Check if content is a python expression like 'active' if active_pollutant == 'PM2.5' else ''
        if any(v in content for v in KNOWN_VARS):
            continue
        # Also check JS template literals like ${c.il} or similar
        # If in an f-string you have `${c.il}`:
        # In Python f-string:
        # `${{c.il}}` -> evaluates to `${c.il}` in HTML/JS!
        # BUT if someone wrote `${c.il}`, Python evaluates `c.il` as a Python variable!
        # If someone wrote `${{s.bg}}`, in clean it becomes `$s.bg` which has no braces.
        # But if clean still has `{` or `}`, it means there was a SINGLE { or }!
        issues.append((i + 1, s, line.strip()))

print(f'Found {len(issues)} potential issues:')
for line_num, s, line_str in issues:
    print(f'Line {line_num}: {s} ---> {line_str[:90]}')
