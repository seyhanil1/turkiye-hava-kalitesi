import re

with open('assets/turkey_map.svg', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update viewBox and preserveAspectRatio
content = re.sub(
    r'<svg\s+xmlns="http://www.w3.org/2000/svg"\s+viewBox="[^"]*"\s+class="turkey-svg-map">',
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 562 238" class="turkey-svg-map" preserveAspectRatio="xMidYMid meet">',
    content
)

# 2. Update <defs> with the 5 palette radial gradients
defs_replacement = """<defs>
  <filter id="badgeShadow" x="-20%" y="-20%" width="140%" height="140%">
    <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#000000" flood-opacity="0.75"/>
  </filter>
  <!-- 5-Level Palet: İyi (#19D3A2), Orta (#E8D44D), Hassas (#FF9F3D), Sağlıksız (#FF4D5E), Kötü (#B05CFF) -->
  <radialGradient id="rg-iyi" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#ffffff" stop-opacity="1" />
    <stop offset="28%" stop-color="#19D3A2" stop-opacity="0.9" />
    <stop offset="70%" stop-color="#19D3A2" stop-opacity="0.35" />
    <stop offset="100%" stop-color="#19D3A2" stop-opacity="0" />
  </radialGradient>
  <radialGradient id="rg-orta" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#ffffff" stop-opacity="1" />
    <stop offset="28%" stop-color="#E8D44D" stop-opacity="0.9" />
    <stop offset="70%" stop-color="#E8D44D" stop-opacity="0.35" />
    <stop offset="100%" stop-color="#E8D44D" stop-opacity="0" />
  </radialGradient>
  <radialGradient id="rg-hassas" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#ffffff" stop-opacity="1" />
    <stop offset="28%" stop-color="#FF9F3D" stop-opacity="0.9" />
    <stop offset="70%" stop-color="#FF9F3D" stop-opacity="0.35" />
    <stop offset="100%" stop-color="#FF9F3D" stop-opacity="0" />
  </radialGradient>
  <radialGradient id="rg-sagliksiz" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#ffffff" stop-opacity="1" />
    <stop offset="28%" stop-color="#FF4D5E" stop-opacity="0.9" />
    <stop offset="70%" stop-color="#FF4D5E" stop-opacity="0.35" />
    <stop offset="100%" stop-color="#FF4D5E" stop-opacity="0" />
  </radialGradient>
  <radialGradient id="rg-kotu" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#ffffff" stop-opacity="1" />
    <stop offset="28%" stop-color="#B05CFF" stop-opacity="0.9" />
    <stop offset="70%" stop-color="#B05CFF" stop-opacity="0.35" />
    <stop offset="100%" stop-color="#B05CFF" stop-opacity="0" />
  </radialGradient>
  <!-- Eski isimler için geriye dönük uyumluluk -->
  <radialGradient id="rg-green" href="#rg-iyi" />
  <radialGradient id="rg-yellow" href="#rg-orta" />
  <radialGradient id="rg-orange" href="#rg-hassas" />
  <radialGradient id="rg-red" href="#rg-sagliksiz" />
  <radialGradient id="rg-purple" href="#rg-kotu" />
</defs>"""

content = re.sub(r'<defs>[\s\S]*?</defs>', defs_replacement, content)

# 3. Extract province names
names = re.findall(r'data-name="([^"]+)"', content)

# 4. Extract dots layer and rewrite with data-city, class, r=9.5 and r=2.8
m_dots = re.search(r'<g class="city-dots-layer"[^>]*>([\s\S]*?)</g>', content)
if m_dots:
    raw_dots = m_dots.group(1)
    # find all circle elements
    circle_matches = list(re.finditer(r'<circle\s+cx="([^"]+)"\s+cy="([^"]+)"\s+r="([^"]+)"\s+fill="([^"]+)"[^>]*>', raw_dots))
    
    new_circles_lines = []
    for i in range(len(names)):
        halo_match = circle_matches[i * 2]
        center_match = circle_matches[i * 2 + 1]
        
        cx = halo_match.group(1)
        cy = halo_match.group(2)
        old_fill = halo_match.group(4)
        cname = names[i]
        
        new_circles_lines.append(f'  <circle cx="{cx}" cy="{cy}" r="9.5" fill="{old_fill}" class="city-dot-halo" data-city="{cname}" pointer-events="none" />')
        new_circles_lines.append(f'  <circle cx="{cx}" cy="{cy}" r="2.8" fill="#ffffff" class="city-dot-center" data-city="{cname}" pointer-events="none" />')
    
    new_dots_layer = '<g class="city-dots-layer" pointer-events="none">\n' + '\n'.join(new_circles_lines) + '\n</g>'
    content = content[:m_dots.start()] + new_dots_layer + content[m_dots.end():]

# 5. Upgrade the 7 badges layer
new_badges_layer = """<g class="city-badges-layer" pointer-events="none">

    <g class="city-badge" data-city="İstanbul" transform="translate(68.0, 16.0)" filter="url(#badgeShadow)">
        <rect width="52" height="23" rx="4" fill="#011b2f" fill-opacity="0.9" stroke="#0a3958" stroke-width="0.8" />
        <text x="26.0" y="8.8" text-anchor="middle" fill="#f8fafc" font-size="6.8" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700">İstanbul</text>
        <text class="badge-val" x="26.0" y="17.5" text-anchor="middle" fill="#E8D44D" font-size="7.5" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800">38 µg/m³</text>
    </g>

    <g class="city-badge" data-city="Ankara" transform="translate(182.0, 62.0)" filter="url(#badgeShadow)">
        <rect width="52" height="23" rx="4" fill="#011b2f" fill-opacity="0.9" stroke="#0a3958" stroke-width="0.8" />
        <text x="26.0" y="8.8" text-anchor="middle" fill="#f8fafc" font-size="6.8" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700">Ankara</text>
        <text class="badge-val" x="26.0" y="17.5" text-anchor="middle" fill="#FF9F3D" font-size="7.5" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800">39 µg/m³</text>
    </g>

    <g class="city-badge" data-city="İzmir" transform="translate(18.0, 112.0)" filter="url(#badgeShadow)">
        <rect width="52" height="23" rx="4" fill="#011b2f" fill-opacity="0.9" stroke="#0a3958" stroke-width="0.8" />
        <text x="26.0" y="8.8" text-anchor="middle" fill="#f8fafc" font-size="6.8" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700">İzmir</text>
        <text class="badge-val" x="26.0" y="17.5" text-anchor="middle" fill="#FF9F3D" font-size="7.5" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800">45 µg/m³</text>
    </g>

    <g class="city-badge" data-city="Antalya" transform="translate(124.0, 166.0)" filter="url(#badgeShadow)">
        <rect width="52" height="23" rx="4" fill="#011b2f" fill-opacity="0.9" stroke="#0a3958" stroke-width="0.8" />
        <text x="26.0" y="8.8" text-anchor="middle" fill="#f8fafc" font-size="6.8" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700">Antalya</text>
        <text class="badge-val" x="26.0" y="17.5" text-anchor="middle" fill="#E8D44D" font-size="7.5" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800">25 µg/m³</text>
    </g>

    <g class="city-badge" data-city="Adana" transform="translate(248.0, 155.0)" filter="url(#badgeShadow)">
        <rect width="52" height="23" rx="4" fill="#011b2f" fill-opacity="0.9" stroke="#0a3958" stroke-width="0.8" />
        <text x="26.0" y="8.8" text-anchor="middle" fill="#f8fafc" font-size="6.8" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700">Adana</text>
        <text class="badge-val" x="26.0" y="17.5" text-anchor="middle" fill="#FF9F3D" font-size="7.5" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800">37 µg/m³</text>
    </g>

    <g class="city-badge" data-city="Diyarbakır" transform="translate(390.0, 120.0)" filter="url(#badgeShadow)">
        <rect width="52" height="23" rx="4" fill="#011b2f" fill-opacity="0.9" stroke="#0a3958" stroke-width="0.8" />
        <text x="26.0" y="8.8" text-anchor="middle" fill="#f8fafc" font-size="6.8" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700">Diyarbakır</text>
        <text class="badge-val" x="26.0" y="17.5" text-anchor="middle" fill="#FF9F3D" font-size="7.5" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800">36 µg/m³</text>
    </g>

    <g class="city-badge" data-city="Van" transform="translate(466.0, 108.0)" filter="url(#badgeShadow)">
        <rect width="52" height="23" rx="4" fill="#011b2f" fill-opacity="0.9" stroke="#0a3958" stroke-width="0.8" />
        <text x="26.0" y="8.8" text-anchor="middle" fill="#f8fafc" font-size="6.8" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700">Van</text>
        <text class="badge-val" x="26.0" y="17.5" text-anchor="middle" fill="#E8D44D" font-size="7.5" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800">22 µg/m³</text>
    </g>

</g>"""

content = re.sub(r'<g class="city-badges-layer"[\s\S]*?</g>\s*</svg>', new_badges_layer + '\n</svg>', content)

with open('assets/turkey_map.svg', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated assets/turkey_map.svg successfully!')
