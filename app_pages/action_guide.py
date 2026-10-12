"""
Yapılması Gerekenler — Önlemler & Eylem Rehberi
HavaAtlası — Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import streamlit as st
import pandas as pd


def render_action_guide_page(df: pd.DataFrame = None):
    """
    Hava Kirliliğine Karşı Eylem Rehberi Sayfası
    DSÖ ve Çevre, Şehircilik ve İklim Değişikliği Bakanlığı kılavuzlarına dayalı pratik adımlar.
    """
    # 1. BAŞLIK VE KURUMSAL GİRİŞ BANDI
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
            <span style="background: rgba(0, 210, 238, 0.15); color: #00d2ee; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; border: 1px solid rgba(0, 210, 238, 0.3);">
                REHBER & EYLEM PLANI
            </span>
            <span style="font-size: 12px; color: #8faec9;">Resmi Kılavuz Standartları</span>
        </div>
        <h2 style="margin: 0; font-size: 24px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;">
            Hava Kirliliğine Karşı Eylem Rehberi: Bireysel Korunma ve Emisyon Azaltım Önlemleri
        </h2>
        <p style="margin: 6px 0 0 0; font-size: 13.5px; color: #cbd5e1; line-height: 1.5;">
            Dünya Sağlık Örgütü (DSÖ) 2021 Küresel Hava Kalitesi Kılavuzları ve T.C. Çevre, Şehircilik ve İklim Değişikliği Bakanlığı Temiz Hava Eylem Planı standartlarına dayalı pratik adımlar.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 2. KURUMSAL VURGU BANDI
    st.markdown("""
    <div style="background: rgba(3, 27, 46, 0.7); border: 1px solid #093452; border-left: 4px solid #00d2ee; border-radius: 8px; padding: 14px 18px; margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <div>
                <strong style="color: #ffffff; font-size: 13.5px;">Çift Yönlü Mücadele İlkesi:</strong>
                <span style="color: #cbd5e1; font-size: 13px; margin-left: 4px;">
                    Hava kirliliğiyle mücadele yalnızca bireysel korunmayı değil, aynı zamanda kaynağında emisyon azaltımını zorunlu kılar.
                </span>
            </div>
            <span style="font-size: 11px; color: #8faec9; font-family: monospace;">Kılavuz Referansı: DSÖ-2021 / ÇŞİDB-2025</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. 6 ADET ŞIK GLASSMORPHISM KART (2 SÜTUNLU YAPI - EMOJİSİZ, MİNİMALİST)
    col1, col2 = st.columns(2)

    with col1:
        # KART 1: Bireysel Maruziyetin Azaltılması ve Zamanlama
        st.markdown("""
        <div style="background: #031b2e; border: 1px solid #093452; border-left: 4px solid #38bdf8; border-radius: 10px; padding: 18px; margin-bottom: 18px; min-height: 220px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background: rgba(56, 189, 248, 0.15); width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 800; color: #38bdf8; font-family: monospace; border: 1px solid rgba(56, 189, 248, 0.3);">
                        01
                    </div>
                    <h4 style="margin: 0; font-size: 15px; font-weight: 700; color: #ffffff;">
                        Bireysel Maruziyetin Azaltılması ve Zamanlama
                    </h4>
                </div>
                <span style="font-size: 10.5px; background: #021220; color: #38bdf8; padding: 3px 8px; border-radius: 4px; border: 1px solid #072e4a;">
                    Bireysel Korunma
                </span>
            </div>
            <ul style="margin: 0; padding-left: 18px; font-size: 13px; color: #cbd5e1; line-height: 1.6;">
                <li style="margin-bottom: 8px;">
                    Kirlilik seviyesinin pik yaptığı <strong>sabah ve akşam iş/okul çıkışı saatlerinde</strong> dış ortamda ağır fiziksel aktivitelerden (koşu, antrenman, spor) kaçınılmalıdır.
                </li>
                <li>
                    PM2.5'in <strong>"Hassas" veya "Kritik"</strong> olduğu günlerde dışarı çıkması zorunlu olan risk grupları (yaşlılar, çocuklar, solunum hastaları) standart cerrahi maske yerine partikül tutucu <strong>FFP2/N95 maske</strong> tercih etmelidir.
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # KART 3: Ulaşım Tercihlerinin Dönüştürülmesi
        st.markdown("""
        <div style="background: #031b2e; border: 1px solid #093452; border-left: 4px solid #00d2ee; border-radius: 10px; padding: 18px; margin-bottom: 18px; min-height: 220px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background: rgba(0, 210, 238, 0.15); width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 800; color: #00d2ee; font-family: monospace; border: 1px solid rgba(0, 210, 238, 0.3);">
                        03
                    </div>
                    <h4 style="margin: 0; font-size: 15px; font-weight: 700; color: #ffffff;">
                        Ulaşım Tercihlerinin Dönüştürülmesi
                    </h4>
                </div>
                <span style="font-size: 10.5px; background: #021220; color: #00d2ee; padding: 3px 8px; border-radius: 4px; border: 1px solid #072e4a;">
                    Mobilite & Emisyon
                </span>
            </div>
            <ul style="margin: 0; padding-left: 18px; font-size: 13px; color: #cbd5e1; line-height: 1.6;">
                <li style="margin-bottom: 8px;">
                    Bireysel araç kullanımı yerine <strong>raylı sistem ve toplu taşıma</strong> tercih edilmeli; kısa mesafeli seyahatlerde mikro-mobilite (yürüme, bisiklet) alışkanlık haline getirilmelidir.
                </li>
                <li>
                    Fosil yakıtlı araçlarda uzun süreli <strong>rölantide bekleme (motoru çalışır bırakma)</strong> kesinlikle önlenmeli; periyodik <strong>egzoz emisyon ölçümleri</strong> ve araç bakımları aksatılmamalıdır.
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # KART 5: Sanayi ve Tarımsal Emisyonların Önlenmesi
        st.markdown("""
        <div style="background: #031b2e; border: 1px solid #093452; border-left: 4px solid #facc15; border-radius: 10px; padding: 18px; margin-bottom: 18px; min-height: 220px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background: rgba(250, 204, 21, 0.15); width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 800; color: #facc15; font-family: monospace; border: 1px solid rgba(250, 204, 21, 0.3);">
                        05
                    </div>
                    <h4 style="margin: 0; font-size: 15px; font-weight: 700; color: #ffffff;">
                        Sanayi ve Tarımsal Emisyonların Önlenmesi
                    </h4>
                </div>
                <span style="font-size: 10.5px; background: #021220; color: #facc15; padding: 3px 8px; border-radius: 4px; border: 1px solid #072e4a;">
                    Sektörel Önlemler
                </span>
            </div>
            <ul style="margin: 0; padding-left: 18px; font-size: 13px; color: #cbd5e1; line-height: 1.6;">
                <li style="margin-bottom: 8px;">
                    Tarımsal alanlarda kesinlikle <strong>anız yakılmamalıdır</strong>; bu uygulamanın atmosferimize tonlarca ince partikül (PM2.5) ve toksik gaz salarak bölgesel hava kalitesini çökerttiği unutulmamalıdır.
                </li>
                <li>
                    Sanayi tesislerinde, OSB üretim sahalarında ve taş ocaklarında <strong>toz indirgeme sistemleri ve elektrostatik baca filtreleri</strong> 7/24 kesintisiz ve denetimli çalıştırılmalıdır.
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # KART 2: İç Mekan Hava Kalitesinin Korunması
        st.markdown("""
        <div style="background: #031b2e; border: 1px solid #093452; border-left: 4px solid #10b981; border-radius: 10px; padding: 18px; margin-bottom: 18px; min-height: 220px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background: rgba(16, 185, 129, 0.15); width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 800; color: #10b981; font-family: monospace; border: 1px solid rgba(16, 185, 129, 0.3);">
                        02
                    </div>
                    <h4 style="margin: 0; font-size: 15px; font-weight: 700; color: #ffffff;">
                        İç Mekan Hava Kalitesinin Korunması
                    </h4>
                </div>
                <span style="font-size: 10.5px; background: #021220; color: #10b981; padding: 3px 8px; border-radius: 4px; border: 1px solid #072e4a;">
                    Yaşam Alanı
                </span>
            </div>
            <ul style="margin: 0; padding-left: 18px; font-size: 13px; color: #cbd5e1; line-height: 1.6;">
                <li style="margin-bottom: 8px;">
                    Dış ortam kirliliği yüksekken pencereler uzun süreli açık tutulmamalı; mekan havalandırması kirliliğin görece düşük olduğu <strong>öğle saatlerinde kısa süreli</strong> yapılmalıdır.
                </li>
                <li>
                    Yaşam ve çalışma alanlarında <strong>HEPA filtreli hava temizleme cihazları</strong> kullanılmalı; kapalı mekanlarda tütün dumanı, tütsü ve kimyasal oda kokuları gibi partikül üreten kaynaklar tamamen engellenmelidir.
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # KART 4: Isınmada Temiz Enerji ve Bina Yalıtımı
        st.markdown("""
        <div style="background: #031b2e; border: 1px solid #093452; border-left: 4px solid #f97316; border-radius: 10px; padding: 18px; margin-bottom: 18px; min-height: 220px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background: rgba(249, 115, 22, 0.15); width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 800; color: #f97316; font-family: monospace; border: 1px solid rgba(249, 115, 22, 0.3);">
                        04
                    </div>
                    <h4 style="margin: 0; font-size: 15px; font-weight: 700; color: #ffffff;">
                        Isınmada Temiz Enerji ve Bina Yalıtımı
                    </h4>
                </div>
                <span style="font-size: 10.5px; background: #021220; color: #f97316; padding: 3px 8px; border-radius: 4px; border: 1px solid #072e4a;">
                    Enerji & Isınma
                </span>
            </div>
            <ul style="margin: 0; padding-left: 18px; font-size: 13px; color: #cbd5e1; line-height: 1.6;">
                <li style="margin-bottom: 8px;">
                    Katı yakıt (kalitesiz kömür, linyit, biyokütle) kullanımından vazgeçilerek <strong>doğalgaz veya ısı pompası</strong> gibi düşük emisyonlu modern ısınma sistemlerine geçilmelidir.
                </li>
                <li>
                    Binalarda <strong>çift cam ve ısı yalıtımı (mantolama)</strong> yaygınlaştırılarak birincil enerji ihtiyacı azaltılmalı; bina baca ve kazan filtre bakımları kış öncesi düzenli yaptırılmalıdır.
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # KART 6: Veri Takibi ve Erken Uyarı Sistemleri
        st.markdown("""
        <div style="background: #031b2e; border: 1px solid #093452; border-left: 4px solid #8b5cf6; border-radius: 10px; padding: 18px; margin-bottom: 18px; min-height: 220px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background: rgba(139, 92, 246, 0.15); width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 800; color: #8b5cf6; font-family: monospace; border: 1px solid rgba(139, 92, 246, 0.3);">
                        06
                    </div>
                    <h4 style="margin: 0; font-size: 15px; font-weight: 700; color: #ffffff;">
                        Veri Takibi ve Erken Uyarı Sistemleri
                    </h4>
                </div>
                <span style="font-size: 10.5px; background: #021220; color: #8b5cf6; padding: 3px 8px; border-radius: 4px; border: 1px solid #072e4a;">
                    Karar Destek
                </span>
            </div>
            <ul style="margin: 0; padding-left: 18px; font-size: 13px; color: #cbd5e1; line-height: 1.6;">
                <li style="margin-bottom: 8px;">
                    Günlük dış mekan planları ve dış ortam fiziksel aktiviteleri yapılmadan önce <strong>HavaAtlası</strong> gibi resmi istasyon ve uydu verilerine dayalı hava kalitesi indeksleri kontrol edilmelidir.
                </li>
                <li>
                    Kirlilik eşikleri aşıldığında yerel yönetimlerin ve mülki amirliklerin yapacağı <strong>inversiyon ve hava kalitesi kriz uyarılarına</strong>, yönlendirmelerine harfiyen uyulmalıdır.
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # 4. ALT BİLGİ VE KURUMSAL FOOTER
    st.markdown("""
    <div style="margin-top: 20px; padding: 14px 18px; background: #021220; border: 1px solid #07253d; border-radius: 8px; text-align: center; font-size: 11.5px; color: #8faec9;">
        <strong>HavaAtlası Rehber Modülü</strong> &bull; Bilgilendirme amaçlı hazırlanmıştır. Akut solunum veya kardiyovasküler rahatsızlıklarda en yakın sağlık kuruluşuna başvurunuz.
    </div>
    """, unsafe_allow_html=True)
