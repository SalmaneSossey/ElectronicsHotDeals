"""
Product API routes
"""
from fastapi import APIRouter, Query
from typing import Optional, List
import pandas as pd
import numpy as np
from pathlib import Path

from models import Product, ProductListResponse, StatsResponse, TopDeal

router = APIRouter(prefix="/api/products", tags=["products"])

# Data file path
DATA_CSV = Path(__file__).parent.parent.parent / "jumia_products_clean.csv"

# Trusted brands for deal scoring
TRUSTED_BRANDS = {"samsung", "xiaomi", "apple", "lg", "sony", "dell", "hp", "lenovo", "huawei", "asus"}


def load_data() -> pd.DataFrame:
    """Load the cleaned product data"""
    if not DATA_CSV.exists():
        return pd.DataFrame()
    return pd.read_csv(DATA_CSV)


@router.get("", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=1000),
    category: Optional[str] = None,
    brand: Optional[str] = None,
    type_product: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = Query(None, regex="^(price|discount|title)$"),
    sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
):
    """List products with filtering, pagination, and sorting"""
    df = load_data()
    
    if df.empty:
        return ProductListResponse(products=[], total=0, page=page, per_page=per_page)
    
    # Apply filters
    if category:
        df = df[df["category"].fillna('').str.lower() == category.lower()]
    if brand:
        df = df[df["brand"].fillna('').str.lower() == brand.lower()]
    if type_product:
        df = df[df["type_product"].fillna('').str.lower() == type_product.lower()]
    if min_price is not None:
        df = df[df["price_numeric"] >= min_price]
    if max_price is not None:
        df = df[df["price_numeric"] <= max_price]
    if search:
        df = df[df["title"].fillna('').str.contains(search, case=False, na=False)]
    
    # Apply sorting
    if sort_by:
        sort_col = {
            "price": "price_numeric",
            "discount": "discount_percentage",
            "title": "title"
        }.get(sort_by)
        if sort_col and sort_col in df.columns:
            df = df.sort_values(sort_col, ascending=(sort_order == "asc"), na_position="last")
    
    # Pagination
    total = len(df)
    start = (page - 1) * per_page
    end = start + per_page
    df_page = df.iloc[start:end]
    
    # Convert to products
    products = []
    for _, row in df_page.iterrows():
        products.append(Product(
            title=row.get("title") if pd.notna(row.get("title")) else None,
            brand=row.get("brand") if pd.notna(row.get("brand")) else None,
            type_product=row.get("type_product") if pd.notna(row.get("type_product")) else None,
            price_numeric=row.get("price_numeric") if pd.notna(row.get("price_numeric")) else None,
            old_price_numeric=row.get("old_price_numeric") if pd.notna(row.get("old_price_numeric")) else None,
            discount_percentage=row.get("discount_percentage") if pd.notna(row.get("discount_percentage")) else None,
            product_link=row.get("product_link") if pd.notna(row.get("product_link")) else None,
            image_url=row.get("image_url") if pd.notna(row.get("image_url")) else None,
            category=row.get("category") if pd.notna(row.get("category")) else None,
        ))
    
    return ProductListResponse(products=products, total=total, page=page, per_page=per_page)


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get dashboard statistics"""
    df = load_data()
    
    if df.empty:
        return StatsResponse(
            total_products=0,
            avg_price=0,
            avg_discount=0,
            brands_count=0,
            categories=[],
            types=[],
            brands=[]
        )
    
    return StatsResponse(
        total_products=len(df),
        avg_price=float(df["price_numeric"].mean()) if "price_numeric" in df else 0,
        avg_discount=float(df["discount_percentage"].mean()) if "discount_percentage" in df else 0,
        brands_count=int(df["brand"].nunique()) if "brand" in df else 0,
        categories=sorted(df["category"].dropna().unique().tolist()) if "category" in df else [],
        types=sorted(df["type_product"].dropna().unique().tolist()) if "type_product" in df else [],
        brands=sorted(df["brand"].dropna().unique().tolist()) if "brand" in df else [],
    )


@router.get("/top-deals", response_model=List[TopDeal])
async def get_top_deals(limit: int = Query(5, ge=1, le=20)):
    """Get top deals based on deal score"""
    df = load_data()
    
    if df.empty:
        return []
    
    # Calculate deal score
    df = df.copy()
    disc_series = df["discount_percentage"].fillna(0) if "discount_percentage" in df else 0
    price_series = df["price_numeric"].replace(0, np.nan)
    brand_score = df["brand"].str.lower().apply(lambda b: 1 if b in TRUSTED_BRANDS else 0) if "brand" in df else 0
    
    df["deal_score"] = (
        disc_series * 0.4 +
        (1 / price_series).fillna(0) * 10000 * 0.3 +
        brand_score * 0.3
    )
    
    # Get top deals
    top = df.nlargest(limit, "deal_score")
    
    deals = []
    for _, row in top.iterrows():
        deals.append(TopDeal(
            title=row.get("title") if pd.notna(row.get("title")) else None,
            brand=row.get("brand") if pd.notna(row.get("brand")) else None,
            price=row.get("price_numeric") if pd.notna(row.get("price_numeric")) else None,
            old_price=row.get("old_price_numeric") if pd.notna(row.get("old_price_numeric")) else None,
            discount=row.get("discount_percentage") if pd.notna(row.get("discount_percentage")) else None,
            image_url=row.get("image_url") if pd.notna(row.get("image_url")) else None,
            product_link=row.get("product_link") if pd.notna(row.get("product_link")) else None,
            category=row.get("category") if pd.notna(row.get("category")) else None,
            deal_score=float(row["deal_score"]),
        ))
    
    return deals
