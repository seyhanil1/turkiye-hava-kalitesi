"""
Ekonomi & Sağlık Maliyeti Sayfası
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def render_economy_page(df: pd.DataFrame):
    """
    Hava kirliliğinin sağlık sistemi, erken ölümler ve iş gücü kaybı üzerindeki
    tahmini ekonomik yükünü (DSÖ, OECD ve HEAL metodolojisi) kurumsal koyu cam temayla sunar.
    """
    # Veri hesaplamaları
    if "maliyet_milyon_tl" in df.columns:
        toplam_maliyet = float(df["maliyet_milyon_tl"].sum())
    else:
        toplam_maliyet = 820000.0  # Literatüre uygun varsayılan (~820 Milyar TL)

    toplam_nufus = float(df["nufus"].sum()) if "nufus" in df.columns else 85341527.0
    kisi_basi_maliyet = round((toplam_maliyet * 1_000_000) / max(toplam_nufus, 1), 0)

    # Sağlık ekonomisi standartları (OECD, DSÖ, HEAL):
    # 1. Erken Vefat Maliyetleri (VSL): %78 (en büyük pay: %75-%80)
    # 2. Doğrudan Sağlık ve Tedavi Giderleri: %16 (%15-%18)
    # 3. İş Gücü ve Verimlilik Kaybı: %6 (%5-%7)
    maliyet_vefat = round(toplam_maliyet * 0.78, 1)
    maliyet_saglik = round(toplam_maliyet * 0.16, 1)
    maliyet_isgucu = round(toplam_maliyet - maliyet_vefat - maliyet_saglik, 1)

    toplam_maliyet_str = f"{toplam_maliyet:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    maliyet_vefat_str = f"{maliyet_vefat:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    maliyet_saglik_str = f"{maliyet_saglik:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    maliyet_isgucu_str = f"{maliyet_isgucu:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # ========================================================
    # 1. ÜST KISIM - BAŞLIK & BİLANÇO (HERO CARD)
    # ========================================================
    st.markdown(f"""
    <div style="margin-bottom: 22px;">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
            <div style="background:rgba(245, 158, 11, 0.15); color:#f59e0b; width:34px; height:34px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-weight:800; font-family:monospace; font-size:14px; border:1px solid rgba(245, 158, 11, 0.3);">₺</div>
            <h2 style="margin:0; font-size:24px; font-weight:800; color:#ffffff; letter-spacing:-0.5px;">
                Hava Kirliliğinin Yıllık Ekonomik &amp; Sağlık Faturası
            </h2>
        </div>
        <p style="margin:0; font-size:13px; color:#8faec9;">
            Dünya Sağlık Örgütü (WHO), OECD ve HEAL epidemiyolojik sağlık-ekonomi modellerine göre hava kirliliğinin Türkiye makroekonomisine getirdiği yıllık tahmini yük.
        </p>
    </div>

    <div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.16) 0%, rgba(239, 68, 68, 0.12) 50%, rgba(11, 19, 43, 0.95) 100%);
                border: 1px solid rgba(245, 158, 11, 0.45);
                border-radius: 16px;
                padding: 24px 28px;
                margin-bottom: 24px;
                box-shadow: 0 12px 36px rgba(0, 0, 0, 0.35);
                backdrop-filter: blur(14px);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
            <div>
                <div style="display:inline-flex; align-items:center; gap:6px; background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.4); padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 700; color: #fde047; margin-bottom: 12px; letter-spacing: 0.5px;">
                    RESMİ EPİDEMİYOLOJİK BİLANÇO
                </div>
                <div style="font-size: 22px; font-weight: 900; color: #ffffff; letter-spacing: -0.3px; line-height: 1.3;">
                    TÜRKİYE GENELİ TAHMİNİ EKONOMİK YÜK: <span style="background: linear-gradient(90deg, #fbbf24, #f43f5e); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{toplam_maliyet_str} MİLYON ₺</span>
                </div>
                <div style="font-size: 12.5px; color: #cbd5e1; margin-top: 8px; line-height: 1.5; max-width: 950px;">
                    Türkiye genelinde hava kirliliğine atfedilen yıllık ~42.000 erken ölümün İstatistiki Yaşam Değeri (VSL) analizi, SGK solunum/dolaşım tedavi giderleri ve kayıp iş günü maliyetlerinin birleşik hesaplamasıdır.
                </div>
            </div>
            <div style="background: rgba(2, 18, 32, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 12px 18px; text-align: right; min-width: 170px;">
                <div style="font-size: 11px; color: #8faec9; text-transform: uppercase; font-weight: 600;">Kişi Başı Yıllık Yük</div>
                <div style="font-size: 20px; font-weight: 800; color: #38bdf8;">{int(kisi_basi_maliyet):,} ₺</div>
                <div style="font-size: 10.5px; color: #64748b;">Nüfus: 85,3 Milyon</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # 2. ORTA KISIM - ÜÇLÜ MALİYET BÖLÜNMESİ (st.columns(3))
    # ========================================================
    col1, col2, col3 = st.columns(3)

    # 1. KART: ERKEN VEFAT MALİYETLERİ (VSL) -> EN BÜYÜK PAY (%78)
    with col1:
        st.markdown(f"""
        <div style="background: rgba(17, 26, 46, 0.9);
                    border: 1px solid rgba(245, 158, 11, 0.45);
                    border-radius: 14px;
                    padding: 20px;
                    min-height: 230px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    box-shadow: 0 8px 24px rgba(245, 158, 11, 0.12);">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <span style="background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.4); padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 800; font-family: monospace;">BEŞERİ SERMAYE</span>
                    <span style="background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.5); padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 700;">
                        %78 PAY • VSL MODELİ
                    </span>
                </div>
                <div style="font-size: 13px; color: #8faec9; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                    ERKEN VEFAT MALİYETLERİ (VSL)
                </div>
                <div style="font-size: 24px; font-weight: 900; color: #ffffff; margin: 6px 0 2px 0;">
                    {maliyet_vefat_str} <span style="font-size:14px; color:#f59e0b; font-weight:700;">Milyon ₺</span>
                </div>
                <div style="font-size: 11.5px; color: #cbd5e1; line-height: 1.5; margin-top: 10px;">
                    DSÖ ve OECD VSL (İstatistiki Yaşam Değeri) yaklaşımıyla hava kirliliğine atfedilen ~42.000 önlenebilir erken vefatın sosyo-ekonomik maliyeti.
                </div>
            </div>
            <div style="margin-top: 14px; padding-top: 10px; border-top: 1px solid rgba(255, 255, 255, 0.06); font-size: 11px; color: #fcd34d;">
                • Türkiye genelinde hava kirliliğine atfedilen yıllık ~42.000 erken ölüm baz alınmıştır
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 2. KART: DOĞRUDAN SAĞLIK GİDERLERİ (%16)
    with col2:
        st.markdown(f"""
        <div style="background: rgba(17, 26, 46, 0.9);
                    border: 1px solid rgba(244, 63, 94, 0.45);
                    border-radius: 14px;
                    padding: 20px;
                    min-height: 230px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    box-shadow: 0 8px 24px rgba(244, 63, 94, 0.12);">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <span style="background: rgba(244, 63, 94, 0.15); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.4); padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 800; font-family: monospace;">KLİNİK TEDAVİ</span>
                    <span style="background: rgba(244, 63, 94, 0.15); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.5); padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 700;">
                        %16 PAY • KLİNİK YÜK
                    </span>
                </div>
                <div style="font-size: 13px; color: #8faec9; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                    DOĞRUDAN SAĞLIK GİDERLERİ
                </div>
                <div style="font-size: 24px; font-weight: 900; color: #ffffff; margin: 6px 0 2px 0;">
                    {maliyet_saglik_str} <span style="font-size:14px; color:#f43f5e; font-weight:700;">Milyon ₺</span>
                </div>
                <div style="font-size: 11.5px; color: #cbd5e1; line-height: 1.5; margin-top: 10px;">
                    SGK ve kamu hastanelerindeki astım, KOAH, solunum yetmezliği yatışları ve ilaç giderleri.
                </div>
            </div>
            <div style="margin-top: 14px; padding-top: 10px; border-top: 1px solid rgba(255, 255, 255, 0.06); font-size: 11px; color: #fca5a5;">
                • SGK solunum reçeteleri ve kamu yataklı tedavi bütçe yükü
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 3. KART: İŞ GÜCÜ & VERİMLİLİK KAYBI (%6)
    with col3:
        st.markdown(f"""
        <div style="background: rgba(17, 26, 46, 0.9);
                    border: 1px solid rgba(0, 242, 254, 0.45);
                    border-radius: 14px;
                    padding: 20px;
                    min-height: 230px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    box-shadow: 0 8px 24px rgba(0, 242, 254, 0.12);">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <span style="background: rgba(0, 242, 254, 0.15); color: #00f2fe; border: 1px solid rgba(0, 242, 254, 0.4); padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 800; font-family: monospace;">REEL SEKTÖR</span>
                    <span style="background: rgba(0, 242, 254, 0.15); color: #00f2fe; border: 1px solid rgba(0, 242, 254, 0.5); padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 700;">
                        %6 PAY • ÜRETİM KAYBI
                    </span>
                </div>
                <div style="font-size: 13px; color: #8faec9; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                    İŞ GÜCÜ &amp; VERİMLİLİK KAYBI
                </div>
                <div style="font-size: 24px; font-weight: 900; color: #ffffff; margin: 6px 0 2px 0;">
                    {maliyet_isgucu_str} <span style="font-size:14px; color:#00f2fe; font-weight:700;">Milyon ₺</span>
                </div>
                <div style="font-size: 11.5px; color: #cbd5e1; line-height: 1.5; margin-top: 10px;">
                    Kirlilik kaynaklı hastalık izinleri ve kayıp iş günlerinin reel sektöre getirdiği üretim kaybı.
                </div>
            </div>
            <div style="margin-top: 14px; padding-top: 10px; border-top: 1px solid rgba(255, 255, 255, 0.06); font-size: 11px; color: #7dd3fc;">
                • Kirlilik pik günlerinde iş günü devamsızlığı ve fabrika verim düşüşü
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # ========================================================
    # 3. GRAFİK & DSÖ KAZANIMLARI (st.columns([3, 2]))
    # ========================================================
    col_chart, col_gain = st.columns([3, 2])

    with col_chart:
        st.markdown("#### Hava Kirliliğinin Yıllık Tahmini Ekonomik Maliyet Dağılımı")
        st.caption("DSÖ ve OECD sağlık ekonomisi modellerine göre 3 ana harcama kaleminin oransal payları.")

        labels = ["Erken Vefat Maliyetleri (VSL)", "Doğrudan Sağlık Giderleri", "İş Gücü & Verimlilik Kaybı"]
        values = [maliyet_vefat, maliyet_saglik, maliyet_isgucu]
        colors = ["#f59e0b", "#f43f5e", "#00f2fe"]

        fig_donut = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.62,
            marker=dict(colors=colors, line=dict(color="#07192b", width=2)),
            textinfo="percent+label",
            textposition="inside",
            hoverinfo="label+value+percent",
            hovertemplate="<b>%{label}</b><br>Tutar: %{value:,.1f} Milyon ₺<br>Oran: %{percent}<extra></extra>"
        )])

        fig_donut.update_layout(
            height=340,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10, l=10, r=10, b=10),
            showlegend=False,
            annotations=[
                dict(
                    text=f"<b>%100</b><br><span style='font-size:11px;color:#8faec9;'>Mali Yük</span>",
                    x=0.5, y=0.5,
                    font=dict(size=16, color="#ffffff"),
                    showarrow=False
                )
            ]
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_gain:
        with st.container(border=True):
            st.markdown("#### DSÖ Standartlarına Geçilseydi Ne Olurdu?")
            st.caption("DSÖ kılavuz sınırına (5 µg/m³) ulaşıldığında sağlanacak yıllık sosyo-ekonomik kazanım projeksiyonu.")

            kazanim_df = pd.DataFrame([
                {"Kazanım Alanı": "Önlenebilir Can Kaybı", "Tahmini Etki": "+18.500 Erken Ölüm", "Kılavuz": "DSÖ 2021 (5 µg/m³)"},
                {"Kazanım Alanı": "Yıllık Kamu Tasarrufu", "Tahmini Etki": "~170 Milyar TL Tasarruf", "Kılavuz": "Sağlık & Tedavi Bütçesi"},
                {"Kazanım Alanı": "İlaç ve Tedavi İndirimi", "Tahmini Etki": "%75 Kronik İlaç Azalımı", "Kılavuz": "SGK Reçete Yükü"},
                {"Kazanım Alanı": "İş Gücü Verim Kazancı", "Tahmini Etki": "+4,2 Milyon İş Günü", "Kılavuz": "Reel Sektör"}
            ])
            st.dataframe(kazanim_df, use_container_width=True, hide_index=True)

            c_k1, c_k2 = st.columns(2)
            with c_k1:
                st.metric(label="Önlenebilir Can Kaybı", value="18.500+ Kişi", delta="Yıllık kurtarılabilir", delta_color="normal")
            with c_k2:
                st.metric(label="Kamu Tasarrufu", value="~170 Milyar ₺", delta="Yıllık bütçe kazancı", delta_color="normal")

            st.caption("* DSÖ 2021 Kılavuzu & OECD İstatistiki Yaşam Değeri (VSL) yaklaşımı.")

    st.write("")

    # ========================================================
    # 4. İL BAZLI MALİYET DAĞILIMI (EN ÇOK ETKİLENEN 10 İL & TABLO)
    # ========================================================
    with st.expander("İl Bazlı Sağlık Faturası Sıralaması & Metodoloji Detayı"):
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("##### En Yüksek Toplam Sağlık Yüküne Sahip 10 İl")
            top_cost = df.sort_values(by="maliyet_milyon_tl", ascending=False).head(10)
            fig_cost = go.Figure(go.Bar(
                x=top_cost["maliyet_milyon_tl"],
                y=top_cost["il"],
                orientation="h",
                marker=dict(
                    color=top_cost["maliyet_milyon_tl"],
                    colorscale="Reds",
                    line=dict(color="rgba(255,255,255,0.1)", width=1)
                ),
                text=[f"{v:,.0f} Milyon ₺" for v in top_cost["maliyet_milyon_tl"]],
                textposition="outside"
            ))
            fig_cost.update_layout(
                height=320,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(autorange="reversed", tickfont=dict(color="#cbd5e1")),
                xaxis=dict(tickfont=dict(color="#94a3b8"), gridcolor="rgba(255,255,255,0.05)"),
                margin=dict(t=10, l=10, r=40, b=10)
            )
            st.plotly_chart(fig_cost, use_container_width=True)

        with col_t2:
            st.markdown("##### En Yüksek Kişi Başı Kirlilik Maliyetine Sahip 10 İl")
            df_temp = df.copy()
            df_temp["kisi_basi_tl"] = ((df_temp["maliyet_milyon_tl"] * 1_000_000) / df_temp["nufus"]).round(0)
            top_capita = df_temp.sort_values(by="kisi_basi_tl", ascending=False).head(10)
            fig_capita = go.Figure(go.Bar(
                x=top_capita["kisi_basi_tl"],
                y=top_capita["il"],
                orientation="h",
                marker=dict(
                    color=top_capita["kisi_basi_tl"],
                    colorscale="YlOrRd",
                    line=dict(color="rgba(255,255,255,0.1)", width=1)
                ),
                text=[f"{int(v):,} ₺" for v in top_capita["kisi_basi_tl"]],
                textposition="outside"
            ))
            fig_capita.update_layout(
                height=320,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(autorange="reversed", tickfont=dict(color="#cbd5e1")),
                xaxis=dict(tickfont=dict(color="#94a3b8"), gridcolor="rgba(255,255,255,0.05)"),
                margin=dict(t=10, l=10, r=40, b=10)
            )
            st.plotly_chart(fig_capita, use_container_width=True)

        st.markdown("##### 81 İl Sağlık & Ekonomik Yük Veri Tablosu")
        cost_table_df = df[["il", "bolge", "nufus", "pm25", "maliyet_milyon_tl"]].copy()
        cost_table_df["kisi_basi_tl"] = ((cost_table_df["maliyet_milyon_tl"] * 1_000_000) / cost_table_df["nufus"]).round(0)
        cost_table_df = cost_table_df.sort_values(by="maliyet_milyon_tl", ascending=False)
        st.dataframe(
            cost_table_df.rename(columns={
                "il": "İl", "bolge": "Bölge", "nufus": "Nüfus",
                "pm25": "PM2.5 (µg/m³)", "maliyet_milyon_tl": "Maliyet (Milyon ₺)",
                "kisi_basi_tl": "Kişi Başı Yük (₺)"
            }),
            use_container_width=True,
            hide_index=True
        )
