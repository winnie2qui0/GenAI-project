import { Routes, Route, Link } from 'react-router-dom'
import { ShoppingCart, History, Home as HomeIcon } from 'lucide-react'
import Home from './pages/Home'
import ProcurementDetail from './pages/ProcurementDetail'
import HistoryPage from './pages/History'

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center gap-6 shadow-sm">
        <Link to="/" className="flex items-center gap-2 text-blue-600 font-bold text-lg">
          <ShoppingCart className="w-5 h-5" />
          AI Procurement
        </Link>
        <Link to="/" className="flex items-center gap-1.5 text-gray-600 hover:text-gray-900 text-sm">
          <HomeIcon className="w-4 h-4" />
          New Request
        </Link>
        <Link to="/history" className="flex items-center gap-1.5 text-gray-600 hover:text-gray-900 text-sm">
          <History className="w-4 h-4" />
          History
        </Link>
      </nav>

      <main className="flex-1 container mx-auto px-4 py-8 max-w-6xl">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/procurement/:requestId" element={<ProcurementDetail />} />
          <Route path="/history" element={<HistoryPage />} />
        </Routes>
      </main>

      <footer className="text-center text-xs text-gray-400 py-4 border-t border-gray-100">
        AI-Assisted Procurement System — MVP v1.0
      </footer>
    </div>
  )
}
