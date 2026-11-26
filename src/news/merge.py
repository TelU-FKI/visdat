"""Gabung shard A-C jadi satu CSV, deduplikasi judul, urut tanggal."""
import re
from pathlib import Path

import pandas as pd

D = Path(__file__).resolve().parents[2] / "data" / "news"
df = pd.concat([pd.read_csv(D / f"shard_{s}.csv") for s in "ABC"], ignore_index=True)
df["_k"] = df["judul"].str.lower().str.replace(r"\s+", " ", regex=True).str.strip()
df = df.drop_duplicates("_k").drop(columns="_k").sort_values(["tanggal", "judul"])
df.insert(0, "id", range(1, len(df) + 1))
df.to_csv(D / "berita_ihsg_2026.csv", index=False, encoding="utf-8")
print(len(df), df.tanggal.min(), df.tanggal.max(), df.sumber.nunique())
