import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import ProcurementForm from '../components/ProcurementForm'
import UploadList from '../components/UploadList'
import ParamConfirmation from '../components/ParamConfirmation'
import { createRequest, confirmRequest } from '../services/api'
import type { ProcurementItem, ProcurementRequestResponse } from '../services/types'

type Stage = 'input' | 'confirm'

export default function Home() {
  const navigate = useNavigate()
  const [stage, setStage] = useState<Stage>('input')
  const [loading, setLoading] = useState(false)
  const [request, setRequest] = useState<ProcurementRequestResponse | null>(null)

  const handleSubmit = async (inputText: string, file?: File) => {
    setLoading(true)
    try {
      const res = await createRequest(inputText, file)
      setRequest(res)
      setStage('confirm')
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Unknown error'
      toast.error(`Failed to create request: ${msg}`)
    } finally {
      setLoading(false)
    }
  }

  const handleConfirm = async (items: ProcurementItem[]) => {
    if (!request) return
    setLoading(true)
    try {
      await confirmRequest(request.request_id, items)
      navigate(`/procurement/${request.request_id}`)
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Unknown error'
      toast.error(`Failed to start search: ${msg}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-gray-900">AI Procurement Assistant</h1>
        <p className="text-gray-500">Describe what you need — we'll find the best prices across platforms.</p>
      </div>

      <div className="card">
        {stage === 'input' ? (
          <ProcurementForm onSubmit={handleSubmit} loading={loading} />
        ) : (
          <div className="space-y-6">
            <UploadList items={request?.parsed_items ?? []} />
            <ParamConfirmation
              items={request?.parsed_items ?? []}
              onConfirm={handleConfirm}
              loading={loading}
            />
          </div>
        )}
      </div>

      <div className="card bg-blue-50 border-blue-200">
        <h2 className="font-semibold text-blue-900 mb-3">How it works</h2>
        <ol className="space-y-2 text-sm text-blue-800">
          {[
            'Describe your need or upload an Excel list',
            'AI extracts and confirms the requirements',
            'We crawl Amazon, Alibaba, PChome + local B2B',
            'Products are matched and scored deterministically',
            'Review the ranked comparison and export',
          ].map((step, i) => (
            <li key={i} className="flex gap-3">
              <span className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-600 text-white text-xs flex items-center justify-center font-bold">
                {i + 1}
              </span>
              {step}
            </li>
          ))}
        </ol>
      </div>
    </div>
  )
}
