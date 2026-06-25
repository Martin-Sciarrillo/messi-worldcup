import sys, time, os
from scrapling.fetchers import StealthyFetcher

YEARS = [1966, 1970, 1974, 1978, 1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022]
OUT = os.path.dirname(os.path.abspath(__file__))
PROFILE = os.path.join(OUT, "cf_profile")

def fetch_year(year, headless, solve):
    out = os.path.join(OUT, f"wc_{year}.html")
    if os.path.exists(out) and os.path.getsize(out) > 300000:
        print(f"skip {year} (cached, {os.path.getsize(out)} bytes)", flush=True)
        return True
    url = f"https://fbref.com/en/comps/1/{year}/stats/{year}-World-Cup-Stats"
    try:
        r = StealthyFetcher.fetch(
            url,
            headless=headless,
            real_chrome=True,
            solve_cloudflare=solve,
            user_data_dir=PROFILE,
            wait_selector="table#stats_standard",
            timeout=60000,
            google_search=True,
        )
        html = r.html_content
        has_table = "stats_standard" in html
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"{year}: status={r.status} len={len(html)} table={has_table}", flush=True)
        return has_table
    except Exception as e:
        print(f"{year}: ERROR {type(e).__name__}: {e}", flush=True)
        return False

if __name__ == "__main__":
    headless = "--headful" not in sys.argv
    solve = "--solve" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    years = [int(a) for a in args] or YEARS
    ok = 0
    for y in years:
        if fetch_year(y, headless, solve):
            ok += 1
        time.sleep(3)
    print(f"\nDone: {ok}/{len(years)} editions fetched", flush=True)
