
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

RAW_CSV = Path("jumia_raw.csv")
CLEAN_CSV = Path("jumia_products_clean.csv")

# ---------------------------------------------------------------------------
# Regex maps for product‑type classification
# ---------------------------------------------------------------------------
TYPE_PATTERNS = {
    "smartphone": r"\b(?:smartphone|phone|galaxy|iphone)\b",
    "laptop": r"\blaptop|notebook|macbook|ideapad|thinkpad|inspiron\b",
    "tablet": r"\btablet|ipad|tab\b",
    "tv": r"\b(?:televis(?:ion)?|smart\s*tv|led\s*tv|uhd\s*tv)\b",
    "earpods": r"\b(?:earpods?|earbuds?|airpods?)\b",
    "smartwatch": r"\bwatch\b",
    "remote": r"\bremote\b",
    "console": r"\b(?:playstation|ps5|xbox|nintendo|switch)\b",
}

# Brand blacklist to avoid fuzzy confusion
BRAND_BLACKLIST = {"vision", "visio", "no"}  # "No Brand" often appears

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def to_float(txt: str | float | int | None) -> Optional[float]:
    """Convert a messy price string to float, else None."""
    if txt is None or (isinstance(txt, float) and np.isnan(txt)):
        return None
    if isinstance(txt, (int, float)):
        return float(txt)
    # keep digits, dot, comma
    digits = re.sub(r"[^0-9,\.]", "", str(txt))
    # remove thousand‑sep commas, replace comma decimal with dot
    if "," in digits and digits.count(",") == 1 and "." not in digits:
        digits = digits.replace(",", ".")
    digits = digits.replace(",", "")
    try:
        return float(digits)
    except ValueError:
        return None


def classify_type(title: str | None) -> Optional[str]:
    if not title:
        return None
    low = title.lower()
    for t, pat in TYPE_PATTERNS.items():
        if re.search(pat, low):
            return t
    return None

# ---------------------------------------------------------------------------
# Cleaning pipeline
# ---------------------------------------------------------------------------

def clean():
    if not RAW_CSV.exists():
        raise FileNotFoundError(f"Raw file {RAW_CSV} missing – run scraper first.")

    df = pd.read_csv(RAW_CSV)
    if df.empty:
        raise ValueError("Raw CSV is empty – nothing to clean.")

    # --- numeric prices -----------------------------------------------------
    df["price_numeric"] = df["price_txt"].apply(to_float)
    df["old_price_numeric"] = df["old_price_txt"].apply(to_float)

    # compute real discount percentage where old price exists
    df["discount_percentage"] = np.where(
        df["old_price_numeric"].notna() & (df["old_price_numeric"] > 0),
        (1 - df["price_numeric"] / df["old_price_numeric"]) * 100,
        np.nan,
    ).round(1)
    df.loc[df["discount_percentage"] < 0, "discount_percentage"] = np.nan

    # --- brand --------------------------------------------------------------
    df["brand"] = (
        df["title"].fillna("").str.extract(r"^(\w+)", expand=False).str.title()
    )
    df.loc[df["brand"].str.lower().isin(BRAND_BLACKLIST), "brand"] = np.nan

    # --- type ---------------------------------------------------------------
    df["type_product"] = df["title"].apply(classify_type)

    # --- Final tidy DataFrame ----------------------------------------------
    keep_cols = [
        "title",
        "brand",
        "type_product",
        "price_numeric",
        "old_price_numeric",
        "discount_percentage",
        "product_link",
        "image_url",  # thumbnail from scraper
        "category",
        "page_url",
    ]
    tidy = df[keep_cols]
    tidy.to_csv(CLEAN_CSV, index=False)
    print(f"✔ Cleaned dataset saved to {CLEAN_CSV} – {len(tidy):,} rows.")


if __name__ == "__main__":
    clean()
