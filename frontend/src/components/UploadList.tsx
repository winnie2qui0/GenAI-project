import { Package, DollarSign, Clock, Hash } from 'lucide-react'
import type { ProcurementItem } from '../services/types'

interface Props {
  items: ProcurementItem[]
}

export default function UploadList({ items }: Props) {
  if (!items.length) return null

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide">Extracted Items</h3>
      {items.map((item, i) => (
        <div key={i} className="bg-gray-50 rounded-lg px-4 py-3 flex flex-wrap gap-4 text-sm">
          <div className="flex items-center gap-1.5 font-medium text-gray-900">
            <Package className="w-4 h-4 text-blue-500" />
            {item.product_name}
          </div>
          {item.brand && <span className="text-gray-500">Brand: <strong>{item.brand}</strong></span>}
          {item.model && <span className="text-gray-500">Model: <strong>{item.model}</strong></span>}
          <div className="flex items-center gap-1 text-gray-500">
            <Hash className="w-3.5 h-3.5" />
            {item.quantity} units
          </div>
          {item.max_price && (
            <div className="flex items-center gap-1 text-gray-500">
              <DollarSign className="w-3.5 h-3.5" />
              Max ${item.max_price}
            </div>
          )}
          {item.max_lead_time_days && (
            <div className="flex items-center gap-1 text-gray-500">
              <Clock className="w-3.5 h-3.5" />
              {item.max_lead_time_days}d max
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
