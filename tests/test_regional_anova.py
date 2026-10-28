"""
Birim Testleri: Bölgeler arası ANOVA / Kruskal-Wallis yorumu
"""

import pytest
from data_sources.local_official_data import build_master_dataset
from analytics.hypothesis_tests import run_regional_anova

def test_regional_anova_academic_turkish():
    df = build_master_dataset()
    res = run_regional_anova(df, group_col="bolge", val_col="pm25")
    
    assert res["success"] is True
    # H0 ve H1 akademik Türkçe kontrolleri
    assert res["h0"] == "H₀: Bölgelerin ortalama PM2.5 kirlilik seviyeleri arasında istatistiksel olarak anlamlı bir fark yoktur."
    assert res["h1"] == "H₁: En az bir bölgenin kirlilik seviyesi diğer bölgelerden istatistiksel olarak anlamlı derecede farklıdır."
    assert "PM25" not in res["h0"]
    assert "PM25" not in res["h1"]
    
    # Değerlendirme cümlesi iki testin sonucuyla tutarlı olmalı (yalnızca biri anlamlıysa bunu açıkça söylemeli)
    interp = res["interpretation"]
    if res["anova_significant"] and res["kruskal_significant"]:
        assert "her iki test için p < 0.05" in interp
    elif not (res["anova_significant"] or res["kruskal_significant"]):
        assert "gruplar arasında istatistiksel olarak anlamlı bir fark tespit edilmemiştir (p > 0.05)." in interp
    else:
        assert "sonuç kullanılan teste duyarlıdır" in interp
    assert "anlamlı bir varyasyon tespit edilmemiştir" not in interp
