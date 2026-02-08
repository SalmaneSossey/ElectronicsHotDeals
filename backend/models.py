from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Product(BaseModel):
    title: Optional[str] = None
    brand: Optional[str] = None
    type_product: Optional[str] = None
    price_numeric: Optional[float] = None
    old_price_numeric: Optional[float] = None
    discount_percentage: Optional[float] = None
    product_link: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None


class ProductListResponse(BaseModel):
    products: List[Product]
    total: int
    page: int
    per_page: int


class StatsResponse(BaseModel):
    total_products: int
    avg_price: float
    avg_discount: float
    brands_count: int
    categories: List[str]
    types: List[str]
    brands: List[str]


class TopDeal(BaseModel):
    title: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    old_price: Optional[float] = None
    discount: Optional[float] = None
    image_url: Optional[str] = None
    product_link: Optional[str] = None
    category: Optional[str] = None
    deal_score: float


class ScrapeStatus(BaseModel):
    last_scrape: Optional[datetime] = None
    status: str
    products_count: int
    is_running: bool
