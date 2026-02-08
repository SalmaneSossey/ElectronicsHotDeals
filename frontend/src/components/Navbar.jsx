import { NavLink } from 'react-router-dom'
import { Home, ShoppingBag, BarChart3, MessageCircle, Zap, RefreshCw } from 'lucide-react'
import { useState, useEffect } from 'react'

function Navbar() {
    const [status, setStatus] = useState({ status: 'idle', products_count: 0 })
    const [sidebarOpen, setSidebarOpen] = useState(false)
    const [isRefreshing, setIsRefreshing] = useState(false)

    useEffect(() => {
        fetchStatus()
        const interval = setInterval(fetchStatus, 30000)
        return () => clearInterval(interval)
    }, [])

    const fetchStatus = async () => {
        try {
            const res = await fetch('/api/scrape/status')
            if (res.ok) {
                const data = await res.json()
                setStatus(data)
            }
        } catch (err) {
            console.error('Failed to fetch status:', err)
        }
    }

    const triggerScrape = async () => {
        setIsRefreshing(true)
        try {
            await fetch('/api/scrape/trigger', { method: 'POST' })
            setTimeout(fetchStatus, 2000)
        } catch (err) {
            console.error('Failed to trigger scrape:', err)
        }
        setTimeout(() => setIsRefreshing(false), 3000)
    }

    const navItems = [
        { path: '/', icon: Home, label: 'Dashboard' },
        { path: '/products', icon: ShoppingBag, label: 'Products' },
        { path: '/analytics', icon: BarChart3, label: 'Analytics' },
        { path: '/chat', icon: MessageCircle, label: 'AI Chat' },
    ]

    return (
        <>
            {/* Mobile Header */}
            <header className="mobile-header">
                <div className="sidebar-logo">
                    <div className="sidebar-logo-icon">⚡</div>
                    <span className="sidebar-logo-text">HotDeals</span>
                </div>
                <button className="menu-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
                    ☰
                </button>
            </header>

            {/* Sidebar */}
            <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
                <div className="sidebar-logo">
                    <div className="sidebar-logo-icon">⚡</div>
                    <div>
                        <div className="sidebar-logo-text">HotDeals</div>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Morocco</span>
                    </div>
                </div>

                <nav className="sidebar-nav">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                            onClick={() => setSidebarOpen(false)}
                        >
                            <item.icon />
                            <span>{item.label}</span>
                        </NavLink>
                    ))}
                </nav>

                <div className="sidebar-status">
                    <div className="status-indicator">
                        <span className="status-dot" style={{
                            background: status.is_running ? 'var(--warning)' : 'var(--success)'
                        }}></span>
                        <span>{status.is_running ? 'Scraping...' : 'System Active'}</span>
                    </div>
                    <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {status.products_count.toLocaleString()} products loaded
                    </div>
                    <button
                        className="btn btn-secondary"
                        style={{ width: '100%', marginTop: '0.75rem', fontSize: '0.75rem' }}
                        onClick={triggerScrape}
                        disabled={isRefreshing || status.is_running}
                    >
                        <RefreshCw size={14} className={isRefreshing ? 'loading-spinner' : ''} />
                        Refresh Data
                    </button>
                </div>
            </aside>

            {/* Overlay for mobile */}
            {sidebarOpen && (
                <div
                    style={{
                        position: 'fixed',
                        inset: 0,
                        background: 'rgba(0,0,0,0.5)',
                        zIndex: 90
                    }}
                    onClick={() => setSidebarOpen(false)}
                />
            )}
        </>
    )
}

export default Navbar
