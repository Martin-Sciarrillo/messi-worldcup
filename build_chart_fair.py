"""Messi G+A/90: comparación JUSTA carrera-vs-carrera en Mundiales (1966-2022).
Cada jugador se agrega por su carrera mundialista completa (suma de todas sus ediciones),
igual que Messi. Distribución normal (mu/sd) + cap q0.995, filtro FW y min carrera >=90.
G+A uniforme = goles + asistencias(NaN->0) para todos.
"""
import os, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.stats import norm

OUT = os.path.dirname(os.path.abspath(__file__))
CY = "#36d7b7"     # Messi
OR = "#ffb142"     # rivales de peso

# ---- Datos: agregar por carrera ----
df = pd.read_csv(os.path.join(OUT, "worldcup_all.csv"))
for c in ["minutes", "goals", "assists"]:
    df[c] = pd.to_numeric(df[c].astype(str).str.replace(",", "", regex=False), errors="coerce")
df["ga_eff"] = df["goals"].fillna(0) + df["assists"].fillna(0)
df["is_fw"] = df["pos"].str.contains("FW", na=False)

g = (df.groupby("player")
       .agg(mins=("minutes", "sum"), goals=("goals", "sum"), assists=("assists", "sum"),
            ga=("ga_eff", "sum"), wcs=("wc_year", "nunique"), fw=("is_fw", "max"),
            squad=("squad", "last")).reset_index())
g = g[(g["fw"]) & (g["mins"] >= 90)].copy()
g["ga90"] = g["ga"] / g["mins"] * 90
cap = g["ga90"].quantile(0.995)
g = g[g["ga90"] <= cap]

vals = g["ga90"].values
mu, sd = vals.mean(), vals.std()
me = g[g["player"].str.contains("Messi", case=False, na=False)].iloc[0]
messi_val = me["ga90"]
z = (messi_val - mu) / sd
p = norm.cdf(z) * 100
rank = int((g["ga90"] > messi_val).sum())

# Rivales de PESO por encima de Messi: carrera sustancial (>=700 min ~ 8 partidos)
heavy = g[(g["ga90"] > messi_val) & (g["mins"] >= 700)].sort_values("ga90", ascending=False)
heavy = heavy.head(6)
print(f"Messi carrera {messi_val:.3f} -> {z:.1f}sigma, percentil {p:.2f}%, top {rank+1}/{len(g)}")
print("Rivales de peso:", list(zip(heavy["player"], heavy["ga90"].round(2))))

# ---- Geometría ----
xmax = max(vals.max(), messi_val) * 1.1
x = np.linspace(0, xmax, 1000)
bw = (vals.max() - vals.min()) / 40
y = norm.pdf(x, mu, sd) * len(vals) * bw
ymax = y.max()

np.random.seed(7)
y_pts = norm.pdf(vals, mu, sd) * len(vals) * bw * np.random.uniform(0, 1, len(vals))
order = np.random.permutation(len(vals))

hx = heavy["ga90"].values
hy = norm.pdf(hx, mu, sd) * len(vals) * bw * 0.12
hnames = [n.split()[-1] for n in heavy["player"]]
y_star = norm.pdf(messi_val, mu, sd) * len(vals) * bw * 0.06

plt.style.use("dark_background")
fig, ax = plt.subplots(figsize=(10, 7))
fig.patch.set_facecolor("#0d0d0d")
ax.set_facecolor("#0d0d0d")
ax.set_title("Messi en Mundiales: comparación JUSTA carrera vs carrera (1966–2022)",
             color="white", fontsize=13, fontweight="bold")
ax.set_xlabel("Goles + Asistencias por 90 minutos — carrera mundialista acumulada", color="#aaaaaa")
ax.set_ylabel("Cantidad de jugadores", color="#aaaaaa")
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#333333"); ax.spines["left"].set_color("#333333")
ax.tick_params(colors="#777777")
ax.set_xlim(0, xmax); ax.set_ylim(0, ymax * 1.05)

curve_line, = ax.plot([], [], color="#cccccc", lw=1.5)
scatter = ax.scatter([], [], color="#888888", alpha=0.35, s=10, linewidths=0)
mean_line = ax.axvline(mu, color="white", lw=1, alpha=0.0, ls="--")
mean_txt = ax.text(mu + 0.01, ymax * 0.9, f"media\n{mu:.2f}/90", color="#aaaaaa", fontsize=9, alpha=0.0)
heavy_scatter = ax.scatter([], [], color=OR, s=55, zorder=5, edgecolors="#1a1a1a", linewidths=0.5)
heavy_box = ax.text(0.03, 0.62, "", transform=ax.transAxes, color=OR, fontsize=9,
                    ha="left", va="top", alpha=0.0,
                    bbox=dict(boxstyle="round,pad=0.4", fc="#1a1a1a", ec=OR, alpha=0.0))
star = ax.scatter([], [], color=CY, s=300, zorder=6, marker="*", edgecolors="white", linewidths=0.7)
star_txt = ax.annotate("", xy=(messi_val, y_star),
                       xytext=(messi_val + sd * 0.7, ymax * 0.45),
                       color=CY, fontweight="bold", fontsize=11, ha="left",
                       arrowprops=dict(arrowstyle="->", color=CY, lw=1.3,
                                       connectionstyle="arc3,rad=0.2"), alpha=0.0)
z_box = ax.text(0.97, 0.92, "", transform=ax.transAxes, color=CY, fontweight="bold",
                ha="right", va="top",
                bbox=dict(boxstyle="round,pad=0.4", fc="#1a1a1a", ec=CY, alpha=0.0))
fig.text(0.5, 0.01,
         "Fuente: FBref · Mundiales FIFA 1966–2022 · Mín. 90 min carrera · Solo atacantes (FW) · "
         "Cada jugador agregado por su carrera mundialista (igual que Messi)",
         ha="center", color="#555555", fontsize=7.5)

F_CURVE, F_PTS, F_MEAN, F_HEAVY, F_STAR = 25, 70, 15, 30, 35
total = F_CURVE + F_PTS + F_MEAN + F_HEAVY + F_STAR
HOLD = 35

heavy_lines = "Carreras de peso por encima de Messi\n(≥ 700 min):\n" + \
              "\n".join(f"  {n}  {v:.2f}" for n, v in zip(heavy["player"], heavy["ga90"]))


def update(frame):
    f = frame
    if f < F_CURVE:
        k = int(len(x) * (f + 1) / F_CURVE)
        curve_line.set_data(x[:k], y[:k]); return
    curve_line.set_data(x, y); f -= F_CURVE

    if f < F_PTS:
        k = int(len(order) * (f + 1) / F_PTS)
        idx = order[:k]
        scatter.set_offsets(np.c_[vals[idx], y_pts[idx]]); return
    scatter.set_offsets(np.c_[vals, y_pts]); f -= F_PTS

    if f < F_MEAN:
        a = (f + 1) / F_MEAN
        mean_line.set_alpha(0.5 * a); mean_txt.set_alpha(a); return
    mean_line.set_alpha(0.5); mean_txt.set_alpha(1.0); f -= F_MEAN

    if f < F_HEAVY:
        k = int(len(hx) * (f + 1) / F_HEAVY)
        k = max(k, 1)
        heavy_scatter.set_offsets(np.c_[hx[:k], hy[:k]])
        a = (f + 1) / F_HEAVY
        heavy_box.set_text(heavy_lines); heavy_box.set_alpha(a)
        heavy_box.get_bbox_patch().set_alpha(0.85 * a)
        return
    heavy_scatter.set_offsets(np.c_[hx, hy])
    heavy_box.set_text(heavy_lines); heavy_box.set_alpha(1.0)
    heavy_box.get_bbox_patch().set_alpha(0.85)
    f -= F_HEAVY

    a = min(1.0, (f + 1) / F_STAR)
    star.set_offsets(np.c_[[messi_val], [y_star]]); star.set_alpha(a)
    star_txt.set_text(f"MESSI\ncarrera: {messi_val:.2f} G+A/90\n13G 6A · 5 Mundiales")
    star_txt.set_alpha(a)
    z_box.set_text(f"{z:.1f}σ sobre la media\npercentil {p:.1f}%  ·  top {rank+1}/{len(g)}")
    z_box.set_alpha(a); z_box.get_bbox_patch().set_alpha(0.85 * a)


frames = list(range(total)) + [total - 1] * HOLD
anim = FuncAnimation(fig, update, frames=frames, interval=60, blit=False)

mp4 = os.path.join(OUT, "messi_worldcup_fair.mp4")
try:
    from matplotlib.animation import FFMpegWriter
    anim.save(mp4, writer=FFMpegWriter(fps=18, bitrate=2400), dpi=120)
    print("Guardado:", mp4)
except Exception as e:
    from matplotlib.animation import PillowWriter
    gif = os.path.join(OUT, "messi_worldcup_fair.gif")
    anim.save(gif, writer=PillowWriter(fps=16), dpi=100)
    print("ffmpeg falló, GIF:", gif, e)

update(total - 1)
png = os.path.join(OUT, "messi_worldcup_fair.png")
fig.savefig(png, dpi=150, bbox_inches="tight", facecolor="#0d0d0d")
print("Guardado:", png)
