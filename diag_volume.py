import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import pandas as pd, numpy as np

df = pd.read_csv("worldcup_all.csv")
for c in ["minutes", "goals", "assists"]:
    df[c] = pd.to_numeric(df[c].astype(str).str.replace(",", "", regex=False), errors="coerce")
df["ga_eff"] = df["goals"].fillna(0) + df["assists"].fillna(0)
df["is_fw"] = df["pos"].str.contains("FW", na=False)
g = (df.groupby("player")
       .agg(mins=("minutes", "sum"), goals=("goals", "sum"), assists=("assists", "sum"),
            ga=("ga_eff", "sum"), wcs=("wc_year", "nunique"), fw=("is_fw", "max")).reset_index())
g = g[(g["fw"]) & (g["mins"] >= 90)].copy()
g["ga90"] = g["ga"] / g["mins"] * 90
g = g[g["ga90"] <= g["ga90"].quantile(0.995)]
mv = g[g["player"].str.contains("Messi", case=False, na=False)]["ga90"].iloc[0]

print("Ranking de Messi segun cuanto volumen de carrera exijas:")
print(f"{'umbral min':>12} | {'N atacantes':>11} | {'mejores q Messi':>15} | {'top de':>8}")
for thr in [90, 270, 450, 700, 1000, 1500, 2000, 2314]:
    sub = g[g["mins"] >= thr]
    better = int((sub["ga90"] > mv).sum())
    print(f"{thr:>12} | {len(sub):>11} | {better:>15} | {better+1:>4}/{len(sub)}")

print()
print("Atacantes con >= 2000 min de carrera mundialista, ordenados por G+A/90:")
elite = g[g["mins"] >= 2000].sort_values("ga90", ascending=False).copy()
elite["ga90"] = elite["ga90"].round(3)
elite["rk"] = range(1, len(elite) + 1)
print(elite[["rk", "player", "wcs", "mins", "goals", "assists", "ga90"]].to_string(index=False))
