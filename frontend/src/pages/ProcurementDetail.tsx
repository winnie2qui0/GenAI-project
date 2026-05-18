import { useEffect, useState, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import CrawlProgress from '../components/CrawlProgress'
import ComparisonTable from '../components/ComparisonTable'
import RecommendationCard from '../components/RecommendationCard'
import ReportExport from '../components/ReportExport'
import { getStatus, getResults, recordDecision } from '../services/api'
import type { StatusResponse, ResultsResponse, RankedListing, ClusterResult } from '../services/types'
import { CheckCircle2, RotateCcw, XCircle } from 'lucide-react'

export default function ProcurementDetail() {
  const { requestId } = useParams<{ requestId: string }>()
  const [status, setStatus] = useState<StatusResponse | null>(null)
  const [results, setResults] = useState<ResultsResponse | null>(null)
  const [selectedListing, setSelectedListing] = useState<RankedListing | null>(null)
  const [activeCluster, setActiveCluster] = useState<ClusterResult | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [decided, setDecided] = useState(false)

  const poll = useCallback(async () => {
    if (!requestId) return
    try {
      const s = await getStatus(requestId)
      setStatus(s)
      if (s.status === 'completed') {
        const r = await getResults(requestId)
        setResults(r)
        if (r.clusters[0]) setActiveCluster(r.clusters[0])
      }
    } catch (e) {
      console.error(e)
    }
  }, [requestId])

  useEffect(() => {
    poll()
    const interval = setInterval(() => {
      if (status?.status === 'completed' || status?.status === 'failed') return
      poll()
    }, 3000)
    return () => clearInterval(interval)
  }, [poll, status?.status])

  const handleDecision = async (action: 'accept' | 'override' | 're_search' | 'reject') => {
    if (!requestId) return
    setSubmitting(true)
    try {
      await recordDecision(requestId, action, selectedListing?.listing_id)
      toast.success('Decision recorded!')
      setDecided(true)
    } catch {
      toast.error('Failed to record decision')
    } finally {
      setSubmitting(false)
    }
  }

  if (!status) return <div className="text-center py-20 text-gray-400">Loading…</div>

  const topListing = activeCluster?.ranked_listings[0]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Procurement Results</h1>
          <p className="text-sm text-gray-500 mt-0.5">Request: {requestId}</p>
        </div>
        {results && <ReportExport requestId={requestId!} />}
      </div>

      {status.status !== 'completed' && status.status !== 'failed' && (
        <CrawlProgress status={status} />
      )}

      {status.status === 'failed' && (
        <div className="card bg-red-50 border-red-200 text-red-700">
          Processing failed. Please try again.
        </div>
      )}

      {results && activeCluster && (
        <>
          {results.clusters.length > 1 && (
            <div className="flex gap-2 flex-wrap">
              {results.clusters.map(c => (
                <button
                  key={c.cluster_id}
                  onClick={() => { setActiveCluster(c); setSelectedListing(null) }}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    activeCluster.cluster_id === c.cluster_id
                      ? 'bg-blue-600 text-white'
                      : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {c.canonical_name.slice(0, 40)}
                  <span className={`ml-2 text-xs px-1.5 py-0.5 rounded-full ${
                    c.confidence === 'HIGH' ? 'badge-high' : c.confidence === 'MEDIUM' ? 'badge-medium' : 'badge-low'
                  }`}>{c.confidence}</span>
                </button>
              ))}
            </div>
          )}

          {topListing && (
            <RecommendationCard
              topListing={topListing}
              explanation={topListing.llm_explanation}
            />
          )}

          <div className="card space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold text-gray-900">All Listings — {activeCluster.canonical_name}</h2>
              <span className="text-sm text-gray-500">{activeCluster.ranked_listings.length} results</span>
            </div>
            <ComparisonTable
              listings={activeCluster.ranked_listings}
              onSelect={setSelectedListing}
              selectedId={selectedListing?.listing_id}
            />
          </div>

          {!decided && (
            <div className="card space-y-4">
              <h2 className="font-semibold text-gray-900">Make Your Decision</h2>
              {selectedListing && (
                <p className="text-sm text-gray-600">
                  Selected: <strong>{selectedListing.title}</strong> (Rank #{selectedListing.rank})
                </p>
              )}
              <div className="flex flex-wrap gap-3">
                <button
                  onClick={() => handleDecision('accept')}
                  disabled={submitting || !selectedListing}
                  className="btn-primary flex items-center gap-2"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  Accept Recommendation
                </button>
                <button
                  onClick={() => handleDecision('override')}
                  disabled={submitting || !selectedListing}
                  className="btn-secondary flex items-center gap-2"
                >
                  Override &amp; Select
                </button>
                <button
                  onClick={() => handleDecision('re_search')}
                  disabled={submitting}
                  className="btn-secondary flex items-center gap-2"
                >
                  <RotateCcw className="w-4 h-4" />
                  Re-search
                </button>
                <button
                  onClick={() => handleDecision('reject')}
                  disabled={submitting}
                  className="btn-secondary flex items-center gap-2 text-red-600"
                >
                  <XCircle className="w-4 h-4" />
                  Reject All
                </button>
              </div>
            </div>
          )}

          {decided && (
            <div className="card bg-green-50 border-green-200 flex items-center gap-3 text-green-700">
              <CheckCircle2 className="w-5 h-5" />
              Decision recorded to audit log. You can export the report above.
            </div>
          )}
        </>
      )}
    </div>
  )
}
