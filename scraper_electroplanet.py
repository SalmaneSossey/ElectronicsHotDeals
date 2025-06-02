"""
Electroplanet product scraper
----------------------------
Scrapes product data (name, price, product URL, image URL, category) from Electroplanet.ma
and writes the results into a JSON‑lines file ``electroplanet_products.jsonl``.

Requirements::

    pip install playwright pandas
    playwright install

Usage::

    python scraper_electroplanet.py  # saves a JSONL file in the current directory

Tweak the ``START_URLS`` dictionary to add or remove categories you wish to scrape.

NOTE: Electroplanet renders its catalogue with client‑side JavaScript, so we control a
headless Chromium browser (via Playwright) instead of using raw ``requests``.
"""

from __future__ import annotations
import asyncio, json
from pathlib import Path
from typing import List, Dict, Any

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

START_URLS: dict[str, str] = {
    # "label": "category‑landing‑page‑URL"
    "smartphones": "https://www.electroplanet.ma/smartphone-tablette-gps/smartphone", # to check
    "televisions": "https://www.electroplanet.ma/tv-photo-video/televiseur/tous-les-televiseur", #televisions are scraped 
    "laptops": "https://www.electroplanet.ma/informatique/ordinateur-portable", # to check
}

OUT_PATH = Path("electroplanet_products.jsonl")
SCROLL_PAUSE_MS = 1500  # tune if products stop loading too soon
HEADLESS = True  # flip to False to watch the browser when debugging

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def auto_scroll(page):
    """Scrolls to the bottom of the page so that lazy‑loaded products appear."""
    previous_height = 0
    while True:
        current_height: int = await page.evaluate("document.body.scrollHeight")
        if current_height == previous_height:
            break
        previous_height = current_height
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(SCROLL_PAUSE_MS)


async def extract_cards(page, category: str) -> List[Dict[str, Any]]:
    """Parses all <li class="product-item"> elements that have become visible."""
    cards = await page.query_selector_all("li.product-item")
    data: list[dict[str, Any]] = []
    for li in cards:
        try:
            title_el = await li.query_selector(".product-item-link")
            price_el = await li.query_selector(".price")
            link_el = await li.query_selector("a")
            img_el = await li.query_selector("img.product-image-photo")

            data.append(
                {
                    "category": category,
                    "name": (await title_el.inner_text()).strip(),
                    "price": (await price_el.inner_text()).strip(),
                    "url": await link_el.get_attribute("href"),
                    "image": await img_el.get_attribute("src"),
                }
            )
        except Exception:
            # Skip quietly if the expected sub‑element is missing
            continue
    return data


async def harvest(playwright, label: str, url: str) -> List[Dict[str, Any]]:
    browser = await playwright.chromium.launch(headless=HEADLESS)
    ctx = await browser.new_context(
        locale="fr-FR",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    )
    page = await ctx.new_page()

    print(f">>> Visiting {label} ({url})")
    try:
        await page.goto(url, timeout=60_000)
        await auto_scroll(page)
        products = await extract_cards(page, label)
    except PlaywrightTimeoutError:
        print(f"!! Timeout while loading {url}")
        products = []
    finally:
        await ctx.close()
        await browser.close()
    return products


async def main():
    async with async_playwright() as p:
        all_rows: list[dict[str, Any]] = []
        for label, link in START_URLS.items():
            all_rows.extend(await harvest(p, label, link))

        print(f"Total products scraped: {len(all_rows)}")
        with OUT_PATH.open("w", encoding="utf-8") as fp:
            for row in all_rows:
                fp.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"Saved to {OUT_PATH.resolve()}")


if __name__ == "__main__":
    asyncio.run(main())
