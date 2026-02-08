import { ExternalLink } from 'lucide-react'

function ProductCard({ product }) {
    const formatPrice = (price) => {
        if (!price) return 'N/A'
        return new Intl.NumberFormat('fr-MA', { minimumFractionDigits: 0 }).format(price) + ' Dhs'
    }

    return (
        <article className="product-card fade-in">
            {product.discount > 0 && (
                <span className="product-badge">-{Math.round(product.discount)}%</span>
            )}

            <img
                src={product.image_url || 'https://via.placeholder.com/300x200?text=No+Image'}
                alt={product.title || 'Product'}
                className="product-image"
                loading="lazy"
                onError={(e) => {
                    e.target.src = 'https://via.placeholder.com/300x200?text=No+Image'
                }}
            />

            <div className="product-content">
                <div className="product-category">{product.category || 'Electronics'}</div>
                <h3 className="product-title">{product.title || 'Untitled Product'}</h3>

                <div className="product-price">
                    <span className="product-price-current">{formatPrice(product.price)}</span>
                    {product.old_price && product.old_price > product.price && (
                        <span className="product-price-old">{formatPrice(product.old_price)}</span>
                    )}
                </div>

                {product.brand && (
                    <div className="product-brand">by {product.brand}</div>
                )}

                {product.product_link && (
                    <a
                        href={product.product_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="product-link"
                    >
                        View on Jumia <ExternalLink size={14} />
                    </a>
                )}
            </div>
        </article>
    )
}

export default ProductCard
