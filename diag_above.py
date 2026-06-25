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

messi = g[g["player"].str.contains("Messi", case=False, na=False)].iloc[0]
mv, mmin = messi["ga90"], messi["mins"]
above = g[g["ga90"] > mv].copy()

print(f"Messi: ga90={mv:.3f}, {int(messi['mins'])} min, {int(messi['wcs'])} Mundiales")
print(f"Total por encima de Messi: {len(above)}")
print()
print("Desglose de los que 'le ganan' por tamaño de muestra:")
print(f"  jugaron 1 solo Mundial:        {(above['wcs']==1).sum()}")
print(f"  jugaron <= 2 Mundiales:        {(above['wcs']<=2).sum()}")
print(f"  con MENOS minutos que Messi:   {(above['mins']<mmin).sum()}  (de {len(above)})")
print(f"  con >= los minutos de Messi:   {(above['mins']>=mmin).sum()}")
print()
print(f"Por encima de Messi Y con carrera comparable (>= {int(mmin)} min como él):")
comp = above[above["mins"] >= mmin].sort_values("ga90", ascending=False)
comp["ga90"] = comp["ga90"].round(3)
print(comp[["player", "wcs", "mins", "goals", "assists", "ga90"]].to_string(index=False))
print()
# minutos mediana de los 111
print(f"Minutos mediana de los {len(above)} por encima: {int(above['mins'].median())}  vs Messi {int(mmin)}")
print(f"Goles mediana de los que le ganan: {above['goals'].median():.0f}  vs Messi {int(messi['goals'])}")
