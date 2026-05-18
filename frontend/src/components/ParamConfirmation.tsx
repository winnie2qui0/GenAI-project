import React, { useState } from 'react'
import { CheckCircle, Edit2 } from 'lucide-react'
import type { ProcurementItem } from '../services/types'

interface Props {
  items: ProcurementItem[]
  onConfirm: (items: ProcurementItem[]) => void
  loading?: boolean
}

export default function ParamConfirmation({ items, onConfirm, loading }: Props) {
  const [editableItems, setEditableItems] = useState<ProcurementItem[]>(
    items.map(i => ({ ...i }))
  )

  const update = (idx: number, field: keyof ProcurementItem, value: string | number) => {
    setEditableItems(prev => {
      const next = [...prev]
      next[idx] = { ...next[idx], [field]: value }
      return next
    })
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-blue-700 bg-blue-50 rounded-lg p-3">
        <Edit2 className="w-4 h-4 flex-shrink-0" />
        <p className="text-sm">Review and adjust the extracted parameters before we start searching.</p>
      </div>

      {editableItems.map((item, idx) => (
        <div key={idx} className="card">
          <h3 className="font-semibold text-gray-900 mb-4">{item.product_name}</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <Field label="Brand" value={item.brand ?? ''} onChange={v => update(idx, 'brand', v)} />
            <Field label="Model" value={item.model ?? ''} onChange={v => update(idx, 'model', v)} />
            <Field label="Quantity" type="number" value={String(item.quantity)} onChange={v => update(idx, 'quantity', Number(v))} />
            <Field label="Max Price (USD)" type="number" value={String(item.max_price ?? '')} onChange={v => update(idx, 'max_price', Number(v))} />
            <Field label="Max Lead Days" type="number" value={String(item.max_lead_time_days ?? '')} onChange={v => update(idx, 'max_lead_time_days', Number(v))} />
            <Field label="Min Order Qty" type="number" value={String(item.moq_acceptable)} onChange={v => update(idx, 'moq_acceptable', Number(v))} />
          </div>
        </div>
      ))}

      <button
        onClick={() => onConfirm(editableItems)}
        disabled={loading}
        className="btn-primary w-full flex items-center justify-center gap-2 py-3"
      >
        <CheckCircle className="w-4 h-4" />
        {loading ? 'Starting search…' : 'Confirm & Start Search'}
      </button>
    </div>
  )
}

function Field({
  label, value, onChange, type = 'text',
}: {
  label: string; value: string; onChange: (v: string) => void; type?: string
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-gray-500 mb-1">{label}</label>
      <input
        type={type}
        value={value}
        onChange={e => onChange(e.target.value)}
        className="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-1 focus:ring-blue-500"
      />
    </div>
  )
}
