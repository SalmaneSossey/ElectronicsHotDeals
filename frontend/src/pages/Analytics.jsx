import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts'
import { BarChart3 } from 'lucide-react'

const COLORS = ['#ff6b35', '#f7931e', '#10b981', '#6366f1', '#ec4899', '#8b5cf6', '#14b8a6', '#f59e0b']

function Analytics() {
    const [products, setProducts] = useState([])
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        try {
            const [productsRes, statsRes] = await Promise.all([
                fetch('/api/products?per_page=1000'),
                fetch('/api/products/stats')
            ])

            if (productsRes.ok) {
                const data = await productsRes.json()
                setProducts(data.products)
            }
            if (statsRes.ok) setStats(await statsRes.json())
        } catch (err) {
            console.error('Failed to fetch data:', err)
        } finally {
            setLoading(false)
        }
    }

    // Prepare chart data
    const categoryData = stats?.categories?.map(cat => {
        const catProducts = products.filter(p => p.category === cat)
        const avgPrice = catProducts.reduce((sum, p) => sum + (p.price_numeric || 0), 0) / (catProducts.length || 1)
        return { name: cat, count: catProducts.length, avgPrice: Math.round(avgPrice) }
    }) || []

    const typeData = stats?.types?.filter(t => t).map(type => {
        const count = products.filter(p => p.type_product === type).length
        return { name: type, value: count }
    }).filter(d => d.value > 0) || []

    const priceRanges = [
        { range: '0-500', min: 0, max: 500 },
        { range: '500-1K', min: 500, max: 1000 },
        { range: '1K-2K', min: 1000, max: 2000 },
        { range: '2K-5K', min: 2000, max: 5000 },
        { range: '5K-10K', min: 5000, max: 10000 },
        { range: '10K+', min: 10000, max: Infinity },
    ]

    const priceDistribution = priceRanges.map(range => ({
        name: range.range,
        count: products.filter(p => (p.price_numeric || 0) >= range.min && (p.price_numeric || 0) < range.max).length
    }))

    const brandData = stats?.brands?.slice(0, 10).map(brand => ({
        name: brand,
        count: products.filter(p => p.brand === brand).length
    })).sort((a, b) => b.count - a.count) || []

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
                    <BarChart3 style={{ display: 'inline', marginRight: '0.5rem', color: 'var(--accent-primary)' }} />
                    Analytics Dashboard
                </h1>
                <p className="page-subtitle">Visual insights into the electronics market</p>
            </header>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', gap: '1.5rem' }}>
                {/* Average Price by Category */}
                <div className="chart-container">
                    <h3 className="chart-title">Average Price by Category (Dhs)</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={categoryData} layout="vertical">
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                            <XAxis type="number" stroke="#a0a0b8" />
                            <YAxis dataKey="name" type="category" width={120} stroke="#a0a0b8" fontSize={12} />
                            <Tooltip
                                contentStyle={{ background: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                                labelStyle={{ color: '#fff' }}
                            />
                            <Bar dataKey="avgPrice" fill="url(#colorGradient)" radius={[0, 4, 4, 0]} />
                            <defs>
                                <linearGradient id="colorGradient" x1="0" y1="0" x2="1" y2="0">
                                    <stop offset="0%" stopColor="#ff6b35" />
                                    <stop offset="100%" stopColor="#f7931e" />
                                </linearGradient>
                            </defs>
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                {/* Product Types Distribution */}
                <div className="chart-container">
                    <h3 className="chart-title">Products by Type</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                            <Pie
                                data={typeData}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={100}
                                paddingAngle={3}
                                dataKey="value"
                                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                labelLine={false}
                            >
                                {typeData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{ background: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </div>

                {/* Price Distribution */}
                <div className="chart-container">
                    <h3 className="chart-title">Price Distribution</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={priceDistribution}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                            <XAxis dataKey="name" stroke="#a0a0b8" />
                            <YAxis stroke="#a0a0b8" />
                            <Tooltip
                                contentStyle={{ background: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                            />
                            <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                {/* Top Brands */}
                <div className="chart-container">
                    <h3 className="chart-title">Top 10 Brands by Product Count</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={brandData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                            <XAxis dataKey="name" stroke="#a0a0b8" fontSize={11} angle={-45} textAnchor="end" height={80} />
                            <YAxis stroke="#a0a0b8" />
                            <Tooltip
                                contentStyle={{ background: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                            />
                            <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    )
}

export default Analytics
