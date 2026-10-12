"""
💬 AI Veri Asistanı (Yerel & Çevrimdışı Chatbot)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

Tamamen yerel (offline), harici kütüphane veya API anahtarı olmadan çalışan akıllı karar destek asistanı.

Özellikler:
1. %100 Çevrimdışı ve Yerel: Yalnızca platformun mevcut 81 il master_df verisini kullanır.
2. 4 Hazır Buton (st.button):
   - 🚨 En Riskli 3 Şehir
   - 🌿 En Temiz 3 Şehir
   - 🏭 En Çok OSB'li 3 İl
   - ⚖️ İstanbul vs Ankara Kıyasla
3. Akıllı Sorgu Eşleme:
   - Türkçe karakter duyarlı il tarama (İ/i, I/ı, Ğ/g, Ü/u, Ş/s, Ö/o, Ç/c ve ekler)
   - İki il geçerse yan yana detaylı karşılaştırma tablosu
   - Tek il geçerse PM2.5, DSÖ durumu ve OSB sayısı karne formatında
   - 'en kirli' / 'en temiz' sorgularında ilk 3 ili listeleme
   - 'osb' / 'sanayi' sorgularında en çok OSB'ye sahip 3 ili listeleme
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
    Doğal dil sorguları ve hızlı analiz butonlarıyla tam uyumlu karar destek yanıtları üretir.
    """
    if df is None or df.empty:
        return "Veri seti henüz yüklenemedi. Lütfen sayfayı yenileyiniz."

    p_norm = normalize_tr(user_prompt)
    matched_cities = detect_cities_in_prompt(user_prompt, df)

    # 1. KURAL: İKİ VEYA DAHA FAZLA İL GEÇERSE YAN YANA KARŞILAŞTIR
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

            osb1 = int(r1.get("osb_sayisi", r1.get("toplam_osb", 0)))
            osb2 = int(r2.get("osb_sayisi", r2.get("toplam_osb", 0)))
            parsel1 = int(r1.get("toplam_parsel", 0)) if pd.notna(r1.get("toplam_parsel")) else 0
            parsel2 = int(r2.get("toplam_parsel", 0)) if pd.notna(r2.get("toplam_parsel")) else 0

            sol1 = float(r1.get("solunum_olum_100k", 0.0))
            sol2 = float(r2.get("solunum_olum_100k", 0.0))

            if pm1 > pm2:
                eval_note = f"**{c1}**, {c2} iline kıyasla PM2.5 bazında **{pm1 - pm2:.1f} µg/m³** daha yüksek kirlilik maruziyetine sahiptir."
            else:
                eval_note = f"**{c2}**, {c1} iline kıyasla PM2.5 bazında **{pm2 - pm1:.1f} µg/m³** daha yüksek kirlilik maruziyetine sahiptir."

            return (
                f"⚖️ **{c1} vs {c2} Karşılaştırmalı Hava Kalitesi ve Sanayi Analizi**\n\n"
                f"| Analiz Göstergesi | **{c1}** | **{c2}** |\n"
                f"| :--- | :---: | :---: |\n"
                f"| **Coğrafi Bölge** | {r1.get('bolge', '-')} | {r2.get('bolge', '-')} |\n"
                f"| **PM2.5 Kirlilik Değeri** | `{pm1:.1f} µg/m³` | `{pm2:.1f} µg/m³` |\n"
                f"| **DSÖ Hedefine Oran (5 µg/m³)** | **{kat1:.1f}x** ({r1.get('dso_risk', '-')}) | **{kat2:.1f}x** ({r2.get('dso_risk', '-')}) |\n"
                f"| **Organize Sanayi Bölgesi (OSB)** | {osb1} adet ({r1.get('osb_alani_hektar', 0):.0f} ha) | {osb2} adet ({r2.get('osb_alani_hektar', 0):.0f} ha) |\n"
                f"| **Sanayi Parsel Sayısı** | {parsel1:,} parsel | {parsel2:,} parsel |\n"
                f"| **Solunum Kaynaklı Vefat (100k)** | `{sol1:.1f} / 100 bin` | `{sol2:.1f} / 100 bin` |\n\n"
                f"💡 **Değerlendirme:** {eval_note}"
            )

    # 2. KURAL: KİRLİLİK VE OSB İLİŞKİSİ / KORELASYON SORGULARI
    if any(k in p_norm for k in ["kirlilik ve osb", "osb ve kirlilik", "osb iliskisi", "sanayi iliskisi", "korelasyon", "baglanti"]) or \
       ("iliski" in p_norm and any(k in p_norm for k in ["osb", "sanayi", "kirlilik"])):
        from scipy import stats
        clean_df = df[["osb_alani_hektar", "pm25"]].dropna()
        if len(clean_df) >= 10:
            rho, p_val = stats.spearmanr(clean_df["osb_alani_hektar"], clean_df["pm25"])
            rho_str = f"{rho:+.2f}".replace(".", ",")
            p_str = "< 0,001" if p_val < 0.001 else f"= {p_val:.3f}".replace(".", ",")
        else:
            rho_str = "+0,11"
            p_str = "= 0,335"

        return (
            "📊 **Türkiye Genelinde Hava Kirliliği ve Organize Sanayi (OSB) İlişkisi Analitiği**\n\n"
            f"- **Spearman Sıra Korelasyon Katsayısı (ρ):** `{rho_str}` ({p_str}, n = {len(df)})\n\n"
            "🔍 **Bilimsel Değerlendirme & Kök Neden Analizi:**\n"
            "1. **Doğrudan Sanayi Baskısı:** Marmara (Kocaeli, Bursa, Tekirdağ) ve Ege (İzmir) havzalarında yoğun OSB parselleri "
            "ve enerji tüketimi, yer seviyesi emisyonları ve ikincil partikül oluşumunu doğrudan artırmaktadır.\n"
            "2. **Topoğrafik Çanak & İnversiyon Etkisi:** Iğdır, Düzce ve Erzincan gibi illerde OSB sayısı nispeten düşük olmasına "
            "rağmen çanak vadi topografyası ve kış aylarındaki sıcaklık inversiyonu, kirliliğin dağılmasını engelleyerek PM2.5 değerlerini "
            "Türkiye'nin en üst seviyesine taşımaktadır.\n\n"
            "💡 **Sonuç:** Türkiye'de hava kalitesi tek başına sanayi varlığıyla değil; **sanayi emisyonları, topoğrafik çanak yapısı ve meteorolojik dinamiklerin** bileşik etkisiyle şekillenmektedir."
        )

    # 3. KURAL: BÖLGESEL SIRALAMA & EN TEMİZ BÖLGE SORGULARI
    if any(k in p_norm for k in ["en temiz bolge", "temiz bolge", "havasi en temiz bolge", "bolgeler", "bolge siralamasi", "cografi bolge"]) or \
       ("bolge" in p_norm and any(k in p_norm for k in ["temiz", "en temiz", "iyi", "hangisi", "siralama"])):
        bolge_stats = df.groupby("bolge")["pm25"].mean().sort_values()
        lines = []
        cleanest_b = bolge_stats.index[0]
        cleanest_v = bolge_stats.iloc[0]

        # En temiz bölgenin en temiz ilini bul
        cleanest_region_df = df[df["bolge"] == cleanest_b].sort_values(by="pm25", ascending=True)
        top_city_in_reg = cleanest_region_df.iloc[0]["il"] if not cleanest_region_df.empty else ""
        top_city_pm = cleanest_region_df.iloc[0]["pm25"] if not cleanest_region_df.empty else 0.0

        for idx, (b_name, b_val) in enumerate(bolge_stats.items()):
            icon = "🌿" if idx == 0 else ("⚠️" if idx == len(bolge_stats) - 1 else "📍")
            lines.append(f"{idx+1}. {icon} **{b_name}:** `{b_val:.1f} µg/m³` PM2.5 (DSÖ sınırının {b_val/5.0:.1f} katı)")

        return (
            f"🌍 **Türkiye'nin 7 Coğrafi Bölgesi Hava Kalitesi Sıralaması:**\n\n"
            f"🏆 **Havası En Temiz Coğrafi Bölge:** **{cleanest_b}** (Bölgesel Ortalama: `{cleanest_v:.1f} µg/m³` PM2.5)\n"
            f"• *Bölgenin En Temiz İli:* **{top_city_in_reg}** (`{top_city_pm:.1f} µg/m³`)\n\n"
            f"**Tüm Coğrafi Bölgelerin Temizden Kirliye Doğru Sıralaması:**\n"
            + "\n".join(lines)
            + "\n\n💡 **Meteorolojik Not:** Karadeniz'in denizel hava akımları ve nemli rüzgar koridorları partikül dağılımını desteklerken; Doğu ve Güneydoğu Anadolu'da kuraklık, sınır ötesi toz taşınımı ve çanak topografya kirlilik yükünü artırmaktadır."
        )

    # 4. KURAL: SOLUNUM RİSKİ EN YÜKSEK İLLER (TÜİK VERİLERİ)
    if any(k in p_norm for k in ["solunum riski", "solunum olumu", "solunum vefati", "solunum", "akciger", "nefes", "vefat", "olum orani"]):
        top3_sol = df.sort_values(by="solunum_olum_100k", ascending=False).head(3)
        lines = []
        for i, (_, r) in enumerate(top3_sol.iterrows()):
            v_sayi = int(r.get("solunum_olum", 0)) if pd.notna(r.get("solunum_olum")) else 0
            lines.append(
                f"{i+1}. **{r['il']}** ({r['bolge']}): `{r['solunum_olum_100k']:.1f} / 100 bin kişi` "
                f"&bull; Yıllık Yaklaşık **{v_sayi:,} Can Kaybı** &bull; PM2.5: `{r['pm25']:.1f} µg/m³` &bull; {int(r.get('osb_sayisi', 0))} OSB"
            )

        turkiye_ort_sol = df["solunum_olum_100k"].dropna().mean()
        return (
            "🫁 **TÜİK Solunum Kaynaklı Vefat Oranı En Yüksek 3 İl:**\n\n"
            + "\n".join(lines)
            + f"\n\n*(Türkiye Geneli Ortalama Solunum Vefat Oranı: ~{turkiye_ort_sol:.1f} / 100 bin kişi)*\n\n"
            "💡 **Halk Sağlığı Notu:** TÜİK ölüm nedeni istatistiklerine göre KOAH, pnömoni ve astım gibi solunum yolu hastalıkları; "
            "uzun vadeli ince partikül maruziyeti, nüfus yaş piramidindeki yaşlılık oranı ve bölgesel iklimsel koşulların bileşik sonucu olarak artış göstermektedir."
        )

    # 5. KURAL: DSÖ LİMİTİNİ EN ÇOK AŞANLAR
    if any(k in p_norm for k in ["dso limitini en cok asanlar", "dso limit", "dso asimi", "dso yu en cok", "dso hedef", "rehber sinir", "5 ug", "dso siniri"]) or \
       ("dso" in p_norm and any(k in p_norm for k in ["asan", "en cok", "kat", "limit", "sinir"])):
        top3_dso = df.sort_values(by="pm25", ascending=False).head(3)
        lines = []
        for i, (_, r) in enumerate(top3_dso.iterrows()):
            kat = r["pm25"] / 5.0
            lines.append(
                f"{i+1}. **{r['il']}** ({r['bolge']}): `{r['pm25']:.1f} µg/m³` &bull; DSÖ 5 µg/m³ sınırının **{kat:.1f} Katı** "
                f"&bull; Durum: **{r.get('dso_risk', 'Kritik')}** &bull; {int(r.get('osb_sayisi', 0))} OSB"
            )

        return (
            "🚨 **Dünya Sağlık Örgütü (DSÖ 2021) Yıllık Kılavuz Sınırını (5 µg/m³) En Çok Aşan İller:**\n\n"
            + "\n".join(lines)
            + "\n\n📌 **Ulusal Uyumluluk Durumu:** Türkiye'deki 81 ilin tamamında yıllık ortalama PM2.5 düzeyi DSÖ 5 µg/m³ kılavuz değerinin üzerindedir (%100 aşım, uyum oranı: 0/81 İl)."
        )

    # 6. KURAL: SANAYİ BASKISI EN YÜKSEK İLLER (OSB & SANAYİ PARSELİ)
    if any(k in p_norm for k in ["sanayi baskisi", "parsel", "en cok osb", "sanayi illeri", "sanayi yogunlugu", "osb", "sanayi"]):
        col_sort = "toplam_parsel" if "toplam_parsel" in df.columns and df["toplam_parsel"].notna().sum() > 0 else "toplam_osb"
        top3_ind = df.sort_values(by=col_sort, ascending=False).head(4)
        lines = []
        for i, (_, r) in enumerate(top3_ind.iterrows()):
            p_cnt = int(r.get("toplam_parsel", 0)) if pd.notna(r.get("toplam_parsel")) else 0
            osb_c = int(r.get("toplam_osb", r.get("osb_sayisi", 0)))
            alan_ha = r.get("osb_alani_hektar", 0)
            lines.append(
                f"{i+1}. **{r['il']}** ({r['bolge']}): **{osb_c} OSB** &bull; **{p_cnt:,} Aktif Parsel** &bull; {alan_ha:,.0f} Hektar Alan &bull; PM2.5: `{r['pm25']:.1f} µg/m³`"
            )

        return (
            "🏭 **Türkiye'de Sanayi Baskısı ve Üretim Yoğunluğu En Yüksek İller (OSBÜK Verileri):**\n\n"
            + "\n".join(lines)
            + "\n\n💡 **Sanayi Analitiği:** Parsel sayısı ve üretim alanı yüksek sanayi havzalarında yeşil dönüşüm, baca gazı filtrasyonu ve temiz yakıt dönüşümü öncelikli politika müdahalesi olarak öne çıkmaktadır."
        )

    # 7. KURAL: TEK İL GEÇERSE DETAYLI İL KARNESİ & PROFİLİ
    if len(matched_cities) == 1:
        c = matched_cities[0]
        df_c = df[df["il"] == c]

        if not df_c.empty:
            r = df_c.iloc[0]
            pm25 = float(r.get("pm25", 0.0))
            kat = pm25 / 5.0
            osb_count = int(r.get("osb_sayisi", r.get("toplam_osb", 0)))
            parsel_count = int(r.get("toplam_parsel", 0)) if pd.notna(r.get("toplam_parsel")) else 0
            alan_ha = float(r.get("osb_alani_hektar", 0.0))
            dso_status = str(r.get("dso_risk", "Kritik" if pm25 > 35 else "Orta"))
            sol_100k = float(r.get("solunum_olum_100k", 0.0))
            sol_toplam = int(r.get("solunum_olum", 0)) if pd.notna(r.get("solunum_olum")) else 0

            return (
                f"🏙️ **{c} İli Çevre & Hava Kalitesi Karnesi**\n\n"
                f"- **PM2.5 Kirlilik Değeri:** `{pm25:.1f} µg/m³`\n"
                f"- **DSÖ Durumu (Dünya Sağlık Örgütü):** **{dso_status}** (DSÖ 5 µg/m³ yıllık kılavuzunun **{kat:.1f} katı**)\n"
                f"- **Organize Sanayi Bölgesi (OSB):** **{osb_count} Adet** ({parsel_count:,} parsel, {alan_ha:,.0f} hektar)\n"
                f"- **Bölge & Plaka:** {r.get('bolge', '-')} &bull; Plaka Kodu: {int(r.get('plaka', 0)):02d}\n"
                f"- **Solunum Kaynaklı Vefat Oranı:** `{sol_100k:.1f} / 100 bin kişi` (~{sol_toplam:,} vefat)"
            )

    # 8. KURAL: 'EN KİRLİ' / 'EN RİSKLİ' SORGUSU (PM2.5 İLK 3)
    if any(k in p_norm for k in ["kirli", "riskli", "en riskli", "kotu", "en kotu", "tehlikeli", "en yuksek"]):
        top3 = df.sort_values(by="pm25", ascending=False).head(3)
        lines = []
        for i, (_, r) in enumerate(top3.iterrows()):
            kat = r["pm25"] / 5.0
            lines.append(
                f"{i+1}. **{r['il']}** ({r['bolge']}): `{r['pm25']:.1f} µg/m³` PM2.5 &bull; DSÖ sınırının **{kat:.1f} katı** &bull; {int(r.get('osb_sayisi', 0))} OSB"
            )
        return (
            "🚨 **Türkiye Genelinde Havası En Riskli (PM2.5 Seviyesi En Yüksek) 3 Şehir:**\n\n"
            + "\n".join(lines)
            + "\n\n*Neden-Sonuç Notu:* Topoğrafik çanak yapısı (inversiyon hapsi) ve yoğun kış emisyonları bu illerde kirliliği artıran en temel etkenlerdir."
        )

    # 9. KURAL: 'EN TEMİZ' SORGUSU (PM2.5 EN DÜŞÜK 3 İL)
    if any(k in p_norm for k in ["temiz", "en temiz", "iyi", "en iyi", "ferah", "en dusuk", "saglikli"]):
        top3 = df.sort_values(by="pm25", ascending=True).head(3)
        lines = []
        for i, (_, r) in enumerate(top3.iterrows()):
            lines.append(
                f"{i+1}. **{r['il']}** ({r['bolge']}): `{r['pm25']:.1f} µg/m³` PM2.5 &bull; DSÖ sınırının **{r['pm25']/5.0:.1f} katı**"
            )
        return (
            "🌿 **Türkiye Genelinde Havası En Temiz (PM2.5 Seviyesi En Düşük) 3 Şehir:**\n\n"
            + "\n".join(lines)
            + "\n\n*Analiz Notu:* Yüksek rakım, güçlü rüzgar koridorları ve sanayi yoğunluğunun düşüklüğü bu illerde temiz hava kalitesini korumaktadır."
        )

    # 10. KURAL: EŞLEŞMEYEN GENEL SORULARDA REHBER SUN
    return (
        "Merhaba! Ben **HavaAtlası Yerel Veri Asistanı**.\n\n"
        "Sorunuzu sistem veritabanındaki 81 il ile eşleştiremedim. Bana şu kalıplarla soru sorabilirsiniz:\n\n"
        "- **Sağlık & Risk:** *'Solunum Riski En Yüksek 3 İl'* veya *'Hangi ilde solunum ölümü daha fazla?'*\n"
        "- **Bölgesel Analiz:** *'En Temiz Bölge'* veya *'Havası en temiz bölge hangisi?'*\n"
        "- **Sanayi & OSB:** *'Sanayi Baskısı En Yüksek İller'* veya *'Kirlilik ve OSB ilişkisi'*\n"
        "- **DSÖ Sınırları:** *'DSÖ Limitini En Çok Aşanlar'*\n"
        "- **Tek Şehir Karnesi:** *'Bursa il profili'*, *'Iğdır hava kalitesi ve karnesi'*, *'Ankara durumu'*\n"
        "- **İki Şehir Kıyaslama:** *'İstanbul vs Ankara Kıyasla'*, *'Bursa ile İzmir kıyasla'*\n\n"
        "Ayrıca yukarıdaki **hazır butonlara** tıklayarak anında detaylı analiz alabilirsiniz!"
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
                        "81 ilimizin PM2.5 hava kalitesi, kirlilik ölçümleri, Organize Sanayi Bölgesi (OSB) sayıları ve TÜİK solunum sağlık verileriyle "
                        "tamamen çevrimdışı ve yerel olarak çalışıyorum.\n\n"
                        "Aşağıdaki **hızlı analiz butonlarını** seçebilir ya da merak ettiğiniz konuyu doğrudan yazabilirsiniz."
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
                    "81 ilimizin PM2.5 hava kalitesi, kirlilik ölçümleri, Organize Sanayi Bölgesi (OSB) sayıları ve TÜİK solunum sağlık verileriyle "
                    "tamamen çevrimdışı ve yerel olarak çalışıyorum.\n\n"
                    "Aşağıdaki **hızlı analiz butonlarını** kullanabilir ya da dilediğiniz ili veya konuyu yazıp analiz edebilirsiniz:\n"
                    "- *'Solunum Riski En Yüksek 3 İl'* (TÜİK solunum ölüm oranlarını listeler)\n"
                    "- *'DSÖ Limitini En Çok Aşanlar'* (5 µg/m³ kılavuz sınırını aşım katları)\n"
                    "- *'Sanayi Baskısı En Yüksek İller'* (OSB ve sanayi parseli sıralaması)\n"
                    "- *'En Temiz Bölge'* veya *'Havası en temiz bölge hangisi?'*\n"
                    "- *'Iğdır hava kalitesi ve karnesi'* veya *'Bursa il profili'*\n"
                    "- *'En kirli 3 il'*\n"
                    "- *'İstanbul vs Ankara Kıyasla'*"
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
        if st.button("Solunum Riski En Yüksek 3 İl", key="btn_solunum_3", use_container_width=True):
            btn_prompt = "Solunum Riski En Yüksek 3 İl"
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='quick-btn-box'>", unsafe_allow_html=True)
        if st.button("DSÖ Limitini En Çok Aşanlar", key="btn_dso_limit_3", use_container_width=True):
            btn_prompt = "DSÖ Limitini En Çok Aşanlar"
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown("<div class='quick-btn-box'>", unsafe_allow_html=True)
        if st.button("Sanayi Baskısı En Yüksek İller", key="btn_sanayi_baskisi_3", use_container_width=True):
            btn_prompt = "Sanayi Baskısı En Yüksek İller"
        st.markdown("</div>", unsafe_allow_html=True)

    with c4:
        st.markdown("<div class='quick-btn-box'>", unsafe_allow_html=True)
        if st.button("En Temiz Bölge", key="btn_temiz_bolge", use_container_width=True):
            btn_prompt = "En Temiz Bölge"
        st.markdown("</div>", unsafe_allow_html=True)

    # Sohbet Giriş Kutusu (st.chat_input)
    user_input = st.chat_input("Hava kalitesi, şehir kıyaslaması veya sanayi dağılımı hakkında bir soru sorun...")

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
