function StatsCard({ icon: Icon, label, value, delay = 0 }) {
    return (
        <div className={`stat-card fade-in fade-in-delay-${delay}`}>
            <div className="stat-icon">
                <Icon size={24} />
            </div>
            <div className="stat-content">
                <div className="stat-label">{label}</div>
                <div className="stat-value">{value}</div>
            </div>
        </div>
    )
}

export default StatsCard
