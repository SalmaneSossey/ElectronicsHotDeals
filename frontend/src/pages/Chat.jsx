import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Search } from 'lucide-react'

function Chat() {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'Hello! I can help you find the best electronics deals. Try asking:\n\n• "Show me Samsung phones"\n• "Best laptops under 5000 Dhs"\n• "TVs with discounts"\n• "Cheapest tablets"\n• "Top gaming products"' }
    ])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [products, setProducts] = useState([])
    const messagesEndRef = useRef(null)

    useEffect(() => {
        // Load products once
        fetch('/api/products?per_page=1000')
            .then(res => res.json())
            .then(data => setProducts(data.products || []))
            .catch(() => { })
    }, [])

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const searchProducts = (query) => {
        const q = query.toLowerCase()
        let results = [...products]

        // Extract price constraints
        const underMatch = q.match(/under\s+(\d+)/)
        const aboveMatch = q.match(/(?:above|over)\s+(\d+)/)
        const maxPrice = underMatch ? parseInt(underMatch[1]) : null
        const minPrice = aboveMatch ? parseInt(aboveMatch[1]) : null

        // Apply price filters
        if (maxPrice) results = results.filter(p => (p.price_numeric || 0) <= maxPrice)
        if (minPrice) results = results.filter(p => (p.price_numeric || 0) >= minPrice)

        // Check for discount requests
        if (q.includes('discount') || q.includes('sale') || q.includes('deal')) {
            results = results.filter(p => (p.discount_percentage || 0) > 20)
            results.sort((a, b) => (b.discount_percentage || 0) - (a.discount_percentage || 0))
        }

        // Check for cheap/budget requests
        if (q.includes('cheap') || q.includes('budget') || q.includes('affordable')) {
            results.sort((a, b) => (a.price_numeric || 0) - (b.price_numeric || 0))
        }

        // Check for best/top requests
        if (q.includes('best') || q.includes('top')) {
            results = results.filter(p => (p.discount_percentage || 0) > 15)
        }

        // Keyword search in title/brand/category
        const keywords = q.replace(/under\s+\d+/g, '').replace(/above\s+\d+/g, '')
            .split(/\s+/).filter(w => w.length > 2 && !['the', 'and', 'for', 'with', 'show', 'find', 'get', 'best', 'good'].includes(w))

        if (keywords.length > 0) {
            results = results.filter(p => {
                const text = `${p.title} ${p.brand} ${p.category} ${p.type_product}`.toLowerCase()
                return keywords.some(kw => text.includes(kw))
            })
        }

        return results.slice(0, 8)
    }

    const formatResponse = (query, results) => {
        if (results.length === 0) {
            return "I couldn't find products matching your criteria. Try different keywords or a higher price range!"
        }

        let response = `Found ${results.length} products for you:\n\n`

        results.forEach((p, i) => {
            const discount = p.discount_percentage ? ` (${Math.round(p.discount_percentage)}% off!)` : ''
            response += `${i + 1}. **${p.title}**\n`
            response += `   💰 ${p.price_numeric?.toFixed(0) || 'N/A'} Dhs${discount}\n`
            response += `   🏷️ ${p.brand || 'Unknown'} | ${p.category || ''}\n\n`
        })

        response += `\n💡 *Tip: Visit the Products page for more filters!*`
        return response
    }

    const handleSend = async () => {
        if (!input.trim() || loading) return

        const userMessage = input.trim()
        setInput('')
        setMessages(prev => [...prev, { role: 'user', content: userMessage }])
        setLoading(true)

        // Simulate slight delay for better UX
        await new Promise(r => setTimeout(r, 500))

        const results = searchProducts(userMessage)
        const response = formatResponse(userMessage, results)

        setMessages(prev => [...prev, { role: 'assistant', content: response }])
        setLoading(false)
    }

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    return (
        <div>
            <header className="page-header">
                <h1 className="page-title">
                    <Search style={{ display: 'inline', marginRight: '0.5rem', color: 'var(--accent-primary)' }} />
                    Smart Product Search
                </h1>
                <p className="page-subtitle">Ask questions about products in natural language</p>
            </header>

            {/* Chat Container */}
            <div className="chat-container">
                <div className="chat-messages">
                    {messages.map((msg, index) => (
                        <div key={index} className={`chat-message ${msg.role}`}>
                            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                                {msg.role === 'assistant' && <Bot size={20} style={{ flexShrink: 0, marginTop: '2px' }} />}
                                <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                                {msg.role === 'user' && <User size={20} style={{ flexShrink: 0, marginTop: '2px' }} />}
                            </div>
                        </div>
                    ))}
                    {loading && (
                        <div className="chat-message assistant">
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                <Bot size={20} />
                                <div className="loading-spinner" style={{ width: 20, height: 20 }}></div>
                                <span>Searching...</span>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <div className="chat-input-container">
                    <div className="chat-input-wrapper">
                        <textarea
                            className="chat-input"
                            placeholder="Try: 'Samsung phones under 3000 Dhs' or 'Laptops with discounts'"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={handleKeyPress}
                            rows={1}
                        />
                        <button
                            className="btn btn-primary"
                            onClick={handleSend}
                            disabled={loading || !input.trim()}
                        >
                            <Send size={18} />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Chat
