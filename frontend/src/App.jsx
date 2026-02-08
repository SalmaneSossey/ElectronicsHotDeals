import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import Products from './pages/Products'
import Analytics from './pages/Analytics'
import Chat from './pages/Chat'

function App() {
    return (
        <BrowserRouter>
            <div className="app-container">
                <Navbar />
                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/products" element={<Products />} />
                        <Route path="/analytics" element={<Analytics />} />
                        <Route path="/chat" element={<Chat />} />
                    </Routes>
                </main>
            </div>
        </BrowserRouter>
    )
}

export default App
