
from __future__ import annotations

import csv
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup, Tag

RAW_CSV = Path("jumia_raw.csv")

CATEGORIES = {
    "telephone_tablette": "https://www.jumia.ma/telephone-tablette/",
    "electronique": "https://www.jumia.ma/electronique/",
    "informatique": "https://www.jumia.ma/ordinateurs-accessoires-informatique/",
    "gaming": "https://www.jumia.ma/jeux-videos-consoles/",
}

N_PAGES = 20  # scrape pages 1 → 20 inclusive for each category

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def clean(txt: str | None) -> str | None:
    if txt is None:
        return None
    return (
        txt.replace("\u202f", "")  # narrow NBSP
        .replace("\xa0", " ")
        .strip()
    )


def extract_image(card: Tag) -> Optional[str]:
    img = card.find("img")
    if not img:
        return None
    url = img.get("data-src") or img.get("src")
    if url and url.startswith("//"):
        url = "https:" + url
    return url


def parse_listing(html: str, url: str, cat_key: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    # product cards: both classic <article> and new <div> variants
    cards = soup.select("article.prd, div[data-card-name='prd']")
    rows: List[Dict[str, str]] = []
    for card in cards:
        # TITLE (any element with class name)
        title_tag = card.select_one(".name")

        # PRICE (current)
        price_tag = card.select_one("div.prc, .prc")

        # OLD PRICE (may have class old or -old-prc)
        old_tag = card.select_one("div.old, .-old-prc, span.-old-prc")

        # DISCOUNT badge (% off) – various badge classes
        discount_tag = card.select_one(
            "div.bdg._dsct, span.bdg._dsct, span.tag._dsct, div.tag._dsct"
        )

        link_tag = card.find("a", class_="core")

        title = clean(title_tag.get_text(" ")) if title_tag else None
        price_txt = clean(price_tag.get_text()) if price_tag else None
        old_price_txt = clean(old_tag.get_text()) if old_tag else None
        discount_txt = clean(discount_tag.get_text()) if discount_tag else None
        product_link = (
            "https://www.jumia.ma" + link_tag["href"] if link_tag and link_tag.get("href") else None
        )
        image_url = extract_image(card)
        brand_guess = title.split(" ")[0].split("-")[0] if title else None

        rows.append(
            {
                "title": title,
                "price_txt": price_txt,
                "old_price_txt": old_price_txt,
                "discount_txt": discount_txt,
                "brand_guess": brand_guess,
                "product_link": product_link,
                "image_url": image_url,
                "page_url": url,
                "category": cat_key,
            }
        )
    return rows


# ---------------------------------------------------------------------------
# Main scraping loop
# ---------------------------------------------------------------------------

def scrape() -> List[Dict[str, str]]:
    sess = requests.Session(); sess.headers.update(HEADERS)
    all_rows: List[Dict[str, str]] = []

    for cat_key, base_url in CATEGORIES.items():
        print(f"\n=== {cat_key.upper()} ===")
        for p in range(1, N_PAGES + 1):
            url = f"{base_url}?page={p}#catalog-listing"
            print(f"→ {url}")
            r = sess.get(url, timeout=30)
            if r.status_code != 200:
                print(f"   HTTP {r.status_code} – skipping page")
                time.sleep(1.5)
                continue
            rows = parse_listing(r.text, url, cat_key)
            print(f"  {len(rows):3d} rows")
            all_rows.extend(rows)
            time.sleep(1.5)
    return all_rows


# ---------------------------------------------------------------------------
# Save helper
# ---------------------------------------------------------------------------

def save_csv(rows: List[Dict[str, str]]):
    if not rows:
        print("No rows scraped – nothing to save.")
        return
    RAW_CSV.write_text("")  # truncate existing
    with RAW_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)
    print(f"\n✔ Saved {len(rows):,} rows ➜ {RAW_CSV}")


if __name__ == "__main__":
    data = scrape(); save_csv(data)
