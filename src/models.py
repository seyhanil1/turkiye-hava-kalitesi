import pandas as pd
import statsmodels.api as sm

def analyze_health_impact():
    # 1. Veriyi Oku
    df = pd.read_csv("data/turkey_industrial_health_data.csv")
    
    print("=" * 60)
    print("TÜRKİYE SANAYİ - HAVA KİRLİLİĞİ VE SAĞLIK MODELLEMESİ")
    print("=" * 60)
    
    # 2. MODEL 1: Kirlilik Dinamikleri (Fabrika & Çanak Etkisi -> PM2.5)
    # PM2.5 kirleticisini fabrika sayısı ve enversiyon gün sayısı ile açıklıyoruz
    X1 = df[["fabrika_sayisi", "inversiyon_gun", "arac_sayisi"]]
    X1 = sm.add_constant(X1)
    y1 = df["pm25_yillik_ort"]
    
    model1 = sm.OLS(y1, X1).fit()
    print("\n>>> MODEL 1 SONUCU: Kirletici Konsantrasyonu (PM2.5) Belirleyicileri")
    print(f"R-squared: {model1.rsquared:.4f}")
    for col, pval, coef in zip(X1.columns, model1.pvalues, model1.params):
        significance = "***" if pval < 0.001 else ("**" if pval < 0.01 else ("*" if pval < 0.05 else ""))
        print(f" - {col:<18}: Katsayı = {coef:>8.4f} | P-Değeri = {pval:.4e} {significance}")

    # 3. MODEL 2: Sağlık Çıktısı (PM2.5 -> Solunum Yolu Ölüm Oranı)
    X2 = df[["pm25_yillik_ort", "arac_sayisi"]]
    X2 = sm.add_constant(X2)
    y2 = df["solunum_olum_yuzbinkisi"]
    
    model2 = sm.OLS(y2, X2).fit()
    print("\n>>> MODEL 2 SONUCU: Solunum Yolu Hastalık Riski (100k Kişi Başına)")
    print(f"R-squared: {model2.rsquared:.4f}")
    for col, pval, coef in zip(X2.columns, model2.pvalues, model2.params):
        significance = "***" if pval < 0.001 else ("**" if pval < 0.01 else ("*" if pval < 0.05 else ""))
        print(f" - {col:<18}: Katsayı = {coef:>8.4f} | P-Değeri = {pval:.4e} {significance}")
    
    print("\n" + "=" * 60)
    print("ÖZET YORUM:")
    print(f"Fabrika sayısındaki her 100 birimlik artış, yıllık PM2.5 seviyesini ortalama {model1.params['fabrika_sayisi']*100:.2f} µg/m³ artırmaktadır.")
    print(f"PM2.5'teki her 10 µg/m³ artış ise 100 bin kişi başına solunum kaynaklı ölümleri {model2.params['pm25_yillik_ort']*10:.2f} kişi yükseltmektedir.")
    print("=" * 60)

if __name__ == "__main__":
    analyze_health_impact()