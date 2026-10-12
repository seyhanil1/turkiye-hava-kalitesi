import re
import json

# Read existing map paths
with open("assets/turkey_map.svg", "r", encoding="utf-8") as f:
    orig_svg = f.read()

# Extract paths
paths_matches = re.findall(r'(<path d="([^"]+)" class="province-path" data-name="([^"]+)" />)', orig_svg)
print(f"Extracted {len(paths_matches)} province paths")

centroids = {}
for full_tag, d, name in paths_matches:
    coords = re.findall(r'([0-9]+\.[0-9]+),([0-9]+\.[0-9]+)', d)
    xs = [float(x) for x, y in coords]
    ys = [float(y) for x, y in coords]
    if xs and ys:
        cx = sum(xs) / len(xs)
        cy = sum(ys) / len(ys)
        centroids[name] = (round(cx, 1), round(cy, 1))

# Manual fine-tuned centroids for visual alignment with reference image
manual_adjustments = {
    "İstanbul": (92.0, 48.0),
    "Ankara": (205.0, 94.0),
    "İzmir": (42.0, 142.0),
    "Antalya": (148.0, 196.0),
    "Adana": (272.0, 185.0),
    "Osmaniye": (290.0, 180.0),
    "Hatay": (286.0, 214.0),
    "Diyarbakır": (416.0, 150.0),
    "Van": (490.0, 138.0),
}
for k, v in manual_adjustments.items():
    centroids[k] = v

red_cities = ["Osmaniye", "Hatay", "Adana", "Kahramanmaraş", "Kilis"]
orange_cities = ["Diyarbakır", "Mardin", "Malatya", "Gaziantep", "Şanlıurfa", "Batman", "Siirt", "Adıyaman", "Elazığ", "Ağrı", "Muş", "Bitlis"]
yellow_cities = ["Ankara", "Konya", "Karaman", "Mersin", "Kayseri", "Niğde", "Sivas", "Tokat", "Çorum", "Yozgat", "Kırşehir", "Nevşehir", "Aksaray", "Van", "Hakkari", "Şırnak", "Kars", "Iğdır", "Erzurum", "Erzincan"]

# Assemble new SVG
svg_parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 540 230" class="turkey-svg-map">',
    '<defs>',
    '  <filter id="badgeShadow" x="-20%" y="-20%" width="140%" height="140%">',
    '    <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#000000" flood-opacity="0.7"/>',
    '  </filter>',
    '  <radialGradient id="rg-red" cx="50%" cy="50%" r="50%">',
    '    <stop offset="0%" stop-color="#ffffff" stop-opacity="1" />',
    '    <stop offset="25%" stop-color="#ef4444" stop-opacity="0.9" />',
    '    <stop offset="65%" stop-color="#ef4444" stop-opacity="0.35" />',
    '    <stop offset="100%" stop-color="#ef4444" stop-opacity="0" />',
    '  </radialGradient>',
    '  <radialGradient id="rg-orange" cx="50%" cy="50%" r="50%">',
    '    <stop offset="0%" stop-color="#ffffff" stop-opacity="1" />',
    '    <stop offset="25%" stop-color="#f97316" stop-opacity="0.9" />',
    '    <stop offset="65%" stop-color="#f97316" stop-opacity="0.35" />',
    '    <stop offset="100%" stop-color="#f97316" stop-opacity="0" />',
    '  </radialGradient>',
    '  <radialGradient id="rg-yellow" cx="50%" cy="50%" r="50%">',
    '    <stop offset="0%" stop-color="#ffffff" stop-opacity="1" />',
    '    <stop offset="25%" stop-color="#facc15" stop-opacity="0.9" />',
    '    <stop offset="65%" stop-color="#eab308" stop-opacity="0.35" />',
    '    <stop offset="100%" stop-color="#eab308" stop-opacity="0" />',
    '  </radialGradient>',
    '  <radialGradient id="rg-green" cx="50%" cy="50%" r="50%">',
    '    <stop offset="0%" stop-color="#ffffff" stop-opacity="1" />',
    '    <stop offset="25%" stop-color="#00e599" stop-opacity="0.9" />',
    '    <stop offset="65%" stop-color="#00e599" stop-opacity="0.35" />',
    '    <stop offset="100%" stop-color="#00e599" stop-opacity="0" />',
    '  </radialGradient>',
    '</defs>',
    '<g fill="#041e30" stroke="#00c8b8" stroke-width="0.5" stroke-opacity="0.75" class="provinces-layer">'
]

# Add province paths
for full_tag, d, name in paths_matches:
    svg_parts.append(f'  <path d="{d}" class="province-path" data-name="{name}" />')
svg_parts.append('</g>')

# Add Glowing City Dots Layer
svg_parts.append('<g class="city-dots-layer">')
for name, (cx, cy) in centroids.items():
    if name in red_cities:
        grad = "rg-red"
        halo_r = 11.5
    elif name in orange_cities:
        grad = "rg-orange"
        halo_r = 9.5
    elif name in yellow_cities:
        grad = "rg-yellow"
        halo_r = 8.5
    else:
        grad = "rg-green"
        halo_r = 7.5
        
    svg_parts.append(f'  <circle cx="{cx}" cy="{cy}" r="{halo_r}" fill="url(#{grad})" pointer-events="none" />')
    svg_parts.append(f'  <circle cx="{cx}" cy="{cy}" r="1.8" fill="#ffffff" pointer-events="none" />')
svg_parts.append('</g>')

# Add 7 Key City Tooltip Badges (positioned exactly as in reference screenshot)
badges_data = [
    ("İstanbul", "32 µg/m³", 92.0, 48.0, -22, -30, "#00e5db"),
    ("Ankara", "42 µg/m³", 205.0, 94.0, -22, -30, "#facc15"),
    ("İzmir", "28 µg/m³", 42.0, 142.0, -22, -28, "#00e599"),
    ("Antalya", "31 µg/m³", 148.0, 196.0, -22, -28, "#00e599"),
    ("Adana", "67 µg/m³", 272.0, 185.0, -22, -28, "#ef4444"),
    ("Diyarbakır", "58 µg/m³", 416.0, 150.0, -24, -28, "#f97316"),
    ("Van", "45 µg/m³", 490.0, 138.0, -22, -28, "#facc15"),
]

svg_parts.append('<g class="city-badges-layer" pointer-events="none">')
for city, val, cx, cy, ox, oy, val_color in badges_data:
    bx = cx + ox
    by = cy + oy
    bw = 48
    bh = 22
    svg_parts.append(f'''
    <g transform="translate({bx}, {by})" filter="url(#badgeShadow)">
        <rect width="{bw}" height="{bh}" rx="3.5" fill="#011b2f" fill-opacity="0.94" stroke="#0a3958" stroke-width="0.8" />
        <text x="{bw/2}" y="8.5" text-anchor="middle" fill="#cbd5e1" font-size="6.5" font-family="'Plus Jakarta Sans', sans-serif" font-weight="600">{city}</text>
        <text x="{bw/2}" y="17" text-anchor="middle" fill="{val_color}" font-size="7.5" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800">{val}</text>
    </g>
    ''')
svg_parts.append('</g>')

svg_parts.append('</svg>')

final_svg = "\n".join(svg_parts)
with open("assets/turkey_map.svg", "w", encoding="utf-8") as out:
    out.write(final_svg)

print("Updated assets/turkey_map.svg successfully!")
