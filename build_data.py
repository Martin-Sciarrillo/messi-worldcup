"""Parse FBref World Cup standard-stats HTML into worldcup_all.csv using data-stat attrs."""
import os, glob, re
import pandas as pd
from bs4 import BeautifulSoup

OUT = os.path.dirname(os.path.abspath(__file__))

WANT = {
    "player": "player",
    "nationality": "nation",
    "position": "pos",
    "team": "squad",
    "minutes": "minutes",
    "goals": "goals",
    "assists": "assists",
    "goals_assists": "ga",
    "goals_assists_per90": "ga_per90",
    "goals_per90": "goals_per90",
    "assists_per90": "assists_per90",
}

def parse_file(path, year):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    # FBref sometimes wraps tables in HTML comments; uncomment them.
    html = html.replace("<!--", "").replace("-->", "")
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", id="stats_standard")
    if table is None:
        return []
    tbody = table.find("tbody")
    rows = []
    for tr in tbody.find_all("tr"):
        if tr.get("class") and "thead" in tr.get("class"):
            continue
        cells = tr.find_all(["th", "td"])
        rec = {}
        for c in cells:
            ds = c.get("data-stat")
            if ds in WANT:
                rec[WANT[ds]] = c.get_text(strip=True)
        if rec.get("player"):
            rec["wc_year"] = year
            rows.append(rec)
    return rows

def main():
    all_rows = []
    files = sorted(glob.glob(os.path.join(OUT, "wc_*.html")))
    for path in files:
        m = re.search(r"wc_(\d{4})\.html", os.path.basename(path))
        if not m:
            continue
        year = int(m.group(1))
        rows = parse_file(path, year)
        print(f"{year}: {len(rows)} players")
        all_rows.extend(rows)
    df = pd.DataFrame(all_rows)
    df.to_csv(os.path.join(OUT, "worldcup_all.csv"), index=False)
    print(f"\nTotal: {len(df)} records, years: {sorted(df['wc_year'].unique())}")

if __name__ == "__main__":
    main()
