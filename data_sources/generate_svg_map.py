import json
import os

with open('data/tr-cities.json', 'r', encoding='utf-8') as f:
    geojson = json.load(f)

min_lon, max_lon = 25.5, 44.9
min_lat, max_lat = 35.7, 42.3
W, H = 560, 240

def proj(lon, lat):
    x = (lon - min_lon) / (max_lon - min_lon) * W
    y = H - (lat - min_lat) / (max_lat - min_lat) * H
    return f"{x:.1f},{y:.1f}"

paths = []
for feat in geojson['features']:
    p_name = feat['properties'].get('name', '')
    geom = feat['geometry']
    g_type = geom['type']
    coords = geom['coordinates']
    
    subpaths = []
    if g_type == 'Polygon':
        for ring in coords:
            if len(ring) > 2:
                first = proj(ring[0][0], ring[0][1])
                rest = " L ".join(proj(pt[0], pt[1]) for pt in ring[1:])
                subpaths.append(f"M {first} L {rest} Z")
    elif g_type == 'MultiPolygon':
        for poly in coords:
            for ring in poly:
                if len(ring) > 2:
                    first = proj(ring[0][0], ring[0][1])
                    rest = " L ".join(proj(pt[0], pt[1]) for pt in ring[1:])
                    subpaths.append(f"M {first} L {rest} Z")
    d_attr = " ".join(subpaths)
    paths.append(f'<path d="{d_attr}" class="province-path" data-name="{p_name}" />')

svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" class="turkey-svg-map">
<defs>
  <filter id="cyanGlow" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="1.5" result="blur" />
    <feMerge>
      <feMergeNode in="blur" />
      <feMergeNode in="SourceGraphic" />
    </feMerge>
  </filter>
</defs>
<g fill="#072238" stroke="#00c8b8" stroke-width="0.55" stroke-opacity="0.85">
{''.join(paths)}
</g>
</svg>'''

os.makedirs('assets', exist_ok=True)
with open('assets/turkey_map.svg', 'w', encoding='utf-8') as f:
    f.write(svg_content)

print(f"assets/turkey_map.svg generated successfully, size: {len(svg_content)} bytes")
