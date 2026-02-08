import { useState, useEffect } from 'react'
import { Package, TrendingDown, Tag, Building2, Flame } from 'lucide-react'
import StatsCard from '../components/StatsCard'
import ProductCard from '../components/ProductCard'

function Dashboard() {
    const [stats, setStats] = useState(null)
    const [topDeals, setTopDeals] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        try {
            const [statsRes, dealsRes] = await Promise.all([
                fetch('/api/products/stats'),
                fetch('/api/products/top-deals?limit=5')
            ])

            if (statsRes.ok) setStats(await statsRes.json())
            if (dealsRes.ok) setTopDeals(await dealsRes.json())
        } catch (err) {
            console.error('Failed to fetch data:', err)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
                <div className="loading-spinner" style={{ width: 48, height: 48 }}></div>
            </div>
        )
    }

    return (
        <div>
            <header className="page-header">
                <h1 className="page-title">
                    Welcome to <span className="gradient-text">HotDeals</span>
                </h1>
                <p className="page-subtitle">
                    Discover the best electronics deals in Morocco from Jumia & Electroplanet
                </p>
            </header>

            {/* Stats Grid */}
            <section className="stats-grid">
                <StatsCard
                    icon={Package}
                    label="Total Products"
                    value={stats?.total_products?.toLocaleString() || '0'}
                    delay={1}
                />
                <StatsCard
                    icon={TrendingDown}
                    label="Avg Discount"
                    value={`${stats?.avg_discount?.toFixed(1) || '0'}%`}
                    delay={2}
                />
                <StatsCard
                    icon={Tag}
                    label="Avg Price"
                    value={`${Math.round(stats?.avg_price || 0).toLocaleString()} Dhs`}
                    delay={3}
                />
                <StatsCard
                    icon={Building2}
                    label="Brands"
                    value={stats?.brands_count || '0'}
                    delay={4}
                />
            </section>

            {/* Top Deals Section */}
            <section>
                <h2 className="section-title">
                    <Flame /> Top 5 Hot Deals
                </h2>

                {topDeals.length > 0 ? (
                    <div className="products-grid">
                        {topDeals.map((deal, index) => (
                            <ProductCard
                                key={index}
                                product={{
                                    title: deal.title,
                                    brand: deal.brand,
                                    price: deal.price,
                                    old_price: deal.old_price,
                                    discount: deal.discount,
                                    image_url: deal.image_url,
                                    product_link: deal.product_link,
                                    category: deal.category
                                }}
                            />
                        ))}
                    </div>
                ) : (
                    <div className="empty-state">
                        <Package className="empty-state-icon" />
                        <p>No deals found. Try refreshing the data.</p>
                    </div>
                )}
            </section>
        </div>
    )
}

export default Dashboard
