"""
Birim Testleri: OSB alanı (hektar) ayrıştırma doğruluğu
"""

import pytest
import pandas as pd
from data_sources.local_official_data import parse_sanayi_osb
from analytics.summaries import to_tr_num

def test_raw_sanayi_vs_master_data_all_81_provinces():
    """81 ilin tamamında ham sanayi.txt toplamı ile master_data.csv osb_alani_hektar değerinin birebir aynı olduğunu doğrular."""
    df_raw = parse_sanayi_osb("data/sanayi.txt")
    df_master = pd.read_csv("data/master_data.csv")

    assert len(df_master) == 81, f"Beklenen 81 il, mevcut {len(df_master)}"
    assert len(df_raw) == 81, f"Beklenen 81 il, ham {len(df_raw)}"

    merged = pd.merge(
        df_master[["il", "osb_alani_hektar"]],
        df_raw[["il", "osb_alani_hektar"]],
        on="il",
        suffixes=("_master", "_raw")
    )

    mismatches = []
    for idx, row in merged.iterrows():
        il = row["il"]
        val_m = row["osb_alani_hektar_master"]
        val_r = row["osb_alani_hektar_raw"]
        if abs(val_m - val_r) > 0.05:
            mismatches.append((il, val_m, val_r))

    assert len(mismatches) == 0, f"81 ilde OSB hektar uyuşmazlığı tespit edildi: {mismatches}"


def test_osb_benchmarks_istanbul_ankara_izmir():
    """İstanbul, Ankara ve İzmir için OSB alanlarının ham veriden beklenen değerlerde ve formatta olduğunu doğrular."""
    df_master = pd.read_csv("data/master_data.csv")

    ist_val = df_master.loc[df_master["il"] == "İstanbul", "osb_alani_hektar"].iloc[0]
    ank_val = df_master.loc[df_master["il"] == "Ankara", "osb_alani_hektar"].iloc[0]
    izm_val = df_master.loc[df_master["il"] == "İzmir", "osb_alani_hektar"].iloc[0]

    # Sayısal değerler (float)
    assert ist_val == 2424.7, f"İstanbul OSB hektar hatalı: {ist_val}"
    assert ank_val == 9173.5, f"Ankara OSB hektar hatalı: {ank_val}"
    assert izm_val == 5070.8, f"İzmir OSB hektar hatalı: {izm_val}"

    # Ekrana basılan Türkçe formatlı metinler
    assert to_tr_num(ist_val, 1) == "2.424,7"
    assert to_tr_num(ank_val, 1) == "9.173,5"
    assert to_tr_num(izm_val, 1) == "5.070,8"
