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
gf = g[(g["fw"]) & (g["mins"] >= 90)].copy()
gf["ga90"] = gf["ga"] / gf["mins"] * 90
mv = gf[gf["player"].str.contains("Messi", case=False, na=False)]["ga90"].iloc[0]

print("=== 1) VOLUMEN (minutos de carrera mundialista) ===")
topm = g.sort_values("mins", ascending=False).head(12)
print(topm[["player", "wcs", "mins", "goals", "assists", "ga"]].to_string(index=False))

print("\n=== 2) PRODUCCION BRUTA (G+A totales en Mundiales) ===")
topga = g.sort_values("ga", ascending=False).head(12)
print(topga[["player", "wcs", "mins", "goals", "assists", "ga"]].to_string(index=False))

print("\n=== 3) PARETO: nadie con MAS min Y MAS ga90 que Messi ===")
dom = gf[(gf["mins"] > 2314) & (gf["ga90"] > mv)]
print(f"Jugadores que dominan a Messi (mas min Y mas ga90): {len(dom)}")
# frontera de Pareto (maximos no dominados)
s = gf.sort_values("mins", ascending=False)
front, best = [], -1
for _, r in s.iterrows():
    if r["ga90"] > best:
        front.append(r["player"]); best = r["ga90"]
print(f"Frontera eficiencia-volumen ({len(front)} jugadores, de mas a menos minutos):")
print("  " + " > ".join(front[:12]))

print("\n=== 4) DOBLE AMENAZA: goles Y asistencias (era con asist, >=1994) ===")
mod = g[(g["fw"]) & (g["mins"] >= 450)].copy()
mod = mod[mod["assists"].notna() & (mod["assists"] > 0)]
mod["dual"] = mod[["goals", "assists"]].min(axis=1)
print("Top por min(goles,asist) = mas balanceado como goleador+asistidor:")
print(mod.sort_values("dual", ascending=False).head(10)[["player","wcs","goals","assists","ga"]].to_string(index=False))

print("\n=== 5) RESUMEN MESSI ===")
me = g[g["player"].str.contains("Messi", case=False, na=False)].iloc[0]
print(f"  {int(me['goals'])}G + {int(me['assists'])}A = {int(me['ga'])} G+A en {int(me['mins'])} min, {int(me['wcs'])} Mundiales (2006-2022)")
print(f"  Rank minutos: #{int((g['mins']>me['mins']).sum())+1}")
print(f"  Rank G+A totales: #{int((g['ga']>me['ga']).sum())+1}")
print(f"  G+A/90: {mv:.3f} (media atacantes {gf['ga90'].mean():.3f})")
