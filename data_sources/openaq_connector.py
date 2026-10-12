"""
OpenAQ API v3 Bağlayıcısı
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

Özellikler:
- OpenAQ v3 REST API entegrasyonu.
- .env dosyasından güvenli API anahtarı okuma.
- Otantik hata ve durum yönetimi (401 Unauthorized, rate limit, vb.).
"""

import os
import requests
from typing import Dict, Any, Optional

class OpenAQConnector:
    BASE_URL = "https://api.openaq.org/v3"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAQ_API_KEY")
        
    def check_connection(self) -> Dict[str, Any]:
        """
        OpenAQ bağlantı durumunu ve yetkilendirmeyi kontrol eder.
        """
        if not self.api_key:
            return {
                "status": "missing_key",
                "connected": False,
                "message": (
                    "OpenAQ API v3 erişimi için API anahtarı gereklidir. "
                    "Lütfen .env dosyasına OPENAQ_API_KEY=anahtariniz tanımlayın. "
                    "Platform şu anda Kara Rapor 2025 ve Copernicus CAMS resmi ölçümlerini kullanmaktadır."
                )
            }
            
        headers = {"X-API-Key": self.api_key}
        try:
            resp = requests.get(
                f"{self.BASE_URL}/locations",
                headers=headers,
                params={"countries_id": "TR", "limit": 1},
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                count = len(data.get("results", []))
                return {
                    "status": "connected",
                    "connected": True,
                    "message": f"OpenAQ API v3 bağlantısı başarılı. Aktif istasyonlar sorgulanabilir.",
                    "results_count": count
                }
            elif resp.status_code == 401:
                return {
                    "status": "unauthorized",
                    "connected": False,
                    "message": "OpenAQ API anahtarı geçersiz veya yetkisiz (HTTP 401)."
                }
            else:
                return {
                    "status": "error",
                    "connected": False,
                    "message": f"OpenAQ API yanıt vermedi (HTTP {resp.status_code})."
                }
        except Exception as e:
            return {
                "status": "network_error",
                "connected": False,
                "message": f"OpenAQ sunucusuna erişilemedi: {str(e)}"
            }

    def get_stations(self, limit: int = 50) -> Dict[str, Any]:
        """Türkiye'deki hava kalitesi ölçüm istasyonlarını sorgular."""
        status = self.check_connection()
        if not status["connected"]:
            return {"success": False, "error": status["message"], "data": []}
            
        headers = {"X-API-Key": self.api_key}
        try:
            resp = requests.get(
                f"{self.BASE_URL}/locations",
                headers=headers,
                params={"countries_id": "TR", "limit": limit},
                timeout=8
            )
            if resp.status_code == 200:
                return {"success": True, "data": resp.json().get("results", [])}
            return {"success": False, "error": f"HTTP {resp.status_code}", "data": []}
        except Exception as e:
            return {"success": False, "error": str(e), "data": []}
