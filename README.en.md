# ⚽🔬 messi-worldcup

**🌐 Read this in:** English · [Español](README.md)

> A playful football _data viz_ experiment. I took 60 years of World Cups (1966–2026\*),
> plotted them on a **volume × efficiency** map, and tried to answer a single question
> with data instead of terrace shouting:
>
> ### How unique is Messi's World Cup profile?

**Spoiler / the finding:** with the **partial data from the in-progress 2026 World Cup**,
Messi became the **all-time top scorer in World Cup history** (18 goals, passing Klose's
16) and sits **alone** in a region of the map I named _**No Man's Land**_: high volume
**and** high efficiency, where nobody else reaches.

<p align="center">
  <img src="messi_profile_portraits.png" width="820" alt="Messi, off the curve — volume x efficiency"><br>
  <em>🎬 Animated version: <a href="messi_profile.mp4"><code>messi_profile.mp4</code></a> &nbsp;·&nbsp;
  🌐 Live post: <a href="https://martin-sciarrillo.github.io/messi-worldcup/index.en.html">martin-sciarrillo.github.io/messi-worldcup</a> &nbsp;·&nbsp; chart labels in Spanish</em>
</p>

---

## 🧪 The hypothesis

The GOAT debate is usually loud and hard to falsify. So I turned it into something measurable:

> _If we look only at World Cups (the biggest stage) and only at forwards, is there anyone
> who is simultaneously **durable**, **productive** and **creative** at Messi's level?_

If the answer is "yes, several", Messi's profile is nothing special. If it's "no, none",
then there's an anomaly worth a chart.

## 📐 The methodology

A single cartesian map, three dimensions of information:

| Axis | Meaning | How it's computed |
|------|---------|-------------------|
| **X — VOLUME** | World Cup career minutes | sum of `minutes` across all editions |
| **Y — EFFICIENCY** | Goals + Assists per 90′ | `(G + A) / minutes × 90` |
| **Color** | Creation / assists | total assists (teal scale) |

**Experiment rules (to keep it fair):**

- Forwards **only** (`pos` contains `FW`) — we compare apples to apples.
- At least **90′** played (one full match) to enter the map.
- Messi is drawn as a **star** and the _high-volume + high-efficiency_ zone is highlighted.
- **Pre-Opta legends** (Kocsis 1954, Fontaine 1958, Pelé 1958–70) enter with an honest
  asterisk: in their era **assists weren't recorded**, so their ratio is **goals-only**
  and marked in gold, kept apart from the main cloud.

**Data source:** [FBref](https://fbref.com/) (editions 1966–2022). The **in-progress 2026
World Cup** deltas were added by hand from press reports (FBref hasn't published them yet)
and are clearly flagged as **partial**. Portraits from Wikipedia/Wikimedia. See
[`REFERENCES.md`](REFERENCES.md).

## 🏆 The findings

Messi is the **only** one who lands the _hat-trick_ of all three podiums at once:

1. **Durability #1** — 2484′, the only player with **+2000′** in World Cups.
2. **Output #1** — **24** total goal contributions (G+A).
3. **Creation #1** — **18 goals + 6 assists**: leads both finishing and passing.

Others reach one corner, but never all three:

- **Klose** (16 G) and **Cristiano** (volume, 6 World Cups) have the mileage, but a low ratio.
- **Mbappé** and **Kocsis/Fontaine** have an elite ratio, but lack volume.
- **Pelé** is the king of titles (3), but the modern dataset doesn't rate him by ratio.

The result: a statistical **anomaly** sitting alone in _No Man's Land_.

> ⚠️ **Honesty first:** the "all-time top scorer" headline uses **partial** 2026 World Cup
> data. Once FBref publishes the official figures, the numbers update. The experiment is
> about the **method**, not the hype.

## 🔁 Reproduce it

```bash
# 1) Dependencies
pip install pandas numpy matplotlib pillow scrapling

# 2) Fetch the portraits (not versioned — see .gitignore / REFERENCES.md)
python fetch_photos.py

# 3) (Optional) re-scrape FBref 1966–2022
python fetch_fbref.py
python build_data.py          # builds worldcup_all.csv

# 4) Render
python build_portraits.py     # -> 300 dpi poster
python build_profile.py       # -> animated MP4 video
```

## 🗂️ Structure

```
build_portraits.py   # final poster (volume x efficiency map with portraits)
build_profile.py     # animated version (MP4)
build_data.py        # parses the FBref dumps -> worldcup_all.csv
fetch_fbref.py       # scrapes FBref tables per edition
fetch_photos.py      # downloads portraits from Wikipedia
worldcup_all.csv     # clean dataset 1966–2022 (+ 2026 deltas in code)
flags/               # circular flags (public domain)
*.png / *.mp4        # rendered outputs
diag_*.py            # diagnostic scripts (the experiment's kitchen)
```

## 🙌 Credits

Data: **FBref / Sports Reference**. Photos: **Wikipedia / Wikimedia Commons**.
Code under the **MIT** license (see [`LICENSE`](LICENSE)). Full attribution in
[`REFERENCES.md`](REFERENCES.md).

Made with curiosity and plenty of coffee by **[Martín Sciarrillo · aka.ms/Tincho](https://aka.ms/Tincho)**.

<sub>\* 1966–2026: the dataset covers 1966–2022; earlier legends (1954/1958) and the
in-progress 2026 World Cup enter as manual/partial data, duly flagged.</sub>
