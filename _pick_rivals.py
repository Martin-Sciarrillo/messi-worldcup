import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd

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

pd.set_option("display.width", 170)
d = g[g["mins"] >= 1500].sort_values("mins", ascending=False)
print("=== DURABLES >=1500 min ===")
print(d[["player", "mins", "goals", "assists", "ga", "ga90", "wcs"]].to_string(index=False))
print("\n=== Candidatos nombrados ===")
names = ["Müller", "Muller", "Batistuta", "Rummenigge", "Lineker", "Klinsmann",
         "Vavá", "Pelé", "Pele", "Rivelino", "Maradona", "Zidane", "Iniesta",
         "Xavi", "Overath", "Cruyff", "Romário", "Romario", "Bebeto", "Ronaldinho",
         "Kaká", "Kaka", "Suárez", "Henry", "Hurst", "Eusébio", "Cubillas", "Müller"]
seen = set()
for n in names:
    r = g[g["player"].str.contains(n, na=False)]
    for _, x in r.iterrows():
        if x["player"] in seen:
            continue
        seen.add(x["player"])
        print(f"{x['player']:<26} {int(x['mins']):>5} min  {int(x['goals'])}G {int(x['assists'])}A  ga90={x['ga90']:.3f}  WCs={x['wcs']}")
