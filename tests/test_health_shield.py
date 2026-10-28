"""
Birim Testleri: DSÖ Kılavuz Standartları & Halk Sağlığı Koruma Kalkanı
"""

import pytest
import inspect
from visualization.health_shield import render_health_shield_section


def test_health_shield_import_and_signature():
    assert callable(render_health_shield_section)
    sig = inspect.signature(render_health_shield_section)
    assert len(sig.parameters) == 0


def test_health_shield_content_integrity():
    source = inspect.getsource(render_health_shield_section)

    # 1. Başlık ve Rozetler
    assert "DSÖ Kılavuz Standartları &amp; Halk Sağlığı Koruma Kalkanı" in source
    assert "DSÖ Yıllık Kılavuz Değeri: <strong style='color:#ffffff; margin-left:3px;'>5 µg/m³</strong>" in source
    assert "DSÖ 24 Saatlik Kılavuz Değeri: <strong style='color:#ffffff; margin-left:3px;'>15 µg/m³</strong>" in source
    # Kara Rapor 2025'te yayımlanan gerçek değer (eski doğrulanamayan 36,3 ortalaması kaldırıldı)
    assert "En Yüksek İstasyon (Iğdır, Kara Rapor 2025): <strong style='color:#ffffff; margin-left:3px;'>46,8 µg/m³</strong>" in source
    assert "DSÖ Ara Hedef-1 (yıllık): <strong style='color:#ffffff; margin-left:3px;'>35 µg/m³</strong>" in source
    assert "36,3 µg/m³" not in source

    # 2. 4 Koruma Kartı
    assert "Hassas Gruplar (Kronik/Çocuk/Yaşlı)" in source
    assert "Bireysel Maske &amp; Filtre" in source
    assert "Ev İçi &amp; Kapalı Alan İzolasyonu" in source
    assert "Egzersiz ve Ulaşım Stratejisi" in source

    # 3. İçerik Doğrulaması
    assert "KOAH, astım ve kalp hastaları" in source
    assert "N95 / FFP2" in source
    assert "HEPA filtreli" in source
    assert "yeşil alan ve park rotalarını" in source
