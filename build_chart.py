"""Messi como anomalía histórica en Mundiales — versión original + animación.
Metodología tal cual la spec: filtro FW, min>=90, distribución normal (mu/sd),
cap outliers q0.995, Messi = G+A/90 de carrera mundialista acumulada.
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
CY = "#36d7b7"  # celeste/turquesa Messi

# 1. Cargar datos
df = pd.read_csv(os.path.join(OUT, "worldcup_all.csv"))
df.columns = df.columns.str.strip()
for col in ["minutes", "ga_per90", "goals", "assists", "ga"]:
    if col in df.columns:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", "", regex=False), errors="coerce"
        )

# 2. Filtros (idénticos a la spec)
df = df[df["pos"].str.contains("FW", na=False)]
df = df[df["minutes"] >= 90]
if df["ga_per90"].isna().sum() > len(df) * 0.3:
    df["ga_per90"] = ((df["goals"].fillna(0) + df["assists"].fillna(0)) / df["minutes"]) * 90
df = df.dropna(subset=["ga_per90"])
df = df[df["ga_per90"] <= df["ga_per90"].quantile(0.995)]

# 3. Stats
ga = df["ga_per90"].values
mu, sd = ga.mean(), ga.std()
messi_df = df[df["player"].str.contains("Messi", case=False, na=False)].copy()
messi_df = messi_df.sort_values("wc_year")
messi_val = (messi_df["ga"].sum() / messi_df["minutes"].sum()) * 90
z = (messi_val - mu) / sd
p = norm.cdf(z) * 100

print(f"N={len(df)}, mu={mu:.3f}, sd={sd:.3f}")
print(f"Messi carrera: {messi_val:.3f} G+A/90 -> {z:.1f}σ (percentil {p:.4f}%)")
print("Messi por Mundial:")
print(messi_df[["wc_year", "squad", "minutes", "goals", "assists", "ga_per90"]].to_string(index=False))

# --- Geometría del gráfico ---
xmax = max(ga.max(), messi_val) * 1.1
x = np.linspace(0, xmax, 1000)
bw = (ga.max() - ga.min()) / 40
y = norm.pdf(x, mu, sd) * len(ga) * bw
ymax = y.max()

np.random.seed(42)
y_pts = norm.pdf(ga, mu, sd) * len(ga) * bw * np.random.uniform(0, 1, len(ga))
order = np.random.permutation(len(ga))  # orden de aparición de los puntos grises

messi_x = messi_df["ga_per90"].values
messi_years = messi_df["wc_year"].values.astype(int)
messi_y = norm.pdf(messi_x, mu, sd) * len(ga) * bw * 0.1
y_carrera = norm.pdf(messi_val, mu, sd) * len(ga) * bw * 0.05


def setup_axes(ax):
    ax.set_facecolor("#0d0d0d")
    ax.set_title("Messi no es histórico. Es una anomalía en 60 años de historia mundialista.",
                 color="white", fontsize=13, fontweight="bold")
    ax.set_xlabel("Goles + Asistencias por 90 minutos", color="#aaaaaa")
    ax.set_ylabel("Cantidad de jugadores", color="#aaaaaa")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color("#333333")
    ax.spines["left"].set_color("#333333")
    ax.tick_params(colors="#777777")
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax * 1.05)


# ============ ANIMACIÓN ============
plt.style.use("dark_background")
fig, ax = plt.subplots(figsize=(10, 7))
fig.patch.set_facecolor("#0d0d0d")
setup_axes(ax)

curve_line, = ax.plot([], [], color="#cccccc", lw=1.5)
scatter = ax.scatter([], [], color="#888888", alpha=0.35, s=10, linewidths=0)
mean_line = ax.axvline(mu, color="white", lw=1, alpha=0.0, ls="--")
mean_txt = ax.text(mu + 0.01, ymax * 0.88, f"media\n{mu:.2f}/90", color="#aaaaaa",
                   fontsize=9, alpha=0.0)
messi_scatter = ax.scatter([], [], color=CY, s=70, zorder=5)
messi_labels = [ax.text(mx, my, str(yr), color=CY, fontsize=8, ha="center",
                        va="bottom", fontweight="bold", alpha=0.0)
                for mx, my, yr in zip(messi_x, messi_y, messi_years)]
star = ax.scatter([], [], color=CY, s=260, zorder=6, marker="*",
                  edgecolors="white", linewidths=0.6)
star_txt = ax.annotate("", xy=(messi_val, y_carrera),
                       xytext=(messi_val - sd * 0.5, ymax * 0.35),
                       color=CY, fontweight="bold", fontsize=11, ha="right",
                       arrowprops=dict(arrowstyle="->", color=CY, lw=1.2,
                                       connectionstyle="arc3,rad=-0.2"), alpha=0.0)
z_box = ax.text(0.97, 0.92, "", transform=ax.transAxes, color=CY, fontweight="bold",
                ha="right", va="top",
                bbox=dict(boxstyle="round,pad=0.4", fc="#1a1a1a", ec=CY, alpha=0.0))
fig.text(0.5, 0.01,
         "Fuente: FBref · Mundiales FIFA 1966–2022 · Mín. 90 min · Solo atacantes (FW) · G+A/90 carrera acumulada",
         ha="center", color="#555555", fontsize=8)

# Fases (en frames)
F_CURVE = 25
F_PTS = 70
F_MEAN = 15
F_MESSI_EACH = 12
F_STAR = 30
n_messi = len(messi_x)
F_MESSI = F_MESSI_EACH * n_messi
total = F_CURVE + F_PTS + F_MEAN + F_MESSI + F_STAR
HOLD = 30  # frames finales quietos


def update(frame):
    f = frame
    # Fase 1: curva
    if f < F_CURVE:
        k = int(len(x) * (f + 1) / F_CURVE)
        curve_line.set_data(x[:k], y[:k])
        return
    curve_line.set_data(x, y)
    f -= F_CURVE

    # Fase 2: puntos grises
    if f < F_PTS:
        k = int(len(order) * (f + 1) / F_PTS)
        idx = order[:k]
        scatter.set_offsets(np.c_[ga[idx], y_pts[idx]])
        return
    scatter.set_offsets(np.c_[ga, y_pts])
    f -= F_PTS

    # Fase 3: media
    if f < F_MEAN:
        a = (f + 1) / F_MEAN
        mean_line.set_alpha(0.5 * a)
        mean_txt.set_alpha(a)
        return
    mean_line.set_alpha(0.5)
    mean_txt.set_alpha(1.0)
    f -= F_MEAN

    # Fase 4: puntos Messi por Mundial (cronológico)
    if f < F_MESSI:
        shown = f // F_MESSI_EACH + 1
        shown = min(shown, n_messi)
        messi_scatter.set_offsets(np.c_[messi_x[:shown], messi_y[:shown]])
        for i in range(shown):
            messi_labels[i].set_alpha(1.0)
            messi_labels[i].set_position((messi_x[i], messi_y[i] + ymax * 0.02))
        return
    messi_scatter.set_offsets(np.c_[messi_x, messi_y])
    for lb in messi_labels:
        lb.set_alpha(1.0)
    f -= F_MESSI

    # Fase 5: estrella carrera + z-score
    a = min(1.0, (f + 1) / F_STAR)
    star.set_offsets(np.c_[[messi_val], [y_carrera]])
    star.set_alpha(a)
    star_txt.set_text(f"MESSI\n(carrera: {messi_val:.2f} G+A/90)")
    star_txt.set_alpha(a)
    z_box.set_text(f"{z:.1f}σ sobre la media\n(percentil {p:.4f}%)")
    z_box.set_alpha(a)
    z_box.get_bbox_patch().set_alpha(0.85 * a)


frames = list(range(total)) + [total - 1] * HOLD

anim = FuncAnimation(fig, update, frames=frames, interval=60, blit=False)

# Guardar: MP4 si hay ffmpeg, si no GIF
mp4 = os.path.join(OUT, "messi_worldcup_anomaly.mp4")
gif = os.path.join(OUT, "messi_worldcup_anomaly.gif")
saved = None
try:
    from matplotlib.animation import FFMpegWriter
    anim.save(mp4, writer=FFMpegWriter(fps=18, bitrate=2400), dpi=120)
    saved = mp4
    print("Guardado:", mp4)
except Exception as e:
    print("ffmpeg no disponible, usando GIF:", e)
    from matplotlib.animation import PillowWriter
    anim.save(gif, writer=PillowWriter(fps=16), dpi=100)
    saved = gif
    print("Guardado:", gif)

# Frame final estático (PNG)
update(total - 1)
png = os.path.join(OUT, "messi_worldcup_anomaly.png")
fig.savefig(png, dpi=150, bbox_inches="tight", facecolor="#0d0d0d")
print("Guardado:", png)
