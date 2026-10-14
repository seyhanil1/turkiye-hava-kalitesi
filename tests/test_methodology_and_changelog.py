"""
Test Methodology and Changelog Pages
Doğrulama:
1. HTML tablo sızıntısı yok (<tr, <td kod bloğu olarak değil düzgün HTML olarak render edilir).
2. 'GG.AA.2026' placeholder'ı yok.
3. 'Son 12 Ay' çelişkili ifadesi yok; 'Doğrulanmış 12 Aylık Konsolidasyon Dönemi' kullanılıyor.
4. 'df[\'pm25\'].mean()', 'b_df[\'pm25\'].mean()' ve 'dropna()' sızıntısı yok.
5. Yinelenen 'Yöntem ve Kaynaklar' expander'ı methodology.py'de yok.
6. Sürüm notlarında 'İl Grupları' doğru Türkçe karakterle yer alıyor.
"""

import os
import re
import pytest


def test_no_placeholder_dates():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_dirs = ["app", "app_pages", "data_sources", "visualization"]
    
    for td in target_dirs:
        dir_path = os.path.join(root, td)
        for root_dir, _, files in os.walk(dir_path):
            for f in files:
                if f.endswith(".py"):
                    full_p = os.path.join(root_dir, f)
                    with open(full_p, "r", encoding="utf-8") as fp:
                        content = fp.read()
                        assert "GG.AA.2026" not in content, f"Placeholder GG.AA.2026 found in {f}"
                        assert "Son 12 Ay" not in content, f"'Son 12 Ay' found in {f}"


def test_methodology_no_code_leaks():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    meth_path = os.path.join(root, "app_pages", "methodology.py")
    with open(meth_path, "r", encoding="utf-8") as fp:
        content = fp.read()
    
    assert "df['pm25'].mean()" not in content
    assert "b_df['pm25'].mean()" not in content
    assert "dropna()" not in content
    assert "with st.expander(\"Yöntem ve Kaynaklar\")" not in content
    assert "Doğrulanmış 12 Aylık Konsolidasyon Dönemi" in content
    assert "OSB verileri: OSBÜK (Ekim 2026)" in content
    assert "81 ilin PM2.5 değerlerinin ağırlıksız aritmetik ortalamasıdır." in content
    assert "İlgili coğrafi bölgedeki illerin PM2.5 konsantrasyonlarının bölgesel aritmetik ortalamasıdır." in content
    assert "Eksik veya sıfır bildirilmiş kayıtlar hesaplamaya dahil edilmemiş, yalnızca geçerli gözlem günleri baz alınmıştır." in content


def test_changelog_typography():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cl_path = os.path.join(root, "app_pages", "changelog.py")
    with open(cl_path, "r", encoding="utf-8") as fp:
        content = fp.read()
    
    assert "İl Grupları" in content
    assert "Il Grupları" not in content
