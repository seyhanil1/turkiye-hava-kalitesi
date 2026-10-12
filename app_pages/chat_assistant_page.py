"""
💬 AI Veri Asistanı (Yerel & Çevrimdışı Chatbot)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

Tamamen yerel (offline), harici kütüphane veya API anahtarı olmadan çalışan akıllı karar destek asistanı.

Özellikler:
1. %100 Çevrimdışı ve Yerel: Yalnızca platformun mevcut 81 il master_df verisini kullanır.
2. 4 Hazır Buton (st.button):
   - 🚨 En Riskli 3 Şehir
   - 🌿 En Temiz 3 Şehir
   - 💰 Ulusal Sağlık Faturası
   - ⚖️ İstanbul vs Ankara Kıyasla
3. Akıllı Sorgu Eşleme:
   - Türkçe karakter duyarlı il tarama (İ/i, I/ı, Ğ/g, Ü/u, Ş/s, Ö/o, Ç/c ve ekler)
   - İki il geçerse yan yana detaylı karşılaştırma tablosu
   - Tek il geçerse PM2.5, DSÖ durumu ve OSB sayısı karne formatında
   - 'en kirli' / 'en temiz' sorgularında ilk 3 ili listeleme
   - 'maliyet' veya 'fatura' sorgularında ulusal toplam sağlık maliyeti
   - Eşleşmeyen sorularda kullanıcı rehberi
4. st.session_state.messages geçmiş yönetimi ve st.chat_message arayüzü
"""

import streamlit as st
import pandas as pd
import re
from typing import List, Dict, Any


def normalize_tr(text: str) -> str:
    """
    Türkçe karakterleri ve noktalama işaretlerini arama/karşılaştırma toleransı için normalize eder.
    """
    text = text.replace("İ", "i").replace("I", "i").replace("ı", "i")
    text = text.replace("Ğ", "g").replace("ğ", "g")
    text = text.replace("Ü", "u").replace("ü", "u")
    text = text.replace("Ş", "s").replace("ş", "s")
    text = text.replace("Ö", "o").replace("ö", "o")
    text = text.replace("Ç", "c").replace("ç", "c")
    # Kesme ve tırnak işaretlerini boşluğa çevirerek 'İstanbul'da' gibi ekli kelimeleri ayıkla
    text = re.sub(r"[\'\"’`]", " ", text)
    return text.lower().strip()


def detect_cities_in_prompt(prompt: str, df: pd.DataFrame) -> List[str]:
    """
    Kullanıcı prompt'u içinde geçen Türkiye il isimlerini Türkçe karakter duyarlı
    ve kelime sınırı kontrolü ile tespit eder. İllerin metindeki geçiş sırasını korur.
    """
    p_norm = normalize_tr(prompt)
    city_list = df["il"].dropna().unique().tolist()
    
    # Şehirlerin normalize hallerini haritala
    city_norm_map = {normalize_tr(c): c for c in city_list}
    
    # Uzun şehir isimlerini önce tara (örn: 'Afyonkarahisar' vs 'Afyon')
    sorted_norm_cities = sorted(city_norm_map.keys(), key=len, reverse=True)
    
    positions = []
    working_str = p_norm
    for c_norm in sorted_norm_cities:
        pattern = r"(?<![a-z0-9])" + re.escape(c_norm) + r"(?![a-z0-9])"
        match = re.search(pattern, working_str)
        if match:
            original_city = city_norm_map[c_norm]
            positions.append((match.start(), original_city))
            # Tekrar eşleşmeyi önlemek için eşleşen kısmı boşlukla maskele
            working_str = working_str[:match.start()] + (" " * len(c_norm)) + working_str[match.end():]
            
    positions.sort(key=lambda x: x[0])
    return [c for _, c in positions]


def generate_local_response(user_prompt: str, df: pd.DataFrame) -> str:
    """
    Kullanıcı mesajını tamamen yerel kurallarla ve 81 il veri seti (df) üzerinden analiz eder.
    """
    p_norm = normalize_tr(user_prompt)
    matched_cities = detect_cities_in_prompt(user_prompt, df)

    # 1. KURAL: İKİ İL GEÇERSE YAN YANA KARŞILAŞTIR
    if len(matched_cities) >= 2:
        c1, c2 = matched_cities[0], matched_cities[1]
        df_c1 = df[df["il"] == c1]
        df_c2 = df[df["il"] == c2]

        if not df_c1.empty and not df_c2.empty:
            r1 = df_c1.iloc[0]
            r2 = df_c2.iloc[0]

            pm1 = float(r1.get("pm25", 0.0))
            pm2 = float(r2.get("pm25", 0.0))
            kat1 = pm1 / 5.0
            kat2 = pm2 / 5.0

            osb1 = int(r1.get("osb_sayisi", 0))
            osb2 = int(r2.get("osb_sayisi", 0))

            maliyet1 = float(r1.get("maliyet_milyon_tl", 0.0))
            maliyet2 = float(r2.get("maliyet_milyon_tl", 0.0))

            if pm1 < pm2:
                fark = pm2 - pm1
                oran = (fark / pm2) * 100.0 if pm2 > 0 else 0
                eval_note = f"🌿 **{c1}**, {c2}'ye kıyasla `{fark:.1f} µg/m³` (%{oran:.0f}) daha temiz bir havaya sahiptir."
            elif pm2 < pm1:
                fark = pm1 - pm2
                oran = (fark / pm1) * 100.0 if pm1 > 0 else 0
                eval_note = f"🌿 **{c2}**, {c1}'e kıyasla `{fark:.1f} µg/m³` (%{oran:.0f}) daha temiz bir havaya sahiptir."
            else:
                eval_note = "⚖️ Her iki ilin ortalama PM2.5 konsantrasyonu birbirine eşittir."

            return (
                f"⚖️ **{c1} vs {c2} Karşılaştırmalı Hava Kalitesi ve Sanayi Analizi**\n\n"
                f"| Analiz Göstergesi | **{c1}** | **{c2}** |\n"
                f"| :--- | :---: | :---: |\n"
                f"| **Coğrafi Bölge** | {r1.get('bolge', '-')} | {r2.get('bolge', '-')} |\n"
                f"| **PM2.5 Kirlilik Değeri** | `{pm1:.1f} µg/m³` | `{pm2:.1f} µg/m³` |\n"
                f"| **DSÖ Hedefine Oran (5 µg/m³)** | **{kat1:.1f}x** ({r1.get('dso_risk', '-')}) | **{kat2:.1f}x** ({r2.get('dso_risk', '-')}) |\n"
                f"| **Organize Sanayi Bölgesi (OSB)** | {osb1} adet ({r1.get('osb_alani_hektar', 0):.0f} ha) | {osb2} adet ({r2.get('osb_alani_hektar', 0):.0f} ha) |\n"
                f"| **Solunum Kaynaklı Vefat (100k)** | {r1.get('solunum_olum_100k', 0):.1f} | {r2.get('solunum_olum_100k', 0):.1f} |\n"
                f"| **Yıllık Sağlık Maliyeti** | {maliyet1:,.1f} Milyon ₺ | {maliyet2:,.1f} Milyon ₺ |\n\n"
                f"💡 **Değerlendirme:** {eval_note}"
            )

    # 2. KURAL: TEK İL GEÇERSE KARNE FORMATINDA YAZDIR
    elif len(matched_cities) == 1:
        c = matched_cities[0]
        df_c = df[df["il"] == c]

        if not df_c.empty:
            r = df_c.iloc[0]
            pm25 = float(r.get("pm25", 0.0))
            kat = pm25 / 5.0
            osb_count = int(r.get("osb_sayisi", 0))
            dso_status = str(r.get("dso_risk", "Kritik" if pm25 > 35 else "Orta"))

            return (
                f"**{c} İli Çevre & Hava Kalitesi Karnesi**\n\n"
                f"- **PM2.5 Kirlilik Değeri:** `{pm25:.1f} µg/m³`\n"
                f"- **DSÖ Durumu (Dünya Sağlık Örgütü):** **{dso_status}** (DSÖ 5 µg/m³ yıllık kılavuzunun **{kat:.1f} katı**)\n"
                f"- **Organize Sanayi Bölgesi (OSB) Sayısı:** **{osb_count} adet** ({r.get('osb_alani_hektar', 0):.0f} hektar)\n"
                f"- **Bölge & Plaka:** {r.get('bolge', '-')} &bull; Plaka Kodu: {int(r.get('plaka', 0)):02d}\n"
                f"- **Solunum Kaynaklı Vefat Oranı:** `{r.get('solunum_olum_100k', 0):.1f} / 100 bin kişi`\n"
                f"- **Tahmini Yıllık Sağlık Maliyeti:** `{r.get('maliyet_milyon_tl', 0):,.1f} Milyon ₺`"
            )

    # 3. KURAL: 'EN KİRLİ' / 'EN RİSKLİ' SORGUSU (İLK 3 İLİ LİSTELE)
    if any(k in p_norm for k in ["kirli", "riskli", "en riskli", "kotu", "en kotu", "tehlikeli", "en yuksek"]):
        top3 = df.sort_values(by="pm25", ascending=False).head(3)
        lines = []
        for i, (_, r) in enumerate(top3.iterrows()):
            kat = r["pm25"] / 5.0
            lines.append(
                f"{i+1}. **{r['il']}** ({r['bolge']}): `{r['pm25']:.1f} µg/m³` PM2.5 &bull; DSÖ sınırının **{kat:.1f} katı** &bull; {int(r['osb_sayisi'])} OSB"
            )
        return (
            "**Türkiye Genelinde Havası En Riskli (PM2.5 Seviyesi En Yüksek) 3 Şehir:**\n\n"
            + "\n".join(lines)
            + "\n\n*Neden-Sonuç Notu:* Topoğrafik çanak yapısı (inversiyon hapsi) ve yoğun kış emisyonları bu illerde kirliliği artıran en temel etkenlerdir."
        )

    # 4. KURAL: 'EN TEMİZ' SORGUSU (İLK 3 İLİ LİSTELE)
    if any(k in p_norm for k in ["temiz", "en temiz", "iyi", "en iyi", "ferah", "en dusuk", "saglikli"]):
        top3 = df.sort_values(by="pm25", ascending=True).head(3)
        lines = []
        for i, (_, r) in enumerate(top3.iterrows()):
            lines.append(
                f"{i+1}. **{r['il']}** ({r['bolge']}): `{r['pm25']:.1f} µg/m³` PM2.5 &bull; DSÖ sınırının **{r['pm25']/5.0:.1f} katı**"
            )
        return (
            "**Türkiye Genelinde Havası En Temiz (PM2.5 Seviyesi En Düşük) 3 Şehir:**\n\n"
            + "\n".join(lines)
            + "\n\n*Analiz Notu:* Yüksek rakım, güçlü rüzgar koridorları ve sanayi yoğunluğunun düşüklüğü bu illerde temiz hava kalitesini korumaktadır."
        )

    # 5. KURAL: 'MALİYET' VEYA 'FATURA' GEÇERSE TOPLAM SAĞLIK MALİYETİNİ SÖYLE
    if any(k in p_norm for k in ["maliyet", "fatura", "saglik maliyet", "ulusal saglik", "butce", "ekonomi", "tl", "harcama", "para"]):
        total_maliyet = df["maliyet_milyon_tl"].sum() if "maliyet_milyon_tl" in df.columns else 0.0
        trilyon = total_maliyet / 1000000.0
        max_city_row = df.loc[df["maliyet_milyon_tl"].idxmax()] if "maliyet_milyon_tl" in df.columns else None
        max_city_text = f"**{max_city_row['il']}** ({max_city_row['maliyet_milyon_tl']:,.0f} Milyon ₺)" if max_city_row is not None else "-"

        return (
            "**Ulusal Sağlık Faturası (Hava Kirliliğinin Türkiye Sağlık Sistemine Toplam Maliyeti):**\n\n"
            f"- **Yıllık Toplam Sağlık Maliyeti:** **{total_maliyet:,.0f} Milyon ₺** (yaklaşık **{trilyon:.2f} Trilyon ₺**)\n"
            f"- **En Yüksek Sağlık Faturasına Sahip İl:** {max_city_text} — Yüksek nüfus ve yoğun maruziyet nedeniyle.\n\n"
            "*Açıklama:* Bu tutar, TÜİK solunum sistemi kaynaklı ölüm verileri ve OECD İstatistiki Yaşam Değeri (VSL) yaklaşımı baz alınarak modellenmiştir."
        )

    # 6. KURAL: EŞLEŞMEYEN GENEL SORULARDA REHBER SUN
    return (
        "Merhaba! Ben **HavaAtlası Yerel Veri Asistanı**.\n\n"
        "Sorunuzu sistem veritabanındaki 81 il ile eşleştiremedim. Bana şu kalıplarla soru sorabilirsiniz:\n\n"
        "- **Risk Sorgusu:** *'En riskli 3 şehir hangileri?'* veya *'en kirli iller'*\n"
        "- **Temiz Hava Sorgusu:** *'En temiz iller hangileri?'* veya *'havası en temiz şehirler'*\n"
        "- **Maliyet Sorgusu:** *'Ulusal sağlık faturası ne kadar?'* veya *'toplam maliyet'*\n"
        "- **Tek Şehir Karnesi:** *'İstanbul hava kalitesi'*, *'Iğdır'*, *'Ankara durumu'*\n"
        "- **İki Şehir Kıyaslama:** *'İstanbul vs Ankara'*, *'Bursa ile İzmir kıyasla'*\n\n"
        "Ayrıca yukarıdaki **4 hazır butona** tıklayarak anında detaylı analiz alabilirsiniz!"
    )


# Geriye dönük uyumluluk ve birim testler için alias
generate_assistant_response = generate_local_response


def render_chat_assistant_page(df: pd.DataFrame):
    """
    Yerel (offline) Streamlit Chatbot Arayüzü:
    - Sohbet geçmişi st.session_state.messages listesinde tutulur.
    - 4 hazır buton st.columns(4) ile sohbet alanının üstünde konumlandırılır.
    - Harici API kullanılmaz.
    """
    # Özel Koyu Tema & HavaAtlası Stilleri
    st.markdown("""
    <style>
    .chat-header {
        background: linear-gradient(135deg, #091a32 0%, #0d2446 100%);
        border: 1px solid #143763;
        border-radius: 14px;
        padding: 16px 22px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
    }
    div[data-testid="stChatMessage"] {
        background-color: #0b1a30 !important;
        border: 1px solid #143763 !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        background-color: #112747 !important;
        border-color: #1e4a80 !important;
    }
    div[data-testid="stChatInput"] {
        border-color: #1e4a80 !important;
    }
    div[data-testid="stChatInput"] textarea {
        background-color: #0b1a30 !important;
        color: #f8fafc !important;
    }
    .quick-btn-box button {
        border: 1px solid #1e4a80 !important;
        background-color: #0d2446 !important;
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        transition: all 0.2s ease-in-out !important;
        height: 44px !important;
        white-space: nowrap !important;
    }
    .quick-btn-box button:hover {
        border-color: #00e5db !important;
        background-color: #11345f !important;
        color: #00e5db !important;
        box-shadow: 0 0 12px rgba(0, 229, 219, 0.25) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Başlık ve Bilgi Kartı
    col_head, col_clr = st.columns([5, 1])
    with col_head:
        st.markdown("""
        <div class='chat-header'>
            <div style='display:flex; align-items:center; gap:14px;'>
                <div style='background:rgba(0,229,219,0.15); color:#00e5db; width:36px; height:36px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-weight:800; font-family:monospace; font-size:13px; border:1px solid rgba(0,229,219,0.3);'>
                    AI
                </div>
                <div>
                    <h3 style='color:#f8fafc; margin:0; font-size:20px; font-weight:800; letter-spacing:0.3px;'>
                        HavaAtlası Yerel Veri Asistanı
                    </h3>
                    <div style='color:#94a3b8; font-size:12.5px; margin-top:3px;'>
                        81 İl Hava Kalitesi, Sanayi Baskısı ve Halk Sağlığı Analitiği &bull; %100 Çevrimdışı & Yerel Motor
                    </div>
                </div>
            </div>
            <span style='background:rgba(0,229,219,0.12); border:1px solid #00e5db; color:#00e5db; padding:6px 14px; border-radius:20px; font-size:12px; font-weight:700;'>
                <span style='display:inline-block; width:7px; height:7px; border-radius:50%; background:#00e5db; margin-right:6px;'></span> Yerel Veri Tabanı Aktif
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col_clr:
        if st.button("Sohbeti Temizle", key="btn_reset_chat", use_container_width=True):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": (
                        "Merhaba! Ben **HavaAtlası Yerel Veri Asistanı**.\n\n"
                        "81 ilimizin PM2.5 hava kirliliği, Organize Sanayi Bölgesi (OSB) sayıları ve TÜİK sağlık maliyeti verileriyle "
                        "tamamen çevrimdışı ve yerel olarak çalışıyorum.\n\n"
                        "Aşağıdaki **4 hazır butonu** seçebilir ya da merak ettiğiniz şehri doğrudan yazabilirsiniz."
                    )
                }
            ]
            st.rerun()

    # Sohbet Geçmişi Başlatma (st.session_state.messages)
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Merhaba! Ben **HavaAtlası Yerel Veri Asistanı**.\n\n"
                    "81 ilimizin PM2.5 hava kirliliği, Organize Sanayi Bölgesi (OSB) sayıları ve TÜİK sağlık faturası verileriyle "
                    "tamamen çevrimdışı ve yerel olarak çalışıyorum.\n\n"
                    "Aşağıdaki **4 hazır butonu** kullanabilir ya da dilediğiniz ili yazıp analiz edebilirsiniz:\n"
                    "- *'İstanbul vs Ankara Kıyasla'* (İki ili yan yana karşılaştırır)\n"
                    "- *'Iğdır hava kirliliği'* (İl çevre ve sağlık karnesini döker)\n"
                    "- *'En riskli 3 şehir'* veya *'En temiz iller'*\n"
                    "- *'Ulusal sağlık faturası ne kadar?'*"
                )
            }
        ]

    # Sohbet Mesajları Konteyneri (Üst Bölüm)
    chat_container = st.container()

    # Sohbet Alanının Üstünde 4 Hazır Buton (st.columns(4))
    st.markdown("<div style='margin-top: 10px; margin-bottom: 6px; font-size: 12px; color: #94a3b8; font-weight: 700; letter-spacing: 0.5px;'>HIZLI ANALİZ SEÇENEKLERİ:</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    btn_prompt = None

    with c1:
        st.markdown("<div class='quick-btn-box'>", unsafe_allow_html=True)
        if st.button("En Riskli 3 Şehir", key="btn_riskli_3", use_container_width=True):
            btn_prompt = "En Riskli 3 Şehir"
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='quick-btn-box'>", unsafe_allow_html=True)
        if st.button("En Temiz 3 Şehir", key="btn_temiz_3", use_container_width=True):
            btn_prompt = "En Temiz 3 Şehir"
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown("<div class='quick-btn-box'>", unsafe_allow_html=True)
        if st.button("Ulusal Sağlık Faturası", key="btn_saglik_faturasi", use_container_width=True):
            btn_prompt = "Ulusal Sağlık Faturası"
        st.markdown("</div>", unsafe_allow_html=True)

    with c4:
        st.markdown("<div class='quick-btn-box'>", unsafe_allow_html=True)
        if st.button("İstanbul vs Ankara Kıyasla", key="btn_ist_ank_vs", use_container_width=True):
            btn_prompt = "İstanbul vs Ankara Kıyasla"
        st.markdown("</div>", unsafe_allow_html=True)

    # Sohbet Giriş Kutusu (st.chat_input)
    user_input = st.chat_input("Hava kalitesi, şehir kıyaslaması veya sağlık faturası hakkında bir soru sorun...")

    # Aktif Girdi: Buton tıklandıysa butonun metni, yoksa metin girişi
    active_prompt = btn_prompt if btn_prompt else user_input

    # Sohbet Geçmişini ve Yeni Mesajı Chat Konteynerine Bas
    with chat_container:
        # Geçmiş mesajları sırayla ekranda göster
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Kullanıcı girdisi veya buton tetiklemesi varsa işle
        if active_prompt:
            # 1. Kullanıcı girdisini geçmişe ekle ve ekrana bas
            st.session_state.messages.append({"role": "user", "content": active_prompt})
            with st.chat_message("user"):
                st.markdown(active_prompt)

            # 2. Yerel kural motoruyla yanıtı üret ve asistan olarak ekrana bas
            response_text = generate_local_response(active_prompt, df)
            with st.chat_message("assistant"):
                st.markdown(response_text)

            # 3. Asistan yanıtını geçmişe ekle
            st.session_state.messages.append({"role": "assistant", "content": response_text})
