import re

with open('assets/turkey_map.svg', 'r', encoding='utf-8') as f:
    text = f.read()

names = re.findall(r'data-name="([^"]+)"', text)
m = re.search(r'<g class="city-dots-layer"[^>]*>([\s\S]*?)</g>', text)
circles = re.findall(r'<circle\s+cx="([^"]+)"\s+cy="([^"]+)"[^>]+>', m.group(1))
pairs = circles[::2]

for idx in [0, 6, 7, 39, 40, 25, 77]:
    print(f'Pair {idx} ({names[idx]}): {pairs[idx]}')
