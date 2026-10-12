import re

with open('assets/turkey_map.svg', 'r', encoding='utf-8') as f:
    text = f.read()

names = re.findall(r'data-name="([^"]+)"', text)
print(f'Provinces count: {len(names)}')
for i, n in enumerate(names):
    print(f'{i}: {n}')
