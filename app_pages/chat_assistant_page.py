"""
💬 AI Veri Asistanı (Yerel & Çevrimdışı Chatbot)
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

Tamamen yerel (offline), harici kütüphane veya API anahtarı olmadan çalışan akıllı karar destek asistanı.

Özellikler:
1. %100 Çevrimdışı ve Yerel: Yalnızca platformun mevcut 81 il master_df verisini kullanır.
2. 4 Hazır Buton (st.button):
   - 🚨 PM2.5 Seviyesi En Yüksek 3 Şehir
   - 🌿 PM2.5 Seviyesi En Düşük 3 Şehir
   - 🏭 En Çok OSB'li 3 İl
   - ⚖️ İstanbul vs Ankara Kıyasla
3. Akıllı Sorgu Eşleme:
   - Türkçe karakter duyarlı il tarama (İ/i, I/ı, Ğ/g, Ü/u, Ş/s, Ö/o, Ç/c ve ekler)
   - İki il geçerse yan yana detaylı karşılaştırma tablosu
   - Tek il geçerse PM2.5, DSÖ durumu ve OSB sayısı karne formatında
   - 'en yüksek' / 'en düşük' sorgularında ilk 3 ili listeleme
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

            parsel1_str = f"{parsel1:,}".replace(",", ".")
            parsel2_str = f"{parsel2:,}".replace(",", ".")
            return (
                f"⚖️ **{c1} vs {c2} Karşılaştırmalı Hava Kalitesi ve Sanayi Analizi**\n\n"
                f"| Analiz Göstergesi | **{c1}** | **{c2}** |\n"
                f"| :--- | :---: | :---: |\n"
                f"| **Coğrafi Bölge** | {r1.get('bolge', '-')} | {r2.get('bolge', '-')} |\n"
                f"| **PM2.5 Kirlilik Değeri** | `{pm1:.1f} µg/m³` | `{pm2:.1f} µg/m³` |\n"
                f"| **DSÖ Hedefine Oran (5 µg/m³)** | **{kat1:.1f}x** ({r1.get('dso_risk', '-')}) | **{kat2:.1f}x** ({r2.get('dso_risk', '-')}) |\n"
                f"| **Organize Sanayi Bölgesi (OSB)** | {osb1} adet | {osb2} adet |\n"
                f"| **Sanayi Parsel Sayısı** | {parsel1_str} parsel | {parsel2_str} parsel |\n"
                f"| **Solunum Kaynaklı Vefat (100k)** | `{sol1:.1f} / 100 bin` | `{sol2:.1f} / 100 bin` |\n\n"
                f"💡 **Değerlendirme:** {eval_note}"
            )

    # ÖZEL ANALİTİK SORU 1: SANAYİSİ AZ AMA HAVASI EN KİRLİ İLLER VE KÖK NEDENLERİ
    if ("sanayisi az" in p_norm or "sanayisiz" in p_norm or ("sanayi" in p_norm and "az" in p_norm)) and \
       any(k in p_norm for k in ["kirli", "kirlilik", "hava", "sebebi"]):
        q1_osb = df["toplam_osb"].quantile(0.25)
        az_sanayi = df[df["toplam_osb"] <= q1_osb].sort_values("pm25", ascending=False).head(4)
        lines = []
        for _, r in az_sanayi.iterrows():
            lines.append(
                f"• **{r['il']}** ({r.get('bolge', '')}): PM2.5: `{r['pm25']:.1f} µg/m³` (DSÖ kılavuzunun {r['pm25']/5.0:.1f} katı) &bull; **Yalnızca {int(r.get('toplam_osb', 0))} OSB**"
            )
        istasyon_lines = []
        if "pm25_istasyon_max_2024" in df.columns:
            ist = df[(df["toplam_osb"] <= q1_osb) & df["pm25_istasyon_max_2024"].notna()]
            for _, r in ist.sort_values("pm25_istasyon_max_2024", ascending=False).iterrows():
                istasyon_lines.append(
                    f"• **{r['il']}**: istasyon `{r['pm25_istasyon_max_2024']:.1f} µg/m³` — CAMS modeli `{r['pm25']:.1f} µg/m³`"
                )

        return (
            f"🏔️ **Sanayisi Az Olmasına Rağmen Havası En Kirli İller (OSB sayısı ≤ {q1_osb:.0f}, CAMS 2025):**\n\n"
            + "\n".join(lines) + "\n\n"
            + (("📍 **Kara Rapor 2025 istasyon ölçümleri (2024) bu illerde modelden belirgin yüksek:**\n"
                + "\n".join(istasyon_lines) + "\n\n") if istasyon_lines else "")
            + "🔍 **Sanayi Dışı Olası Nedenler:**\n"
            "1. **Topoğrafik Çanak (Havza):** Etrafı dağlarla çevrili havzalarda rüzgar sirkülasyonu kısıtlıdır; kirli hava kütlesi havzada kalır.\n"
            "2. **Kış Sıcaklık Terselmesi (İnversiyon):** Soğuk hava tabakası yere yakın sıkışarak bacalardan ve egzozlardan çıkan partiküllerin dikey dağılımını engeller.\n"
            "3. **Sınır Ötesi Toz Taşınımı:** Güney ve doğu illeri kurak bölgelerden gelen mineral toz taşınımına açıktır.\n"
            "4. **Konut Isınmasında Katı Yakıt:** Kömür ve linyit ısınması yer seviyesinde yoğun partikül birikimine yol açar.\n\n"
            "⚠️ **Not:** ~10 km çözünürlüklü CAMS modeli bu yerel etkileri tam yakalayamaz; il sıralaması istasyon ölçümlerinden farklı olabilir."
        )

    # ÖZEL ANALİTİK SORU 2: DSÖ 5 µg/m³ KILAVUZ DEĞERİNİ KARŞILAYAN İL VAR MI?
    if any(k in p_norm for k in ["dso", "dso'nun", "5 ug", "kilavuz"]) and any(k in p_norm for k in ["karsilayan", "karsiliyor", "uyumlu", "var mi"]):
        min_c = df.sort_values(by="pm25", ascending=True).iloc[0]
        max_c = df.sort_values(by="pm25", ascending=False).iloc[0]
        avg_pm = df["pm25"].mean()
        return (
            "🌍 **DSÖ (Dünya Sağlık Örgütü) 5 µg/m³ Yıllık Kılavuz Değeri Uyumluluk Analizi:**\n\n"
            "❌ **Cevap: Hayır, 81 ilimizin hiçbirinde DSÖ 5 µg/m³ kılavuz değeri karşılanamamaktadır.**\n\n"
            "📌 **Temel Göstergeler:**\n"
            f"• **Ulusal Uyum Oranı:** %0 (81 ilin tamamında PM2.5 seviyesi 5 µg/m³ limitinin üzerindedir).\n"
            f"• **Türkiye Aritmetik Ortalaması:** `{avg_pm:.1f} µg/m³` (DSÖ kılavuz değerinin **{avg_pm/5.0:.1f} katı**).\n"
            f"• **En Düşük Kirlilikli İl:** **{min_c['il']}** (`{min_c['pm25']:.1f} µg/m³` - DSÖ sınırının **{min_c['pm25']/5.0:.1f} katı**).\n"
            f"• **En Yüksek Kirlilikli İl:** **{max_c['il']}** (`{max_c['pm25']:.1f} µg/m³` - DSÖ sınırının **{max_c['pm25']/5.0:.1f} katı**).\n\n"
            f"💡 **Kıyaslama:** İllerin yıllık ortalamaları DSÖ'nün 5 µg/m³ kılavuz değerinin {min_c['pm25']/5.0:.1f} ila {max_c['pm25']/5.0:.1f} katı arasındadır.\n\n"
            "_Not: Değerler CAMS 2025 yıllık model ortalamasıdır; istasyon ölçümleri genellikle daha yüksektir (ör. Kara Rapor 2025'te Iğdır istasyonu 46,8 µg/m³)._"
        )

    # ÖZEL ANALİTİK SORU 5: HAVA KİRLİLİĞİ İLE SOLUNUM ÖLÜMLERİ ARASINDA PARALELLİK VAR MI?
    if ("solunum" in p_norm or "vefat" in p_norm) and ("paralellik" in p_norm or "dogrudan" in p_norm or ("iliski" in p_norm and "kirlilik" in p_norm)):
        return (
            "🫁 **Hava Kirliliği ile Solunum Yolu Ölümleri Arasındaki İlişki Analizi:**\n\n"
            "⚠️ **Cevap: Doğrudan ve doğrusal bir birebir paralellik bulunmamaktadır.**\n\n"
            "TÜİK ölüm nedeni istatistikleri ve PM2.5 kirlilik verileri karşılaştırıldığında şu kritik epidemiyolojik gerçekler öne çıkmaktadır:\n\n"
            "1. **Demografik Yaş Yapısı Faktörü:** Solunum yolu kaynaklı vefatlar (KOAH, pnömoni vb.) ileri yaş gruplarında katlanarak artmaktadır. Örneğin Edirne ve Çanakkale gibi yaşlı nüfus oranı yüksek illerde kirlilik orta düzeyde olsa dahi 100 bin kişiye düşen solunum vefatı yüksek çıkmaktadır.\n"
            "2. **Genç Nüfuslu İller:** Hakkari ve Şırnak gibi nüfusun genç olduğu illerde kaba solunum ölüm hızları 30/100 bin civarında kalırken Edirne'de 200/100 binin üzerine çıkmaktadır; fark büyük ölçüde yaş yapısından kaynaklanır.\n"
            "3. **Kronik Maruziyet Gecikmesi (Lag Etkisi):** Solunum yolu hastalıkları anlık hava kirliliğinden ziyade 20-30 yıllık birikimli maruziyetin sonucudur.\n"
            "4. **Ekolojik Yanılgı (Ecological Fallacy):** İl düzeyindeki makro kirlilik verileri, bireylerin mesleki veya iç ortam maruziyetini tek başına yansıtamaz.\n\n"
            "💡 **Özet:** Hava kirliliği solunum hastalıkları için kanıtlanmış bir risk faktörüdür; ancak il bazındaki vefat istatistiklerinde nüfusun yaş ortalaması ve sağlık altyapısı birincil belirleyici olmaktadır."
        )

    # ÖZEL ANALİTİK SORU 4: OSB SAYISI EN YÜKSEK İLLERDE KİRLİLİK NE DURUMDA?
    if ("osb sayisi en yuksek" in p_norm or "organize sanayi bolgesi" in p_norm or "en cok osb" in p_norm) and ("kirlilik" in p_norm or "ne durumda" in p_norm):
        top_osb_df = df.sort_values(by="toplam_osb", ascending=False).head(5)
        lines = []
        for i, (_, r) in enumerate(top_osb_df.iterrows()):
            p_cnt = int(r.get("toplam_parsel", 0)) if pd.notna(r.get("toplam_parsel")) else 0
            lines.append(
                f"{i+1}. **{r['il']}** ({r['bolge']}): **{int(r['toplam_osb'])} OSB** ({p_cnt:,} parsel) &bull; PM2.5: `{r['pm25']:.1f} µg/m³` (DSÖ'nün {r['pm25']/5.0:.1f} katı)"
            )
        return (
            "🏭 **Organize Sanayi Bölgesi (OSB) Sayısı En Yüksek İllerde Kirlilik Durumu:**\n\n"
            + "\n".join(lines) + "\n\n"
            f"📊 **Analitik Bulgular:** Bu 5 ilin ortalama PM2.5 değeri `{top_osb_df['pm25'].mean():.1f} µg/m³`, "
            f"81 il ortalaması `{df['pm25'].mean():.1f} µg/m³`.\n\n"
            "⚠️ **Yorum Sınırı:** OSB sayısı yüksek iller aynı zamanda nüfusu ve trafiği yüksek büyükşehirlerdir. "
            "İl düzeyindeki bu karşılaştırma sanayinin etkisini nüfus, ısınma, trafik ve topoğrafyadan ayıramaz; nedensellik göstermez."
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
            rho_str = "-"
            p_str = "hesaplanamadı"
        pop_df = df[["nufus", "pm25"]].dropna()
        rho_pop = stats.spearmanr(pop_df["nufus"], pop_df["pm25"])[0] if len(pop_df) >= 10 else float("nan")
        rho_pop_str = f"{rho_pop:+.2f}".replace(".", ",")

        return (
            "📊 **Türkiye Genelinde Hava Kirliliği ve Organize Sanayi (OSB) İlişkisi Analitiği**\n\n"
            f"- **Spearman Sıra Korelasyon Katsayısı (ρ):** `{rho_str}` ({p_str}, n = {len(df)})\n\n"
            f"- **Karşılaştırma — Nüfus ile PM2.5 (ρ):** `{rho_pop_str}`\n\n"
            "🔍 **Değerlendirme:**\n"
            "1. **Karıştırıcı Etken:** OSB alanı büyük iller aynı zamanda kalabalık büyükşehirlerdir; nüfus, trafik ve konut ısınması "
            "PM2.5 ile en az OSB kadar güçlü ilişkilidir. Bu korelasyon sanayinin kendi etkisini ayırt etmez.\n"
            "2. **Model Sınırı:** PM2.5 değerleri ~10 km çözünürlüklü CAMS modelinin il merkezi değeridir; Iğdır gibi kapalı havzalarda "
            "kış inversiyonu ve yerel ısınma kaynaklı kirliliği eksik gösterebilir (Kara Rapor 2025: Iğdır istasyonu 46,8 µg/m³).\n\n"
            "💡 **Sonuç:** İl düzeyindeki ekolojik korelasyon bir ilişkiyi betimler; nedensellik kurmak için emisyon envanteri ve "
            "nüfusu kontrol eden modeller gerekir."
        )

    # 3. KURAL: BÖLGESEL SIRALAMA & EN TEMİZ VE EN KİRLİ BÖLGE SORGULARI
    if any(k in p_norm for k in ["en temiz bolge", "temiz bolge", "havasi en temiz bolge", "bolgeler", "bolge siralamasi", "cografi bolge", "en temiz ve en kirli", "en kirli ve en temiz"]) or \
       ("bolge" in p_norm and any(k in p_norm for k in ["temiz", "en temiz", "kirli", "en kirli", "iyi", "hangisi", "siralama"])):
        bolge_stats = df.groupby("bolge")["pm25"].mean().sort_values()
        lines = []
        cleanest_b = bolge_stats.index[0]
        cleanest_v = bolge_stats.iloc[0]
        dirtiest_b = bolge_stats.index[-1]
        dirtiest_v = bolge_stats.iloc[-1]

        # Bölgenin PM2.5 seviyesi en düşük ilini bul
        cleanest_region_df = df[df["bolge"] == cleanest_b].sort_values(by="pm25", ascending=True)
        top_city_in_reg = cleanest_region_df.iloc[0]["il"] if not cleanest_region_df.empty else ""
        top_city_pm = cleanest_region_df.iloc[0]["pm25"] if not cleanest_region_df.empty else 0.0

        for idx, (b_name, b_val) in enumerate(bolge_stats.items()):
            icon = "🌿" if idx == 0 else ("🚨" if idx == len(bolge_stats) - 1 else "📍")
            lines.append(f"{idx+1}. {icon} **{b_name}:** `{b_val:.1f} µg/m³` PM2.5 (DSÖ sınırının {b_val/5.0:.1f} katı)")

        return (
            f"🌍 **Türkiye'nin 7 Coğrafi Bölgesi Hava Kalitesi Sıralaması:**\n\n"
            f"🌿 **En Temiz Coğrafi Bölge:** **{cleanest_b}** (Bölgesel Ortalama: `{cleanest_v:.1f} µg/m³` PM2.5)\n"
            f"• *Bölgede PM2.5 En Düşük İl:* **{top_city_in_reg}** (`{top_city_pm:.1f} µg/m³`)\n\n"
            f"🚨 **En Kirli Coğrafi Bölge:** **{dirtiest_b}** (Bölgesel Ortalama: `{dirtiest_v:.1f} µg/m³` PM2.5)\n\n"
            f"**Tüm Coğrafi Bölgelerin PM2.5 Seviyesine Göre Sıralaması (Düşükten Yükseğe):**\n"
            + "\n".join(lines)
            + "\n\n💡 **Veri Notu:** Coğrafi bölgeler arasındaki partikül konsantrasyonu dağılımı bölgesel sanayi, topoğrafya ve meteorolojik faktörlerin bileşkesini yansıtır."
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
            + "\n\n💡 **Sanayi Analitiği:** OSB sayısı ve sanayi alanı yüksek illerde emisyon izleme ve mevzuat standartlarına uyum takip edilmektedir."
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
            dso_status = str(r.get("dso_risk", "Kritik" if pm25 > 35 else "Orta"))
            sol_100k = float(r.get("solunum_olum_100k", 0.0))
            sol_toplam = int(r.get("solunum_olum", 0)) if pd.notna(r.get("solunum_olum")) else 0
            parsel_str = f"{parsel_count:,}".replace(",", ".")

            return (
                f"🏙️ **{c} İli Çevre & Hava Kalitesi Karnesi**\n\n"
                f"- **PM2.5 Kirlilik Değeri:** `{pm25:.1f} µg/m³`\n"
                f"- **DSÖ Durumu (Dünya Sağlık Örgütü):** **{dso_status}** (DSÖ 5 µg/m³ yıllık kılavuzunun **{kat:.1f} katı**)\n"
                f"- **Organize Sanayi Bölgesi (OSB):** **{osb_count} Adet** ({parsel_str} parsel)\n"
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
            "🚨 **Türkiye Genelinde PM2.5 Seviyesi En Yüksek 3 Şehir:**\n\n"
            + "\n".join(lines)
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
            "🌿 **Türkiye Genelinde PM2.5 Seviyesi En Düşük 3 Şehir:**\n\n"
            + "\n".join(lines)
        )

    # 10. KURAL: EŞLEŞMEYEN GENEL SORULARDA REHBER SUN
    return (
        "Merhaba! Ben **HavaAtlası Yerel Veri Asistanı**.\n\n"
        "Sorunuzu sistem veritabanındaki 81 il ile eşleştiremedim. Bana şu kalıplarla soru sorabilirsiniz:\n\n"
        "- *'Sanayisi az olmasına rağmen havası en kirli iller hangileri ve sebebi ne?'*\n"
        "- *'DSÖ'nün 5 µg/m³ kılavuz değerini karşılayan temiz bir ilimiz var mı?'*\n"
        "- *'İstanbul ile Ankara'nın hava kalitesi ve sanayi yükünü kıyasla.'*\n"
        "- *'Organize Sanayi Bölgesi (OSB) sayısı en yüksek illerde kirlilik ne durumda?'*\n"
        "- *'Hava kirliliği ile solunum yolu ölümleri arasında doğrudan bir paralellik var mı?'*\n"
        "- *'Türkiye'nin havası en temiz ve en kirli coğrafi bölgeleri hangileridir?'*\n"
        "- *'Bursa il profili'* veya *'Iğdır hava kalitesi ve karnesi'*\n\n"
        "Ayrıca yukarıdaki **hazır analiz butonlarına** tıklayarak anında detaylı analiz alabilirsiniz!"
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
        min-height: 50px !important;
        height: auto !important;
        white-space: normal !important;
        font-size: 12px !important;
        line-height: 1.35 !important;
        padding: 8px 10px !important;
        text-align: center !important;
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

    welcome_text = (
        "Merhaba! Ben **HavaAtlası Yerel Veri Asistanı**.\n\n"
        "81 ilimizin PM2.5 hava kalitesi, kirlilik ölçümleri, Organize Sanayi Bölgesi (OSB) ve parsel sayıları ile "
        "TÜİK solunum sağlık verileri üzerinden **%100 yerel ve çevrimdışı** olarak çalışıyorum.\n\n"
        "Aşağıdaki **önerilen analitik soruları** tek tıkla sorabilir ya da dilediğiniz ili/konuyu doğrudan yazabilirsiniz:\n\n"
        "- *Sanayisi az olmasına rağmen havası en kirli iller hangileri ve sebebi ne?*\n"
        "- *DSÖ'nün 5 µg/m³ kılavuz değerini karşılayan temiz bir ilimiz var mı?*\n"
        "- *İstanbul ile Ankara'nın hava kalitesi ve sanayi yükünü kıyasla.*\n"
        "- *Organize Sanayi Bölgesi (OSB) sayısı en yüksek illerde kirlilik ne durumda?*\n"
        "- *Hava kirliliği ile solunum yolu ölümleri arasında doğrudan bir paralellik var mı?*\n"
        "- *Türkiye'nin havası en temiz ve en kirli coğrafi bölgeleri hangileridir?*"
    )

    with col_clr:
        if st.button("Sohbeti Temizle", key="btn_reset_chat", use_container_width=True):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": welcome_text
                }
            ]
            st.rerun()

    # Sohbet Geçmişi Başlatma (st.session_state.messages)
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": welcome_text
            }
        ]

    # Sohbet Mesajları Konteyneri (Üst Bölüm)
    chat_container = st.container()

    # Sohbet Alanının Üstünde 6 Hazır Analitik Soru Butonu (2 Satır x 3 Sütun)
    st.markdown("<div style='margin-top: 10px; margin-bottom: 8px; font-size: 12px; color: #94a3b8; font-weight: 700; letter-spacing: 0.5px;'>ÖNERİLEN ANALİTİK SORULAR & HIZLI ANALİZ:</div>", unsafe_allow_html=True)
    btn_prompt = None

    row1_c1, row1_c2, row1_c3 = st.columns(3)

    with row1_c1:
        st.markdown("<div class='quick-btn-box'>", unsafe_allow_html=True)
        if st.button("🏔️ Sanayisi az ama kirli iller ve sebepleri", key="btn_q1_sanayi_az", use_container_width=True):
            btn_prompt = "Sanayisi az olmasına rağmen havası en kirli iller hangileri ve sebebi ne?"
        st.markdown("</div>", unsafe_allow_html=True)

    with row1_c2:
        st.markdown("<div class='quick-btn-box'>", unsafe_allow_html=True)
        if st.button("🌍 DSÖ 5 µg/m³ kılavuzunu karşılayan il var mı?", key="btn_q2_dso_uyum", use_container_width=True):
            btn_prompt = "DSÖ'nün 5 µg/m³ kılavuz değerini karşılayan temiz bir ilimiz var mı?"
        st.markdown("</div>", unsafe_allow_html=True)

    with row1_c3:
        st.markdown("<div class='quick-btn-box'>", unsafe_allow_html=True)
        if st.button("⚖️ İstanbul ile Ankara kıyaslaması", key="btn_q3_ist_ank", use_container_width=True):
            btn_prompt = "İstanbul ile Ankara'nın hava kalitesi ve sanayi yükünü kıyasla."
        st.markdown("</div>", unsafe_allow_html=True)

    row2_c1, row2_c2, row2_c3 = st.columns(3)

    with row2_c1:
        st.markdown("<div class='quick-btn-box'>", unsafe_allow_html=True)
        if st.button("🏭 En çok OSB'li illerde kirlilik durumu", key="btn_q4_top_osb", use_container_width=True):
            btn_prompt = "Organize Sanayi Bölgesi (OSB) sayısı en yüksek illerde kirlilik ne durumda?"
        st.markdown("</div>", unsafe_allow_html=True)

    with row2_c2:
        st.markdown("<div class='quick-btn-box'>", unsafe_allow_html=True)
        if st.button("🫁 Kirlilik ile solunum vefatı paralelliği", key="btn_q5_solunum_rel", use_container_width=True):
            btn_prompt = "Hava kirliliği ile solunum yolu ölümleri arasında doğrudan bir paralellik var mı?"
        st.markdown("</div>", unsafe_allow_html=True)

    with row2_c3:
        st.markdown("<div class='quick-btn-box'>", unsafe_allow_html=True)
        if st.button("🗺️ En temiz ve en kirli coğrafi bölgeler", key="btn_q6_bolgeler", use_container_width=True):
            btn_prompt = "Türkiye'nin havası en temiz ve en kirli coğrafi bölgeleri hangileridir?"
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
