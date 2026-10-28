"""
data_sources paketi
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

from data_sources.constants import (
    PLAKA_ILLER,
    IL_TO_PLAKA,
    BOLGELER,
    IL_BOLGE,
    KOORDINATLAR,
    NUFUSLAR,
    DSO_LIMITLERI
)
from data_sources.local_official_data import (
    parse_kara_rapor_istasyon,
    parse_cams_annual,
    parse_tuik_saglik,
    parse_sanayi_osb,
    build_master_dataset
)
from data_sources.openmeteo_connector import (
    OpenMeteoAirQualityConnector,
    get_national_timeseries
)
from data_sources.openaq_connector import OpenAQConnector

__all__ = [
    "PLAKA_ILLER",
    "IL_TO_PLAKA",
    "BOLGELER",
    "IL_BOLGE",
    "KOORDINATLAR",
    "NUFUSLAR",
    "DSO_LIMITLERI",
    "parse_kara_rapor_istasyon",
    "parse_cams_annual",
    "parse_tuik_saglik",
    "parse_sanayi_osb",
    "build_master_dataset",
    "OpenMeteoAirQualityConnector",
    "get_national_timeseries",
    "OpenAQConnector"
]
