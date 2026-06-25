"""Descarga fotos de jugadores desde Wikipedia (REST summary API).
Guarda photos/<key>.jpg. Fallback a Scrapling si requests falla.
"""
import os, sys, json, time
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

OUT = os.path.dirname(os.path.abspath(__file__))
PH = os.path.join(OUT, "photos")
os.makedirs(PH, exist_ok=True)

UA = ("MessiWCChart/1.0 (educational data-viz; contact local) "
      "python-requests")
HEAD = {"User-Agent": UA}

PLAYERS = {
    "messi": ["Lionel Messi"],
    "ronaldo_br": ["Ronaldo (Brazilian footballer)", "Ronaldo Nazário", "Ronaldo"],
    "klose": ["Miroslav Klose"],
    "maradona": ["Diego Maradona"],
    "gmuller": ["Gerd Müller"],
    "batistuta": ["Gabriel Batistuta"],
    "perisic": ["Ivan Perišić"],
    "huntelaar": ["Klaas-Jan Huntelaar"],
    "mbappe": ["Kylian Mbappé", "Kylian Mbappe"],
    "cristiano": ["Cristiano Ronaldo"],
    "fontaine": ["Just Fontaine"],
    "pele": ["Pelé"],
    "kocsis": ["Sándor Kocsis", "Sandor Kocsis"],
}

import urllib.parse
import requests


def summary_url(title):
    return "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(title)


def bump_px(src, px=480):
    # .../thumb/a/ab/Name.jpg/320px-Name.jpg -> 480px
    import re
    return re.sub(r"/(\d+)px-", f"/{px}px-", src)


def get_thumb_via_requests(title):
    r = requests.get(summary_url(title), headers=HEAD, timeout=30)
    if r.status_code != 200:
        return None, f"http {r.status_code}"
    data = r.json()
    th = data.get("thumbnail", {}).get("source")
    orig = data.get("originalimage", {}).get("source")
    return (th, orig), None


def download(url):
    r = requests.get(url, headers=HEAD, timeout=40)
    if r.status_code == 200 and len(r.content) > 1500:
        return r.content
    return None


def fetch_scrapling(title):
    from scrapling.fetchers import Fetcher
    try:
        page = Fetcher.get(summary_url(title), headers=HEAD, timeout=30)
        data = json.loads(page.body if hasattr(page, "body") else page.html_content)
        th = data.get("thumbnail", {}).get("source")
        return th
    except Exception as e:
        print("  scrapling fail:", e)
        return None


def main():
    results = {}
    for key, titles in PLAYERS.items():
        dest = os.path.join(PH, key + ".jpg")
        if os.path.exists(dest) and os.path.getsize(dest) > 3000:
            print(f"[skip] {key} ya existe")
            results[key] = dest
            continue
        got = None
        for title in titles:
            try:
                (th, orig), err = get_thumb_via_requests(title)
            except Exception as e:
                th, orig, err = None, None, str(e)
            if not th:
                print(f"[{key}] '{title}' requests -> {err}; probando scrapling")
                th = fetch_scrapling(title)
            if not th:
                continue
            src = bump_px(th, 480)
            content = download(src) or download(th) or (download(orig) if orig else None)
            if content:
                with open(dest, "wb") as f:
                    f.write(content)
                print(f"[ok] {key}  <- {title}  ({len(content)//1024} KB)  {src}")
                got = dest
                break
        if not got:
            print(f"[MISS] {key}: no se pudo descargar")
        results[key] = got
        time.sleep(0.4)
    miss = [k for k, v in results.items() if not v]
    print("\nDescargadas:", sum(1 for v in results.values() if v), "/", len(PLAYERS))
    if miss:
        print("Faltan:", miss)


if __name__ == "__main__":
    main()
