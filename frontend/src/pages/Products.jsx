import { useState, useEffect } from 'react'
import { Search, SlidersHorizontal, Package } from 'lucide-react'
import ProductCard from '../components/ProductCard'

function Products() {
    const [products, setProducts] = useState([])
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)
    const [page, setPage] = useState(1)
    const [total, setTotal] = useState(0)
    const perPage = 12

    // Filters
    const [search, setSearch] = useState('')
    const [category, setCategory] = useState('')
    const [brand, setBrand] = useState('')
    const [type, setType] = useState('')
    const [sortBy, setSortBy] = useState('')

    useEffect(() => {
        fetchStats()
    }, [])

    useEffect(() => {
        fetchProducts()
    }, [page, category, brand, type, sortBy])

    const fetchStats = async () => {
        try {
            const res = await fetch('/api/products/stats')
            if (res.ok) setStats(await res.json())
        } catch (err) {
            console.error('Failed to fetch stats:', err)
        }
    }

    const fetchProducts = async () => {
        setLoading(true)
        try {
            const params = new URLSearchParams({
                page: page.toString(),
                per_page: perPage.toString(),
            })

            if (category) params.append('category', category)
            if (brand) params.append('brand', brand)
            if (type) params.append('type_product', type)
            if (search) params.append('search', search)
            if (sortBy) {
                const [field, order] = sortBy.split('-')
                params.append('sort_by', field)
                params.append('sort_order', order)
            }

            const res = await fetch(`/api/products?${params}`)
            if (res.ok) {
                const data = await res.json()
                setProducts(data.products)
                setTotal(data.total)
            }
        } catch (err) {
            console.error('Failed to fetch products:', err)
        } finally {
            setLoading(false)
        }
    }

    const handleSearch = (e) => {
        e.preventDefault()
        setPage(1)
        fetchProducts()
    }

    const totalPages = Math.ceil(total / perPage)

    return (
        <div>
            <header className="page-header">
                <h1 className="page-title">Product Catalog</h1>
                <p className="page-subtitle">Browse {total.toLocaleString()} electronics from Jumia Morocco</p>
            </header>

            {/* Filters Section */}
            <div className="glass-card" style={{ marginBottom: '2rem' }}>
                <form onSubmit={handleSearch} style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
                    {/* Search */}
                    <div className="filter-section" style={{ flex: '2', minWidth: '200px', marginBottom: 0 }}>
                        <label className="filter-title">Search</label>
                        <div style={{ position: 'relative' }}>
                            <Search size={18} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                            <input
                                type="text"
                                className="filter-input"
                                placeholder="Search products..."
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                style={{ paddingLeft: '2.5rem' }}
                            />
                        </div>
                    </div>

                    {/* Category */}
                    <div className="filter-section" style={{ flex: '1', minWidth: '150px', marginBottom: 0 }}>
                        <label className="filter-title">Category</label>
                        <select
                            className="filter-select"
                            value={category}
                            onChange={(e) => { setCategory(e.target.value); setPage(1); }}
                        >
                            <option value="">All Categories</option>
                            {stats?.categories?.map(cat => (
                                <option key={cat} value={cat}>{cat}</option>
                            ))}
                        </select>
                    </div>

                    {/* Type */}
                    <div className="filter-section" style={{ flex: '1', minWidth: '150px', marginBottom: 0 }}>
                        <label className="filter-title">Type</label>
                        <select
                            className="filter-select"
                            value={type}
                            onChange={(e) => { setType(e.target.value); setPage(1); }}
                        >
                            <option value="">All Types</option>
                            {stats?.types?.map(t => (
                                <option key={t} value={t}>{t}</option>
                            ))}
                        </select>
                    </div>

                    {/* Brand */}
                    <div className="filter-section" style={{ flex: '1', minWidth: '150px', marginBottom: 0 }}>
                        <label className="filter-title">Brand</label>
                        <select
                            className="filter-select"
                            value={brand}
                            onChange={(e) => { setBrand(e.target.value); setPage(1); }}
                        >
                            <option value="">All Brands</option>
                            {stats?.brands?.slice(0, 50).map(b => (
                                <option key={b} value={b}>{b}</option>
                            ))}
                        </select>
                    </div>

                    {/* Sort */}
                    <div className="filter-section" style={{ flex: '1', minWidth: '150px', marginBottom: 0 }}>
                        <label className="filter-title">Sort By</label>
                        <select
                            className="filter-select"
                            value={sortBy}
                            onChange={(e) => { setSortBy(e.target.value); setPage(1); }}
                        >
                            <option value="">Default</option>
                            <option value="price-asc">Price: Low to High</option>
                            <option value="price-desc">Price: High to Low</option>
                            <option value="discount-desc">Highest Discount</option>
                        </select>
                    </div>

                    <button type="submit" className="btn btn-primary" style={{ height: '42px' }}>
                        <SlidersHorizontal size={16} /> Apply
                    </button>
                </form>
            </div>

            {/* Products Grid */}
            {loading ? (
                <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
                    <div className="loading-spinner" style={{ width: 48, height: 48 }}></div>
                </div>
            ) : products.length > 0 ? (
                <>
                    <div className="products-grid">
                        {products.map((product, index) => (
                            <ProductCard
                                key={index}
                                product={{
                                    title: product.title,
                                    brand: product.brand,
                                    price: product.price_numeric,
                                    old_price: product.old_price_numeric,
                                    discount: product.discount_percentage,
                                    image_url: product.image_url,
                                    product_link: product.product_link,
                                    category: product.category
                                }}
                            />
                        ))}
                    </div>

                    {/* Pagination */}
                    <div className="pagination">
                        <button
                            className="pagination-btn"
                            onClick={() => setPage(p => Math.max(1, p - 1))}
                            disabled={page === 1}
                        >
                            Previous
                        </button>
                        <span className="pagination-info">
                            Page {page} of {totalPages}
                        </span>
                        <button
                            className="pagination-btn"
                            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                            disabled={page >= totalPages}
                        >
                            Next
                        </button>
                    </div>
                </>
            ) : (
                <div className="empty-state">
                    <Package className="empty-state-icon" />
                    <p>No products found matching your filters.</p>
                </div>
            )}
        </div>
    )
}

export default Products
