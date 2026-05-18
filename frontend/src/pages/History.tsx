import { Clock, ExternalLink } from 'lucide-react'

export default function HistoryPage() {
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Procurement History</h1>

      <div className="card text-center py-12 text-gray-400 space-y-3">
        <Clock className="w-12 h-12 mx-auto opacity-30" />
        <p className="text-sm">History is stored in the audit_log table.</p>
        <p className="text-xs">
          In a future version, this page will display past requests and outcomes.
          <br />
          For now, query the <code className="bg-gray-100 px-1 rounded">audit_log</code> table directly.
        </p>
      </div>
    </div>
  )
}
