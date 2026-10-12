"""
Korelasyon ve Doğrusal Regresyon Analiz Motoru
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any, Tuple, List, Optional

def calculate_bivariate_correlation(
    x: pd.Series, 
    y: pd.Series
) -> Dict[str, Any]:
    """
    İki değişken arasındaki Pearson ve Spearman korelasyon katsayılarını,
    p-değerlerini ve OLS regresyon parametrelerini hesaplar.
    """
    valid_mask = x.notna() & y.notna()
    x_clean = x[valid_mask].astype(float)
    y_clean = y[valid_mask].astype(float)
    
    n = len(x_clean)
    if n < 3:
        return {
            "n": n, "pearson_r": 0.0, "pearson_p": 1.0,
            "spearman_rho": 0.0, "spearman_p": 1.0,
            "r_squared": 0.0, "slope": 0.0, "intercept": 0.0,
            "std_err": 0.0, "p_value_ols": 1.0
        }
        
    pearson_r, pearson_p = stats.pearsonr(x_clean, y_clean)
    spearman_rho, spearman_p = stats.spearmanr(x_clean, y_clean)
    
    # OLS Doğrusal Regresyon
    reg = stats.linregress(x_clean, y_clean)
    
    return {
        "n": n,
        "pearson_r": round(float(pearson_r), 3),
        "pearson_p": float(pearson_p),
        "spearman_rho": round(float(spearman_rho), 3),
        "spearman_p": float(spearman_p),
        "r_squared": round(float(reg.rvalue ** 2), 3),
        "slope": round(float(reg.slope), 4),
        "intercept": round(float(reg.intercept), 2),
        "std_err": round(float(reg.stderr), 4),
        "p_value_ols": float(reg.pvalue),
        "x_values": x_clean.tolist(),
        "y_values": y_clean.tolist()
    }

def calculate_correlation_matrix(
    df: pd.DataFrame, 
    columns: Optional[List[str]] = None,
    method: str = "pearson"
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Belirtilen sütunlar arasında korelasyon ve p-değeri matrisini üretir.
    """
    if columns is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        # İdari plaka ve koordinatları çıkar
        exclude = ["plaka", "lat", "lon"]
        columns = [c for c in numeric_cols if c not in exclude]
        
    sub_df = df[columns].dropna()
    n_cols = len(columns)
    
    corr_matrix = pd.DataFrame(np.zeros((n_cols, n_cols)), index=columns, columns=columns)
    pval_matrix = pd.DataFrame(np.zeros((n_cols, n_cols)), index=columns, columns=columns)
    
    for i, col1 in enumerate(columns):
        for j, col2 in enumerate(columns):
            if i == j:
                corr_matrix.iloc[i, j] = 1.0
                pval_matrix.iloc[i, j] = 0.0
            else:
                s1 = sub_df[col1]
                s2 = sub_df[col2]
                if method == "spearman":
                    r, p = stats.spearmanr(s1, s2)
                else:
                    r, p = stats.pearsonr(s1, s2)
                corr_matrix.iloc[i, j] = round(float(r), 3)
                pval_matrix.iloc[i, j] = float(p)
                
    return corr_matrix, pval_matrix


def calculate_bootstrap_ci(
    x: pd.Series, 
    y: pd.Series, 
    method: str = "pearson", 
    n_boot: int = 1000, 
    alpha: float = 0.05, 
    seed: int = 42
) -> Tuple[float, float]:
    """
    x ve y serileri arasındaki korelasyon katsayısı için n_boot iterasyonlu
    %95 Bootstrap güven aralığını türetir.
    """
    x_s = pd.Series(x)
    y_s = pd.Series(y)
    valid = x_s.notna() & y_s.notna()
    x_arr = x_s[valid].to_numpy(dtype=float)
    y_arr = y_s[valid].to_numpy(dtype=float)
    n = len(x_arr)
    if n < 5:
        return (0.0, 0.0)

    rng = np.random.default_rng(seed)
    idx = rng.choice(n, size=(n_boot, n), replace=True)
    xb = x_arr[idx]
    yb = y_arr[idx]

    if method == "pearson":
        x_dev = xb - xb.mean(axis=1, keepdims=True)
        y_dev = yb - yb.mean(axis=1, keepdims=True)
        num = (x_dev * y_dev).sum(axis=1)
        den = np.sqrt((x_dev**2).sum(axis=1) * (y_dev**2).sum(axis=1))
        den = np.where(den == 0, 1e-9, den)
        boot_corrs = num / den
    else:
        boot_corrs = np.empty(n_boot)
        for b in range(n_boot):
            r_val, _ = stats.spearmanr(xb[b], yb[b])
            boot_corrs[b] = r_val if not np.isnan(r_val) else 0.0

    ci_low = float(np.percentile(boot_corrs, 100 * (alpha / 2)))
    ci_high = float(np.percentile(boot_corrs, 100 * (1 - alpha / 2)))
    return (round(ci_low, 3), round(ci_high, 3))


def fit_multivariate_ols(
    df: pd.DataFrame,
    y_col: str = "pm25",
    x_cols: Optional[List[str]] = None,
    feature_labels: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Çoklu OLS regresyon modeli (statsmodels veya saf numpy/scipy fallback).
    Model: y = β₀ + β₁X₁ + ... + βₖXₖ + ε
    """
    if x_cols is None:
        x_cols = ["toplam_osb", "rakim", "nufus"]

    available_x = [c for c in x_cols if c in df.columns]
    if not available_x or y_col not in df.columns:
        return {"success": False, "error": "Model için gerekli değişkenler bulunamadı."}

    sub_df = df[[y_col] + available_x].dropna()
    n = len(sub_df)
    k = len(available_x)
    if n <= k + 1:
        return {"success": False, "error": "Gözlem sayısı yetersiz."}

    y = sub_df[y_col].to_numpy(dtype=float)
    X = sub_df[available_x].to_numpy(dtype=float)

    labels = feature_labels or {}
    names = ["Sabit Terim (β₀)"] + [labels.get(c, c) for c in available_x]

    # 1. statsmodels dene
    try:
        import statsmodels.api as sm
        X_sm = sm.add_constant(X)
        model = sm.OLS(y, X_sm).fit()

        coef_df = pd.DataFrame({
            "Degisken": names,
            "Kolon": ["const"] + available_x,
            "Katsayi": model.params,
            "Std_Hata": model.bse,
            "t_degeri": model.tvalues,
            "p_degeri": model.pvalues,
            "CI_alt": model.conf_int()[0],
            "CI_ust": model.conf_int()[1]
        })

        return {
            "success": True,
            "r2": float(model.rsquared),
            "adj_r2": float(model.rsquared_adj),
            "f_stat": float(model.fvalue),
            "f_pval": float(model.f_pvalue),
            "n": int(n),
            "k": int(k),
            "coef_df": coef_df,
            "residuals": model.resid,
            "y_pred": model.fittedvalues,
            "y_true": y,
            "sub_df": sub_df
        }
    except Exception:
        pass

    # 2. Saf numpy fallback
    X_mat = np.column_stack([np.ones(n), X])
    beta = np.linalg.solve(X_mat.T @ X_mat, X_mat.T @ y)
    y_pred = X_mat @ beta
    resid = y - y_pred
    df_resid = n - k - 1
    sse = float(np.sum(resid ** 2))
    sst = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - (sse / sst) if sst > 0 else 0.0
    adj_r2 = 1.0 - (1.0 - r2) * ((n - 1) / df_resid) if df_resid > 0 else 0.0
    mse = sse / df_resid if df_resid > 0 else 1.0
    var_beta = mse * np.linalg.inv(X_mat.T @ X_mat)
    se_beta = np.sqrt(np.maximum(np.diag(var_beta), 1e-12))
    t_stats = beta / se_beta
    p_vals = [float(2 * (1 - stats.t.cdf(np.abs(t), df=df_resid))) for t in t_stats]
    msm = (sst - sse) / k if k > 0 else 0.0
    f_stat = msm / mse if mse > 0 else 0.0
    f_pval = float(1.0 - stats.f.cdf(f_stat, k, df_resid)) if df_resid > 0 else 1.0

    t_crit = float(stats.t.ppf(0.975, df=df_resid))
    ci_alt = beta - t_crit * se_beta
    ci_ust = beta + t_crit * se_beta

    coef_df = pd.DataFrame({
        "Degisken": names,
        "Kolon": ["const"] + available_x,
        "Katsayi": beta,
        "Std_Hata": se_beta,
        "t_degeri": t_stats,
        "p_degeri": p_vals,
        "CI_alt": ci_alt,
        "CI_ust": ci_ust
    })

    return {
        "success": True,
        "r2": float(r2),
        "adj_r2": float(adj_r2),
        "f_stat": float(f_stat),
        "f_pval": float(f_pval),
        "n": int(n),
        "k": int(k),
        "coef_df": coef_df,
        "residuals": resid,
        "y_pred": y_pred,
        "y_true": y,
        "sub_df": sub_df
    }


def calculate_moran_global(
    df: pd.DataFrame,
    value_col: str = "pm25",
    k: int = 5,
    weight_type: str = "knn",
    n_permutations: int = 999,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Global Moran's I mekânsal otokorelasyon katsayısı ve permütasyon testi.
    """
    sub = df[["il", "lat", "lon", value_col]].dropna().copy()
    if "bolge" in df.columns:
        sub["bolge"] = df["bolge"]
    n = len(sub)
    if n < 10:
        return {"success": False, "error": "Mekânsal analiz için yetersiz il sayısı."}

    coords = sub[["lat", "lon"]].to_numpy(dtype=float)
    diff = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]
    dists = np.sqrt(np.sum(diff**2, axis=-1))

    W = np.zeros((n, n), dtype=float)
    if weight_type == "idw":
        np.fill_diagonal(dists, np.inf)
        W = 1.0 / dists
        np.fill_diagonal(W, 0.0)
    else:
        for i in range(n):
            nn_idx = np.argsort(dists[i])[1:k+1]
            W[i, nn_idx] = 1.0

    row_sums = W.sum(axis=1, keepdims=True)
    row_sums = np.where(row_sums == 0, 1.0, row_sums)
    W = W / row_sums

    x = sub[value_col].to_numpy(dtype=float)
    sub["val"] = x
    x_mean = np.mean(x)
    std_x = np.std(x, ddof=0)
    z = (x - x_mean) / (std_x if std_x > 0 else 1.0)
    wz = np.dot(W, z)

    sum_z2 = np.sum(z**2)
    moran_i = float(np.sum(z * wz) / sum_z2) if sum_z2 > 0 else 0.0
    expected_i = float(-1.0 / (n - 1))

    rng = np.random.default_rng(seed)
    perm_i = np.empty(n_permutations)
    for b in range(n_permutations):
        z_perm = rng.permutation(z)
        perm_i[b] = np.sum(z_perm * np.dot(W, z_perm)) / (sum_z2 if sum_z2 > 0 else 1.0)

    pseudo_p = float((np.sum(perm_i >= moran_i) + 1) / (n_permutations + 1))
    std_perm = np.std(perm_i)
    z_score = float((moran_i - np.mean(perm_i)) / (std_perm if std_perm > 0 else 1e-9))

    quadrant_labels = []
    quadrant_codes = []
    for zi, wzi in zip(z, wz):
        if zi >= 0 and wzi >= 0:
            quadrant_labels.append("High-High (Sıcak Nokta)")
            quadrant_codes.append("HH")
        elif zi < 0 and wzi >= 0:
            quadrant_labels.append("Low-High (Mekânsal Aykırı)")
            quadrant_codes.append("LH")
        elif zi < 0 and wzi < 0:
            quadrant_labels.append("Low-Low (Soğuk Nokta)")
            quadrant_codes.append("LL")
        else:
            quadrant_labels.append("High-Low (Mekânsal Aykırı)")
            quadrant_codes.append("HL")

    sub["z_score"] = z
    sub["spatial_lag_z"] = wz
    sub["quadrant"] = quadrant_labels
    sub["quadrant_code"] = quadrant_codes

    return {
        "success": True,
        "moran_i": moran_i,
        "expected_i": expected_i,
        "p_value": pseudo_p,
        "z_score": z_score,
        "n": n,
        "k": k,
        "weight_type": weight_type,
        "df_moran": sub,
        "quadrant_counts": sub["quadrant"].value_counts().to_dict()
    }

