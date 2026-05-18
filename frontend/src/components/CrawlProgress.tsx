import { Loader2, CheckCircle2, XCircle } from 'lucide-react'
import type { StatusResponse } from '../services/types'

interface Props {
  status: StatusResponse
}

const STAGES = ['crawling', 'matching', 'scoring', 'completed'] as const
const STAGE_LABELS: Record<string, string> = {
  pending: 'Waiting to start',
  crawling: 'Crawling platforms',
  matching: 'Matching products',
  scoring: 'Calculating scores',
  completed: 'Done',
  failed: 'Failed',
}

export default function CrawlProgress({ status }: Props) {
  const currentStageIdx = STAGES.indexOf(status.status as typeof STAGES[number])
  const { progress } = status

  return (
    <div className="card space-y-6">
      <div className="flex items-center gap-3">
        {status.status === 'failed' ? (
          <XCircle className="w-6 h-6 text-red-500" />
        ) : status.status === 'completed' ? (
          <CheckCircle2 className="w-6 h-6 text-green-500" />
        ) : (
          <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />
        )}
        <span className="font-semibold text-gray-800">
          {STAGE_LABELS[status.status] ?? status.status}
        </span>
      </div>

      <div className="flex gap-2">
        {STAGES.slice(0, 3).map((stage, idx) => (
          <div key={stage} className="flex-1">
            <div className={`h-2 rounded-full ${
              currentStageIdx > idx
                ? 'bg-green-500'
                : currentStageIdx === idx
                ? 'bg-blue-500 animate-pulse'
                : 'bg-gray-200'
            }`} />
            <p className="text-xs text-gray-500 mt-1 text-center capitalize">{stage}</p>
          </div>
        ))}
      </div>

      {progress && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <Stat label="Platforms" value={`${progress.platforms_crawled ?? 0} / ${progress.total_platforms ?? 4}`} />
          <Stat label="Listings Found" value={progress.listings_found ?? 0} />
          <Stat label="Clusters" value={progress.clusters_created ?? 0} />
          <Stat label="Status" value={STAGE_LABELS[status.status] ?? status.status} />
        </div>
      )}
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-gray-50 rounded-lg p-3">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-lg font-bold text-gray-900">{value}</p>
    </div>
  )
}
