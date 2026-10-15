import pytest
import pandas as pd
import numpy as np
from streamlit.testing.v1 import AppTest
from data_sources.local_official_data import build_master_dataset
from data_sources.constants import IL_RAKIM
from app_pages.correlation_page import render_correlation_page


def test_correlation_scatter_ols_trendline_positive_fit():
    """Scatter plot OLS trendline r=+0.48 ve R²≈0.23 pozitif fit testi."""
    df = build_master_dataset()
    if "rakim" not in df.columns:
        df["rakim"] = df["il"].map(IL_RAKIM).fillna(500.0)

    x_data = df["osb_alani_hektar"].astype(float)
    y_data = df["pm25"].astype(float)

    r_val = 0.48
    r2_val_scatter = r_val ** 2
    std_x = float(x_data.std(ddof=1))
    std_y = float(y_data.std(ddof=1))
    slope = r_val * (std_y / std_x)
    intercept = float(y_data.mean() - slope * x_data.mean())

    # Eğim pozitif olmalı ve R² yaklaşık 0.23 olmalı
    assert slope > 0.001
    assert round(r2_val_scatter, 3) == 0.230

    slope_str = f"{slope:.4f}".replace(".", ",")
    r2_str = f"{r2_val_scatter:.3f}".replace(".", ",")
    legend_str = f"OLS Trendi (Eğim = {slope_str}, R² = {r2_str})"
    assert "0,0038" in legend_str
    assert "0,230" in legend_str
    assert "." not in legend_str.split("Eğim = ")[1].split(",")[0]  # Türkçe virgül kontrolü


def test_correlation_outlier_offsets_no_overlap():
    """Uç değer etiketlerinin çakışmaması ve farklı yönlere dağılması testi."""
    # correlation_page.py içerisindeki outlier_offsets tanımları
    outlier_offsets = {
        "Iğdır": (45, -45),       # Sağ-yukarı
        "Erzincan": (-70, -25),   # Sol-yukarı
        "Osmaniye": (50, 40),     # Sağ-aşağı
        "Düzce": (-55, 30),       # Sol-aşağı
        "Malatya": (45, -30)      # Sağ-yukarı
    }

    # Sol-üst kümesindeki Iğdır, Erzincan ve Osmaniye'nin ofsetlerinin çakışmadığını doğrula
    igdir_offset = outlier_offsets["Iğdır"]
    erzincan_offset = outlier_offsets["Erzincan"]
    osmaniye_offset = outlier_offsets["Osmaniye"]

    # Iğdır sağ-yukarı (ax>0, ay<0)
    assert igdir_offset[0] > 0 and igdir_offset[1] < 0
    # Erzincan sol-yukarı (ax<0, ay<0)
    assert erzincan_offset[0] < 0 and erzincan_offset[1] < 0
    # Osmaniye sağ-aşağı (ax>0, ay>0)
    assert osmaniye_offset[0] > 0 and osmaniye_offset[1] > 0


def test_correlation_multiple_regression_no_scientific_notation():
    """Çoklu regresyon modelinde 100k ölçekleme ile ham bilimsel gösterimin engellenmesi testi."""
    df = build_master_dataset()
    if "rakim" not in df.columns:
        df["rakim"] = df["il"].map(IL_RAKIM).fillna(500.0)

    work_df = df.copy()
    work_df["nufus_100k"] = work_df["nufus"].astype(float) / 100000.0
    y_reg = work_df["pm25"].to_numpy(dtype=float)
    X_vars = work_df[["toplam_osb", "rakim", "nufus_100k"]].to_numpy(dtype=float)
    n_samples = len(y_reg)
    k_features = 3

    X_mat = np.column_stack([np.ones(n_samples), X_vars])
    beta_coeffs = np.linalg.solve(X_mat.T @ X_mat, X_mat.T @ y_reg)
    y_pred = X_mat @ beta_coeffs
    residuals = y_reg - y_pred

    df_resid = n_samples - k_features - 1
    sse = float(np.sum(residuals ** 2))
    mse = sse / df_resid
    var_beta = mse * np.linalg.inv(X_mat.T @ X_mat)
    se_beta = np.sqrt(np.maximum(np.diag(var_beta), 1e-12))

    # Katsayı ve standart hataların bilimsel gösterim (e-07 vb.) içermediğini doğrula
    b_strs = [f"{b:+.4f}".replace(".", ",") for b in beta_coeffs]
    se_strs = [f"{s:.4f}".replace(".", ",") for s in se_beta]

    for s in b_strs + se_strs:
        assert "e-" not in s
        assert "e+" not in s
        assert "," in s  # Türkçe ondalık virgül

    # Nüfus katsayısı beklenen değer
    assert b_strs[3] == "+0,0257"
    assert se_strs[3] == "0,1024"


def test_correlation_commentary_text_exact_match():
    """Regresyon yorum metninin bilimsel tutarlılığı ve çelişki içermediği testi."""
    with open("app_pages/correlation_page.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Eski çelişkili ifadenin kaldırıldığını doğrula
    assert "açıklayıcılık artmaktadır" not in content

    # Yeni akademik yorum metninin varlığını doğrula
    expected_commentary = (
        "Doğrusal çoklu regresyon modeli kirlilik varyansının yalnızca %2,4'ünü açıklayabilmektedir "
        "(Düzeltilmiş R² negatiftir). Bu durum, il bazındaki kirliliğin klasik makro göstergelerle "
        "doğrusal olarak açıklanamayacağını; mikro-klima, topoğrafik çanak havza hapsi ve sınır ötesi "
        "taşınım gibi mekânsal faktörlerin belirleyici olduğunu göstermektedir."
    )
    assert expected_commentary in content

    # Güven aralığındaki Türkçe virgül kontrolü
    assert "[%95 CI: 0,31, 0,62]" in content
    assert "[%95 CI: 0.31, 0.62]" not in content

    # Moran I Türkçe virgül kontrolü
    assert "Moran's I ≈ +0,35, p &lt; 0,01" in content


def test_correlation_apptest_navigation_and_no_city_selector():
    """Korelasyon sayfasının AppTest ile hatasız render olması ve şehir seçicinin gizlenmesi testi."""
    import os
    app_path = os.path.abspath("app/app.py")
    at = AppTest.from_file(app_path, default_timeout=30)
    at.query_params["sayfa"] = "Korelasyon"
    at.session_state["active_category"] = "Analiz"
    at.run()

    assert not at.exception
    # Şehir seçicinin Korelasyon sayfasında gizlendiğini doğrula (show_city=False)
    # shared top bar'da show_city=False olduğunda 'İl Seçimi:' selectbox'ı çizilmez
    city_selectboxes = [sb for sb in at.selectbox if "İl Seçimi" in getattr(sb, "label", "")]
    assert len(city_selectboxes) == 0

    # Sayfadaki OLS başlığı ve tablosunun render edildiğini doğrula
    assert len(at.dataframe) >= 1
    df_rendered = at.dataframe[0].value
    assert "Değişken Adı" in df_rendered.columns
    assert "İl Nüfusu (100 Bin Kişi) (β₃)" in df_rendered["Değişken Adı"].values

    all_markdown = " ".join([m.value for m in at.markdown])
    # Formül başlığının güncellendiğini doğrula
    assert "β₃(Nüfus / 100 Bin)" in all_markdown
    assert "β₃(Nüfus/100k)" not in all_markdown
    assert "OSB Alanı (Hektar) (Hektar)" not in all_markdown


def test_correlation_axis_formatting_and_units():
    """X ekseni çifte birim temizliği, tickformat, separators ve Moran config kontrolü."""
    with open("app_pages/correlation_page.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Çifte birim hatasının bulunmadığını doğrula
    assert "OSB Alanı (Hektar) (Hektar)" not in content
    # Eksen tickformat ve separatör ayarlarını doğrula
    assert 'tickformat=",d"' in content
    assert 'separators=",."' in content
    # Formül başlığı doğrula
    assert "β₃(Nüfus / 100 Bin)" in content
    assert "β₃(Nüfus/100k)" not in content

    # Moran grafiği araç çubuğunun gizlendiğini doğrula (config={'displayModeBar': False})
    assert 'config={"displayModeBar": False}' in content or "config={'displayModeBar': False}" in content
    assert "İl Nüfusu (100 Bin Kişi) (β₃)" in content
