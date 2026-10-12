import re

with open('assets/turkey_map.svg', 'r', encoding='utf-8') as f:
    text = f.read()

provinces = re.findall(r'data-name="([^"]+)"', text)
outer_circles = re.findall(r'<circle cx="([^"]+)" cy="([^"]+)" r="([0-9.]+)" fill="url\([^)]+\)"', text)

print(f"Provinces: {len(provinces)}, Outer circles: {len(outer_circles)}")
for i in range(min(len(provinces), len(outer_circles))):
    p = provinces[i]
    cx, cy, r = outer_circles[i]
    if i < 10 or i > 75:
        print(f"{i+1}. {p}: cx={cx}, cy={cy}, r={r}")
