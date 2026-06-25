"""Versión PÓSTER con retratos de Wikipedia.
Plano VOLUMEN x EFICIENCIA con foto circular de cada jugador etiquetado,
anillo de color por arquetipo, línea guía al punto real y caption.
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
import matplotlib.patheffects as pe
import matplotlib.cm as cm
from matplotlib.colors import Normalize, LinearSegmentedColormap
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image, ImageDraw, ImageFilter

matplotlib.rcParams["font.family"] = ["Segoe UI", "DejaVu Sans"]

OUT = os.path.dirname(os.path.abspath(__file__))
PH = os.path.join(OUT, "photos")
FL = os.path.join(OUT, "flags")
CY = "#36d7b7"
BG = "#0a0e16"
ASSIST_CMAP = LinearSegmentedColormap.from_list(
    "assist", ["#46566b", "#2aa9a0", "#36d7b7", "#a8f7ea"])
BLOOM_CMAP = LinearSegmentedColormap.from_list("bloom", [BG, BG, "#0e2a28", "#12463f"])


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def make_flag(iso, d, ring_w=4):
    fim = Image.open(os.path.join(FL, iso + ".png")).convert("RGBA")
    w, h = fim.size
    s = min(w, h)
    fim = fim.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize((d, d), Image.LANCZOS)
    out = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    disc = Image.new("L", (d, d), 0)
    ImageDraw.Draw(disc).ellipse((0, 0, d - 1, d - 1), fill=255)
    out.paste(Image.new("RGBA", (d, d), (255, 255, 255, 255)), (0, 0), disc)
    inner = Image.new("L", (d, d), 0)
    ImageDraw.Draw(inner).ellipse((ring_w, ring_w, d - 1 - ring_w, d - 1 - ring_w), fill=255)
    out.paste(fim, (0, 0), inner)
    return out


# Recorte focal por jugador: (cx, cy, escala) — centro como fracción de W,H; lado = escala*min(W,H)
CROP = {
    "messi":      (0.50, 0.42, 0.96),
    "cristiano":  (0.50, 0.42, 0.97),
    "mbappe":     (0.50, 0.33, 0.86),
    "pele":       (0.46, 0.30, 0.74),
    "maradona":   (0.41, 0.20, 0.50),
    "klose":      (0.50, 0.38, 0.94),
    "ronaldo_br": (0.50, 0.40, 0.94),
    "gmuller":    (0.50, 0.40, 0.97),
    "fontaine":   (0.52, 0.40, 0.80),
    "kocsis":     (0.50, 0.34, 0.90),
}


def make_avatar(key, ring_hex, size=256, ring_w=11, glow=False, iso=None):
    ss = 4  # supersample para un círculo y un aro nítidos
    S, rw = size * ss, ring_w * ss
    im = Image.open(os.path.join(PH, key + ".jpg")).convert("RGBA")
    w, h = im.size
    cx, cy, sc = CROP.get(key, (0.50, 0.40, 0.95))
    s = int(min(w, h) * sc)
    left = max(0, min(int(w * cx - s / 2), w - s))
    top = max(0, min(int(h * cy - s / 2), h - s))
    im = im.crop((left, top, left + s, top + s)).resize((S, S), Image.LANCZOS)
    ring = hex2rgb(ring_hex)
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    # disco exterior con el color del aro: define el círculo limpio
    disc = Image.new("L", (S, S), 0)
    ImageDraw.Draw(disc).ellipse((0, 0, S - 1, S - 1), fill=255)
    out.paste(Image.new("RGBA", (S, S), ring + (255,)), (0, 0), disc)
    # foto enmascarada a un círculo interior -> el aro queda como banda y nunca asoma el borde
    inner = Image.new("L", (S, S), 0)
    ImageDraw.Draw(inner).ellipse((rw, rw, S - 1 - rw, S - 1 - rw), fill=255)
    out.paste(im, (0, 0), inner)
    if iso:
        fd = int(S * 0.30)
        fl = make_flag(iso, fd, ring_w=3 * ss)
        fx = int(S * 0.80 - fd / 2)
        fy = int(S * 0.82 - fd / 2)
        out.alpha_composite(fl, (fx, fy))
    out = out.resize((size, size), Image.LANCZOS)  # downsample -> antialias limpio
    if glow:
        pad = 70
        canvas = Image.new("RGBA", (size + pad * 2, size + pad * 2), (0, 0, 0, 0))
        gl = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        ImageDraw.Draw(gl).ellipse((pad - 10, pad - 10, pad + size + 10, pad + size + 10),
                                   fill=ring + (200,))
        gl = gl.filter(ImageFilter.GaussianBlur(28))
        canvas = Image.alpha_composite(canvas, gl)
        canvas.paste(out, (pad, pad), out)
        out = canvas
    return np.asarray(out) / 255.0


# ---------- Datos ----------
df = pd.read_csv(os.path.join(OUT, "worldcup_all.csv"))
for c in ["minutes", "goals", "assists"]:
    df[c] = pd.to_numeric(df[c].astype(str).str.replace(",", "", regex=False), errors="coerce")
df["ga_eff"] = df["goals"].fillna(0) + df["assists"].fillna(0)
df["is_fw"] = df["pos"].str.contains("FW", na=False)
g = (df.groupby("player")
       .agg(mins=("minutes", "sum"), goals=("goals", "sum"), assists=("assists", "sum"),
            ga=("ga_eff", "sum"), wcs=("wc_year", "nunique"), fw=("is_fw", "max")).reset_index())
g = g[(g["fw"]) & (g["mins"] >= 90)].copy()
g["ga90"] = g["ga"] / g["mins"] * 90

# ---- Mundial 2026 (en curso) — datos parciales al 24-jun-2026 (fase de grupos) ----
WC2026 = {  # jugador: (+minutos, +goles, +asistencias) · fuente: prensa (no FBref aún)
    "Messi": (170, 5, 0),      # Argelia 80'/3G · Austria 90'/2G -> récord histórico
    "Cristiano": (180, 2, 0),  # RD Congo 90'/0 · Uzbekistán 90'/2G
    "Mbapp": (181, 4, 0),      # Senegal 90'/2G · Irak 91'/2G
}
for _nm, (_dm, _dg, _da) in WC2026.items():
    _m = g["player"].str.contains(_nm, na=False)
    g.loc[_m, "mins"] += _dm
    g.loc[_m, "goals"] += _dg
    g.loc[_m, "assists"] += _da
    g.loc[_m, "ga"] += _dg + _da
    g.loc[_m, "wcs"] += 1
g["ga90"] = g["ga"] / g["mins"] * 90  # recomputar tras sumar 2026

me = g[g["player"].str.contains("Messi", case=False, na=False)].iloc[0]
durable = g[g["mins"] >= 1500]
mx, my = me["mins"], me["ga90"]
xmax = g["mins"].max() * 1.16
ymax = min(g["ga90"].max(), 2.6) * 1.05


def find(n):
    r = g[g["player"].str.contains(n, na=False)]
    return r.iloc[0] if len(r) else None


klose, r9, mara = find("Klose"), g[g["player"] == "Ronaldo"].iloc[0], find("Maradona")
gmuller, bati, perisic = find("Gerd Müller"), find("Batistuta"), find("Perišić")
hunt = g.sort_values("ga90", ascending=False).iloc[0]
mbappe = find("Mbapp")
cristiano = find("Cristiano")
# Leyendas fuera/parciales del dataset 1966–2022 (ratio solo-goles; asist. pre-Opta no registradas)
fontaine = {"mins": 540, "ga90": 13 / 540 * 90}    # 1958 FRA — 13 G, récord de un torneo
kocsis   = {"mins": 450, "ga90": 11 / 450 * 90}    # 1954 HUN — 11 G
pele     = {"mins": 1215, "ga90": 12 / 1215 * 90}  # 1958–70 BRA — 12 G, 3 títulos


def pt(name):
    r = g[g["player"] == name].iloc[0]
    return (r["mins"], r["ga90"])


eusebio   = pt("Eusébio")
lineker   = pt("Gary Lineker")
klinsmann = pt("Jürgen Klinsmann")
tmuller   = pt("Thomas Müller")
kane      = pt("Harry Kane")
lato      = pt("Grzegorz Lato")

# ---------- Figura ----------
plt.style.use("dark_background")
fig, ax = plt.subplots(figsize=(12.6, 7.6))
fig.patch.set_facecolor(BG); ax.set_facecolor(BG)

gy, gx = np.mgrid[0:ymax:320j, 0:xmax:320j]
bloom = np.exp(-(((gx - mx) / (xmax * 0.30)) ** 2 + ((gy - my) / (ymax * 0.34)) ** 2))
ax.imshow(bloom, extent=[0, xmax, 0, ymax], origin="lower", aspect="auto",
          cmap=BLOOM_CMAP, zorder=0, interpolation="bilinear")

ax.set_axisbelow(True)
ax.grid(True, which="major", color="#1c2433", lw=0.8, alpha=0.7, zorder=1)
ax.set_xticks(np.arange(0, xmax, 500))
ax.set_yticks(np.arange(0, ymax, 0.5))

fig.text(0.5, 0.955, "Messi, fuera de la curva", color="white",
         fontsize=21, fontweight="bold", ha="center")
fig.text(0.5, 0.915, "Durabilidad × eficiencia · Mundiales 1966–2026* (+ leyendas: Kocsis, Fontaine, Pelé) · solo atacantes",
         color=CY, fontsize=11, ha="center")
ax.set_xlabel("VOLUMEN  →  minutos de carrera mundialista", color="#8a93a6", fontsize=10.5, labelpad=8)
ax.set_ylabel("EFICIENCIA  →  G+A por 90 min", color="#8a93a6", fontsize=10.5, labelpad=8)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
for s in ["bottom", "left"]:
    ax.spines[s].set_color("#2a3242")
ax.tick_params(colors="#6b7488")
ax.set_xlim(0, xmax); ax.set_ylim(0, ymax)

sm = cm.ScalarMappable(norm=Normalize(0, 6), cmap=ASSIST_CMAP); sm.set_array([])
cb = fig.colorbar(sm, ax=ax, fraction=0.030, pad=0.012)
cb.set_label("asistencias (creación)", color="#8a93a6", fontsize=9)
cb.ax.yaxis.set_tick_params(color="#6b7488")
cb.outline.set_edgecolor("#2a3242")
plt.setp(plt.getp(cb.ax.axes, "yticklabels"), color="#6b7488")

# Nube de fondo
others = g[~g["player"].str.contains("Messi", case=False, na=False)]
ax.scatter(others["mins"], others["ga90"], s=12, c="#5b6678", alpha=0.30, linewidths=0, zorder=2)
# Club duradero coloreado por asistencias
ax.scatter(durable["mins"], durable["ga90"], s=70 + durable["assists"].fillna(0) * 30,
           c=durable["assists"].fillna(0), cmap=ASSIST_CMAP, norm=Normalize(0, 6),
           edgecolors=BG, linewidths=0.8, alpha=0.95, zorder=3)
# Leyendas históricas (fuera/parciales del dataset) — diamantes en oro
GOLD = "#c9a23a"
for L in (fontaine, kocsis, pele):
    ax.scatter([L["mins"]], [L["ga90"]], s=66, marker="D", c="#5b6678",
               edgecolors=GOLD, linewidths=1.3, zorder=3)

# Zona vacía
ax.add_patch(plt.Rectangle((mx, my), xmax - mx, ymax - my, fc=CY, ec=CY, lw=1.0,
                           ls=(0, (4, 3)), alpha=0.12, zorder=1))
zx = mx + (xmax - mx) * 0.55
ax.text(zx, my + (ymax - my) * 0.26, "TIERRA DE NADIE",
        color="#bff7ee", fontsize=9.0, ha="center", va="center", alpha=0.92,
        fontstyle="italic", fontweight="bold", zorder=2)
ax.text(zx, my + (ymax - my) * 0.17, "— salvo Messi —",
        color="#7fd9cd", fontsize=7.2, ha="center", va="center", alpha=0.85,
        fontstyle="italic", zorder=2)

# Estrella Messi
for s_, a_ in [(2600, 0.05), (1600, 0.07), (950, 0.11), (560, 0.18)]:
    ax.scatter([mx], [my], s=s_, marker="*", c=CY, alpha=a_, edgecolors="none", zorder=5)
ax.scatter([mx], [my], s=460, marker="*", c="#eafff9", edgecolors=CY, linewidths=1.6, zorder=6)

GRAY = "#aeb8c8"
CEL = "#75aadb"
ISO = {"messi": "ar", "cristiano": "pt", "mbappe": "fr", "pele": "br",
       "maradona": "ar", "klose": "de", "ronaldo_br": "br", "gmuller": "de",
       "fontaine": "fr", "kocsis": "hu"}
# (key, dot_row, badge_xy, ring, zoom, caption, cap_dy, glow)
PHOTO_CAST = [
    ("kocsis", kocsis, (250, 2.06), GOLD, 0.26,
     "Sándor Kocsis · 1 Mundial\n11 Goles en 1954 · ratio 2.20\nleyenda húngara", -0.30, False),
    ("fontaine", fontaine, (640, 2.42), GOLD, 0.26,
     "Just Fontaine · 1 Mundial\n13 Goles en 1958 · ratio 2.17\nrécord de un torneo", -0.30, False),
    ("gmuller", gmuller, (1120, 2.32), GRAY, 0.26,
     "Gerd Müller · 2 Mundiales\n14 Goles · 0 Asist.\ngoleador histórico", -0.31, False),
    ("mbappe", mbappe, (835, 1.55), "#6f8fd6", 0.26,
     "Mbappé · 3 Mundiales\n16 Goles · 2 Asist.\nratio élite, falta volumen", -0.31, False),
    ("ronaldo_br", r9, (1560, 1.82), GRAY, 0.26,
     "Ronaldo · 3 Mundiales\n15 Goles · 3 Asist.\nR9, el Fenómeno", -0.31, False),
    ("pele", pele, (1330, 1.22), GOLD, 0.26,
     "Pelé · 4 Mundiales\n12 Goles · 3 títulos\nrey, más allá del ratio", -0.31, False),
    ("cristiano", cristiano, (1880, 1.28), "#cf6679", 0.26,
     "Cristiano · 6 Mundiales\n10 Goles · 1 Asist.\nvolumen sí, ratio no", -0.31, False),
    ("klose", klose, (2150, 1.58), GRAY, 0.26,
     "Klose · 4 Mundiales\n16 Goles · 0 Asist.\nrécord superado por Messi", -0.30, False),
    ("maradona", mara, (2280, 0.46), CEL, 0.26,
     "Maradona · 4 Mundiales\n8 Goles · 0 Asist.\ncampeón 1986", -0.31, False),
    ("messi", me, (2480, 2.28), "#a8f7ea", 0.40,
     "MESSI · 6 Mundiales\n18 Goles (récord) · 6 Asist.\n2484' — único +2000", -0.44, True),
]

# Ajuste horizontal de leyendas para evitar solapes con objetos vecinos
CAP_DX = {"klose": 70, "messi": -70, "pele": -80}

for key, row, bxy, ring, zoom, cap, cap_dy, glow in PHOTO_CAST:
    dot = (row["mins"], row["ga90"])
    img = make_avatar(key, ring, glow=glow, iso=ISO.get(key))
    ab = AnnotationBbox(
        OffsetImage(img, zoom=zoom), dot, xybox=bxy, xycoords="data", boxcoords="data",
        frameon=False, pad=0, zorder=11,
        arrowprops=dict(arrowstyle="-", color=ring, lw=1.1, alpha=0.55,
                        connectionstyle=f"arc3,rad={-0.22 if key == 'messi' else 0.10}",
                        shrinkA=2, shrinkB=6))
    ax.add_artist(ab)
    col = "#eafff9" if key == "messi" else "#d4dae6"
    fs = 9.0 if key == "messi" else 8.4
    fw = "bold" if key == "messi" else "normal"
    ax.text(bxy[0] + CAP_DX.get(key, 0), bxy[1] + cap_dy, cap, ha="center", va="top", color=col, fontsize=fs,
            fontweight=fw, zorder=12, linespacing=1.25,
            path_effects=[pe.withStroke(linewidth=3.4, foreground=BG)])

# Etiquetas de nombre (goleadores notables sin foto) — punto + apellido
LBL = "#c2cad8"
LABELS = [
    ("Huntelaar", hunt["mins"], hunt["ga90"], 205, 2.49, "left"),
    ("Eusébio",   eusebio[0],   eusebio[1],   430, 1.40, "right"),
    ("Lineker",   lineker[0],   lineker[1],   1075, 0.60, "right"),
    ("Klinsmann", klinsmann[0], klinsmann[1], 1505, 0.56, "center"),
    ("T. Müller", tmuller[0],   tmuller[1],   1635, 0.62, "left"),
    ("Kane",      kane[0],      kane[1],      1020, 1.05, "left"),
    ("Batistuta", bati["mins"], bati["ga90"], 980, 0.80, "center"),
    ("Lato",      lato[0],      lato[1],      1895, 0.42, "left"),
]
for disp, xm, ym2, tx, ty, ha in LABELS:
    ax.plot([xm, tx], [ym2, ty], color=LBL, lw=0.7, alpha=0.40, zorder=7)
    ax.scatter([xm], [ym2], s=46, c="#9aa6ba", edgecolors=BG, linewidths=0.8, zorder=8)
    ax.text(tx, ty, disp, ha=ha, va="center", color=LBL, fontsize=7.0, zorder=12,
            path_effects=[pe.withStroke(linewidth=2.4, foreground=BG)])
ax.text(980, 0.165, "+ goleadores: Baggio · Rummenigge · Vieri · Villa · Perišić",
        ha="left", va="center", color="#8a93a6", fontsize=7.2, fontstyle="italic",
        zorder=12, path_effects=[pe.withStroke(linewidth=2.0, foreground=BG)])

# Info / tesis — panel dentro del plano (abajo-izquierda, sobre la nube tenue)
info = ("MESSI — el único que combina las tres:\n"
        r"$\bf{1}$  Durabilidad #1 (2484', único +2000)" + "\n"
        r"$\bf{2}$  Producción #1 (24 G+A totales)" + "\n"
        r"$\bf{3}$  Creación #1 (18 Goles + 6 Asist.)")
ax.text(110, 0.66, info, transform=ax.transData, ha="left", va="top",
        color="#dbe2ee", fontsize=9, linespacing=1.6, zorder=13,
        bbox=dict(boxstyle="round,pad=0.7", fc="#0d1320", ec=CY, lw=1.2, alpha=0.92))
fig.text(0.5, 0.886, "Fuente: FBref (1966–2022) · *Mundial 2026 en curso: datos parciales · fotos: Wikimedia Commons",
         ha="center", color="#5a6478", fontsize=7.4)
fig.text(0.988, 0.020, "aka.ms/Tincho", ha="right", va="bottom", color=CY,
         fontsize=12.5, fontstyle="italic", fontweight="bold", alpha=0.9)

png = os.path.join(OUT, "messi_profile_portraits.png")
fig.savefig(png, dpi=150, bbox_inches="tight", facecolor=BG)
print("Guardado:", png)
if os.environ.get("FAST") == "1":
    print("FAST: salteo poster 300dpi")
else:
    poster = os.path.join(OUT, "messi_profile_portraits_poster.png")
    fig.savefig(poster, dpi=300, bbox_inches="tight", facecolor=BG)
    print("Guardado:", poster)
