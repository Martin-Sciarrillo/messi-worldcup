import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import pandas as pd, numpy as np
from scipy.stats import norm

df = pd.read_csv("worldcup_all.csv")
for c in ["minutes", "goals", "assists"]:
    df[c] = pd.to_numeric(df[c].astype(str).str.replace(",", "", regex=False), errors="coerce")

# G+A efectivo uniforme: goles + asistencias (NaN->0) para TODOS por igual
df["ga_eff"] = df["goals"].fillna(0) + df["assists"].fillna(0)
df["is_fw"] = df["pos"].str.contains("FW", na=False)

# AGREGAR POR CARRERA mundialista de cada jugador
g = (df.groupby("player")
       .agg(mins=("minutes", "sum"), goals=("goals", "sum"), assists=("assists", "sum"),
            ga=("ga_eff", "sum"), wcs=("wc_year", "nunique"), fw=("is_fw", "max"),
            squad=("squad", "last"))
       .reset_index())
g = g[(g["fw"]) & (g["mins"] >= 90)].copy()
g["ga90"] = g["ga"] / g["mins"] * 90
cap = g["ga90"].quantile(0.995)
g = g[g["ga90"] <= cap]

mu, sd = g["ga90"].mean(), g["ga90"].std()
me = g[g["player"].str.contains("Messi", case=False, na=False)].iloc[0]
z = (me["ga90"] - mu) / sd
p = norm.cdf(z) * 100
rank = int((g["ga90"] > me["ga90"]).sum())

print(f"CARRERA vs CARRERA | N={len(g)} atacantes | mu={mu:.3f} sd={sd:.3f} cap={cap:.2f}")
print(f"Messi carrera: ga90={me['ga90']:.3f} ({int(me['goals'])}G {int(me['assists'])}A "
      f"en {int(me['mins'])}min, {int(me['wcs'])} Mundiales) -> {z:.1f} sigma, percentil {p:.2f}%")
print(f"Carreras por encima de Messi: {rank} de {len(g)}  (Messi = top {rank+1})")
print()
print("TOP 25 carreras (min carrera >= 270 = 3 partidos):")
top = g[g["mins"] >= 270].sort_values("ga90", ascending=False).head(25).copy()
top["squad"] = top["squad"].str[2:]
top["ga90"] = top["ga90"].round(3)
print(top[["player", "squad", "wcs", "mins", "goals", "assists", "ga90"]].to_string(index=False))

g.to_csv("career_agg.csv", index=False)
