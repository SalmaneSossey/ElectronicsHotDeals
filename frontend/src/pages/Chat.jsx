import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, AlertCircle } from 'lucide-react'

function Chat() {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'Hello! I can help you find the best electronics deals. Ask me about specific products, brands, or price ranges. For example: "What are the best TVs under 5000 Dhs?" or "Show me Samsung smartphones"' }
    ])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [apiKey, setApiKey] = useState('')
    const [showApiInput, setShowApiInput] = useState(true)
    const messagesEndRef = useRef(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const handleSend = async () => {
        if (!input.trim() || loading) return
        if (!apiKey) {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: '⚠️ Please enter your Google Gemini API key above to enable AI chat.'
            }])
            return
        }

        const userMessage = input.trim()
        setInput('')
        setMessages(prev => [...prev, { role: 'user', content: userMessage }])
        setLoading(true)

        try {
            // Fetch products for context
            const productsRes = await fetch('/api/products?per_page=200')
            const productsData = productsRes.ok ? await productsRes.json() : { products: [] }

            // Create context from products
            const context = productsData.products.slice(0, 100).map(p =>
                `${p.title} | ${p.brand} | ${p.price_numeric} Dhs | ${p.category} | ${p.discount_percentage || 0}% off`
            ).join('\n')

            // Call Gemini API directly
            const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    contents: [{
                        parts: [{
                            text: `You are an expert electronics shopping assistant for Morocco. Use ONLY the following product data to answer questions. If the data doesn't contain the answer, say so politely. Format prices in Dhs. Be concise but helpful.

PRODUCT DATA:
${context}

USER QUESTION: ${userMessage}

Provide a helpful, concise answer based only on the product data above.`
                        }]
                    }]
                })
            })

            if (!response.ok) {
                throw new Error('Failed to get response from Gemini')
            }

            const data = await response.json()
            const aiResponse = data.candidates?.[0]?.content?.parts?.[0]?.text || 'Sorry, I could not generate a response.'

            setMessages(prev => [...prev, { role: 'assistant', content: aiResponse }])
        } catch (err) {
            console.error('Chat error:', err)
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: '❌ Error: Could not get a response. Please check your API key and try again.'
            }])
        } finally {
            setLoading(false)
        }
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
                    <Bot style={{ display: 'inline', marginRight: '0.5rem', color: 'var(--accent-primary)' }} />
                    AI Shopping Assistant
                </h1>
                <p className="page-subtitle">Ask questions about products using natural language</p>
            </header>

            {/* API Key Input */}
            {showApiInput && (
                <div className="glass-card" style={{ marginBottom: '1rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    <AlertCircle size={20} style={{ color: 'var(--warning)', flexShrink: 0 }} />
                    <input
                        type="password"
                        className="filter-input"
                        placeholder="Enter your Google Gemini API key..."
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        style={{ flex: 1 }}
                    />
                    <button
                        className="btn btn-secondary"
                        onClick={() => apiKey && setShowApiInput(false)}
                        disabled={!apiKey}
                    >
                        Save
                    </button>
                </div>
            )}

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
                                <span>Thinking...</span>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <div className="chat-input-container">
                    <div className="chat-input-wrapper">
                        <textarea
                            className="chat-input"
                            placeholder="Ask about products... (e.g., 'Best laptops under 8000 Dhs')"
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
