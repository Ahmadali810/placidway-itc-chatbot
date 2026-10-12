"""Polite scraper for the 7 PlacidWay assessment URLs. Saves clean text per page."""
import json, re, time
import requests
from bs4 import BeautifulSoup

URLS = [
    ("profile", "https://www.placidway.com/profile/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center"),
    ("package_adenocarcinoma", "https://www.placidway.com/package/7903/Alternative-Adenocarcinoma-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC"),
    ("package_adrenal", "https://www.placidway.com/package/7902/Alternative-Adrenal-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC"),
    ("package_anal", "https://www.placidway.com/package/7901/Alternative-Anal-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC"),
    ("videos", "https://www.placidway.com/profile-videos/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center"),
    ("price_list", "https://www.placidway.com/price-list/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center"),
    ("search_pricings", "https://www.placidway.com/search-medical-pricings/Alternative-Medicine/All/1"),
]

HEADERS = {"User-Agent": "Mozilla/5.0 (assessment-bot; contact: vornexia4@gmail.com)"}

def clean_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "iframe"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.split("\n")]
    lines = [ln for ln in lines if len(ln) > 2]
    # drop obvious nav/cookie junk lines
    junk = re.compile(r"cookie|privacy policy|terms of (use|service)|all rights reserved|subscribe|newsletter", re.I)
    lines = [ln for ln in lines if not junk.search(ln)]
    # dedupe while keeping order
    seen, out = set(), []
    for ln in lines:
        if ln not in seen:
            seen.add(ln)
            out.append(ln)
    return "\n".join(out)

def main():
    results = {}
    for name, url in URLS:
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()
            text = clean_text(r.text)
            results[name] = {"url": url, "status": r.status_code, "chars": len(text), "text": text}
            print(f"OK {name}: {r.status_code}, {len(text)} chars", flush=True)
        except Exception as e:
            results[name] = {"url": url, "status": "error", "error": str(e), "chars": 0, "text": ""}
            print(f"FAIL {name}: {e}", flush=True)
        time.sleep(4)  # polite: 4s between requests
    with open("pages.json", "w") as f:
        json.dump(results, f, indent=1)
    print("saved pages.json", flush=True)

if __name__ == "__main__":
    main()
