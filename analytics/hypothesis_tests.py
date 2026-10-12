"""
Hipotez Testleri ve İstatistiki Karar Motoru
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu

Desteklenen Testler:
1. İki Örneklem Testleri (Şehir Düellosu ve Grup Karşılaştırmaları):
   - Shapiro-Wilk Normallik Testi
   - Levene Varyans Homojenliği Testi
   - Bağımsız İki Örneklem t-Testi / Welch t-Testi (Parametrik)
   - Mann-Whitney U Testi (Parametrik Olmayan)
   - Etki Büyüklüğü (Cohen's d veya Rank-Biserial r)
2. Çoklu Grup Testleri (7 Coğrafi Bölge Analizi):
   - Tek Yönlü ANOVA (F-Testi)
   - Kruskal-Wallis H-Testi
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any, List, Union

def run_two_sample_test(
    group1: Union[pd.Series, np.ndarray, list],
    group2: Union[pd.Series, np.ndarray, list],
    label1: str = "Grup A",
    label2: str = "Grup B",
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    İki bağımsız grup arasında istatistiksel fark olup olmadığını hipotez testleri ile inceler.
    Otomatik normallik ve varyans homojenliği kontrolü yaparak en uygun testi seçer.
    """
    s1 = pd.Series(group1).dropna().astype(float)
    s2 = pd.Series(group2).dropna().astype(float)
    
    n1, n2 = len(s1), len(s2)
    if n1 < 3 or n2 < 3:
        return {
            "success": False,
            "message": f"Hipotez testi için yeterli örneklem yok (n1={n1}, n2={n2}). En az 3 geçerli gözlem gereklidir."
        }
        
    m1, m2 = float(s1.mean()), float(s2.mean())
    med1, med2 = float(s1.median()), float(s2.median())
    std1, std2 = float(s1.std(ddof=1)), float(s2.std(ddof=1))
    
    # 1. Varsayım Kontrolleri: Normallik Testi (Shapiro-Wilk)
    # n < 3 ise test yapılamaz, n > 5000 ise ilk 5000 alınır
    shapiro1_stat, shapiro1_p = stats.shapiro(s1.iloc[:5000]) if n1 >= 3 else (1.0, 1.0)
    shapiro2_stat, shapiro2_p = stats.shapiro(s2.iloc[:5000]) if n2 >= 3 else (1.0, 1.0)
    
    normal1 = shapiro1_p > alpha
    normal2 = shapiro2_p > alpha
    both_normal = normal1 and normal2
    
    # 2. Varsayım Kontrolü: Varyans Homojenliği (Levene Testi)
    try:
        levene_stat, levene_p = stats.levene(s1, s2)
        equal_var = levene_p > alpha
    except Exception:
        levene_stat, levene_p = 0.0, 1.0
        equal_var = True
        
    # 3. Test Seçimi ve Uygulanması
    if both_normal:
        if equal_var:
            test_name = "Student's Bağımsız İki Örneklem t-Testi"
            test_type = "Parametrik"
            res = stats.ttest_ind(s1, s2, equal_var=True)
        else:
            test_name = "Welch's t-Testi (Eşit Olmayan Varyanslar)"
            test_type = "Parametrik"
            res = stats.ttest_ind(s1, s2, equal_var=False)
            
        test_stat = float(res.statistic)
        p_val = float(res.pvalue)
        
        # Cohen's d Etki Büyüklüğü
        pooled_std = np.sqrt(((n1 - 1) * (std1**2) + (n2 - 1) * (std2**2)) / (n1 + n2 - 2)) if (n1 + n2 > 2) else 1.0
        effect_size = (m1 - m2) / pooled_std if pooled_std > 0 else 0.0
        effect_label = "Cohen's d"
        
    else:
        test_name = "Mann-Whitney U Testi (Wilcoxon Sıra Toplamı)"
        test_type = "Parametrik Olmayan"
        res = stats.mannwhitneyu(s1, s2, alternative="two-sided")
        test_stat = float(res.statistic)
        p_val = float(res.pvalue)
        
        # Rank-Biserial Korelasyon (r)
        u_val = test_stat
        effect_size = 1.0 - (2.0 * u_val) / (n1 * n2)
        effect_label = "Rank-Biserial r"
        
    # 4. Hipotez Kararı
    h0 = f"H₀: {label1} ile {label2} grupları arasında hava kalitesi açısından fark yoktur."
    h1 = f"H₁: {label1} ile {label2} grupları arasında istatistiksel olarak anlamlı bir fark vardır."
    
    is_significant = p_val < alpha
    if is_significant:
        decision = f"H₀ REDDEDİLDİ (p = {p_val:.4e} < {alpha}). İki grup arasında istatistiksel olarak anlamlı bir fark bulunmaktadır."
    else:
        decision = f"H₀ REDDEDİLEMEDİ (p = {p_val:.4f} >= {alpha}). Gözlemlenen fark örneklem şansına bağlı olabilir, istatistiksel olarak anlamlı değildir."
        
    # Etki Büyüklüğü Yorumu
    abs_eff = abs(effect_size)
    if abs_eff < 0.2:
        eff_desc = "İhmal Edilebilir Düzeyde Etki"
    elif abs_eff < 0.5:
        eff_desc = "Küçük Düzeyde Etki"
    elif abs_eff < 0.8:
        eff_desc = "Orta Düzeyde Etki"
    else:
        eff_desc = "Geniş / Güçlü Düzeyde Etki"
        
    return {
        "success": True,
        "label1": label1,
        "label2": label2,
        "n1": n1,
        "n2": n2,
        "mean1": round(m1, 2),
        "mean2": round(m2, 2),
        "median1": round(med1, 2),
        "median2": round(med2, 2),
        "std1": round(std1, 2),
        "std2": round(std2, 2),
        "normality1": {"shapiro_p": round(float(shapiro1_p), 4), "is_normal": normal1},
        "normality2": {"shapiro_p": round(float(shapiro2_p), 4), "is_normal": normal2},
        "levene_test": {"p_value": round(float(levene_p), 4), "equal_var": equal_var},
        "test_name": test_name,
        "test_type": test_type,
        "test_statistic": round(test_stat, 4),
        "p_value": p_val,
        "is_significant": is_significant,
        "h0": h0,
        "h1": h1,
        "decision": decision,
        "effect_size": round(float(effect_size), 3),
        "effect_label": effect_label,
        "effect_description": eff_desc
    }

def run_regional_anova(
    df: pd.DataFrame, 
    group_col: str = "bolge", 
    val_col: str = "pm25",
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    7 Coğrafi bölge arasında Tek Yönlü ANOVA ve Kruskal-Wallis testlerini çalıştırır.
    """
    groups = [group[val_col].dropna().values for _, group in df.groupby(group_col)]
    group_names = [name for name, _ in df.groupby(group_col)]
    
    if len(groups) < 2:
        return {"success": False, "message": "En az 2 bölge grubu gereklidir."}
        
    # Levene Varyans Homojenliği
    try:
        levene_stat, levene_p = stats.levene(*groups)
        equal_var = levene_p > alpha
    except Exception:
        levene_stat, levene_p = 0.0, 1.0
        equal_var = True
        
    # Tek Yönlü ANOVA
    f_stat, f_pval = stats.f_oneway(*groups)
    
    # Kruskal-Wallis (Parametrik olmayan eşdeğeri)
    h_stat, kw_pval = stats.kruskal(*groups)
    
    h0 = f"H₀: Türkiye'nin 7 coğrafi bölgesi arasında ortalama {val_col.upper()} kirlilik seviyeleri farksızdır."
    h1 = f"H₁: En az bir bölgenin ortalama {val_col.upper()} kirlilik seviyesi diğerlerinden anlamlı derecede farklıdır."
    
    is_sig_anova = f_pval < alpha
    is_sig_kw = kw_pval < alpha
    
    return {
        "success": True,
        "num_groups": len(groups),
        "group_names": group_names,
        "anova_f": round(float(f_stat), 3),
        "anova_p": float(f_pval),
        "anova_significant": is_sig_anova,
        "kruskal_h": round(float(h_stat), 3),
        "kruskal_p": float(kw_pval),
        "kruskal_significant": is_sig_kw,
        "levene_p": round(float(levene_p), 4),
        "equal_variance": equal_var,
        "h0": h0,
        "h1": h1,
        "interpretation": (
            f"ANOVA F-testi (F={f_stat:.2f}, p={f_pval:.4f}) ve Kruskal-Wallis testi (H={h_stat:.2f}, p={kw_pval:.4f}) sonucunda; "
            + ("bölgeler arasında hava kalitesi açısından istatistiksel olarak ANLAMLI FARK bulunmuştur." if (is_sig_anova or is_sig_kw)
               else "bölgeler arasında istatistiksel olarak anlamlı bir varyasyon tespit edilmemiştir.")
        )
    }
