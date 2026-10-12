"""
HavaAtlası — Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
Kök Dizin Başlatıcı (Root Entrypoint)
"""

import os
import sys

# app/app.py dosyasını çalıştır
app_path = os.path.join(os.path.dirname(__file__), "app", "app.py")
with open(app_path, "r", encoding="utf-8") as f:
    code = f.read()

exec(code, {"__name__": "__main__", "__file__": app_path})
