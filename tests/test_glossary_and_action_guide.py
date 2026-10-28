"""
Unit and Integration Tests for Glossary Page & Action Guide
Testing DOM stability, emoji-free typography, and academic translations.
"""

import pytest
from streamlit.testing.v1 import AppTest
from app_pages.glossary import render_glossary_page
from app_pages.action_guide import render_action_guide_page
import inspect


def test_glossary_definitions_content():
    """Verify academic definitions for PM2.5, NO2, and SO2 exist in glossary source."""
    source = inspect.getsource(render_glossary_page)
    
    # PM2.5 academic definition check
    assert "Çapı 2,5 mikrometre veya daha küçük ince partikül maddelerdir" in source
    assert "Akciğer alveollerine ve doğrudan kan dolaşımına nüfuz edebildiği için" in source
    
    # SO2 and O3 academic definition check
    assert "SO₂ (Kükürt Dioksit)" in source
    assert "Yüksek kükürtlü kömür ve fuel-oil yakılması sonucu oluşan" in source
    assert "O₃ (Yer Seviyesi Ozon / Troposferik Ozon)" in source


def test_action_guide_content_and_translations():
    """Verify clean translations, 5-tier level terminology and absence of emojis in Action Guide."""
    source = inspect.getsource(render_action_guide_page)
    
    # Check translations and 5-tier scale text
    assert "çift cam ve ısı yalıtımı" in source
    assert "dış ortam fiziksel aktiviteleri" in source
    assert "PM2.5 düzeyinin" in source
    assert "'Yüksek', 'Çok Yüksek' veya 'Kritik'" in source
    assert "Sağlıksız" not in source
    assert '"Hassas" veya "Kritik"' not in source
    assert "'Hassas' veya 'Kritik'" not in source
    
    # Verify no emojis in source
    for char in source:
        code = ord(char)
        assert not (0x1F300 <= code <= 0x1FAFF), f"Stray emoji found: {char} (U+{code:04X})"


def test_apptest_navigation_and_glossary_search():
    """Verify Streamlit AppTest runs Glossary and Action Guide with search filter without errors."""
    at = AppTest.from_file("../app/app.py", default_timeout=30)
    at.run()
    assert not at.exception
    
    # Navigate to Rehber category and Terimler Sözlüğü page
    at.session_state["active_category"] = "Rehber"
    at.session_state["active_page"] = "Terimler Sözlüğü"
    at.run()
    assert not at.exception
    
    # Test typing in search box
    text_inputs = at.text_input
    assert len(text_inputs) >= 1
    
    # Search for PM2.5
    search_box = at.text_input(key="glossary_search_query")
    search_box.input("PM2.5").run()
    assert not at.exception
    
    # Search for an unmatched query (should show st.info without DOM error)
    search_box.input("non_existent_term_xyz_123").run()
    assert not at.exception
    assert len(at.info) >= 1
    assert "Aranan terim bulunamadı." in at.info[0].value
    
    # Clear search
    search_box.input("").run()
    assert not at.exception
    
    # Navigate to Eylem Rehberi (ve geriye dönük Yapılması Gerekenler)
    at.session_state["active_page"] = "Eylem Rehberi"
    at.run()
    assert not at.exception

    at.session_state["active_page"] = "Yapılması Gerekenler"
    at.run()
    assert not at.exception
