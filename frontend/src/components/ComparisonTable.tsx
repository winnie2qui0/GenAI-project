import { ExternalLink, AlertTriangle, Info } from 'lucide-react'
import type { RankedListing, AnomalyFlag } from '../services/types'

interface Props {
  listings: RankedListing[]
  onSelect: (listing: RankedListing) => void
  selectedId?: string
}

export default function ComparisonTable({ listings, onSelect, selectedId }: Props) {
  return (
    <div className="overflow-x-auto rounded-xl border border-gray-200">
      <table className="min-w-full text-sm">
        <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
          <tr>
            <th className="px-4 py-3 text-left">Rank</th>
            <th className="px-4 py-3 text-left">Product</th>
            <th className="px-4 py-3 text-left">Source</th>
            <th className="px-4 py-3 text-right">Price (USD)</th>
            <th className="px-4 py-3 text-right">Lead Days</th>
            <th className="px-4 py-3 text-right">Rating</th>
            <th className="px-4 py-3 text-right">Score</th>
            <th className="px-4 py-3 text-center">Flags</th>
            <th className="px-4 py-3 text-center">Select</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 bg-white">
          {listings.map(l => (
            <tr
              key={l.listing_id}
              className={`hover:bg-blue-50 transition-colors ${selectedId === l.listing_id ? 'bg-blue-50 ring-2 ring-inset ring-blue-400' : ''}`}
            >
              <td className="px-4 py-3">
                <RankBadge rank={l.rank} />
              </td>
              <td className="px-4 py-3 max-w-xs">
                <a href={l.url} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline flex items-start gap-1">
                  <span className="line-clamp-2">{l.title}</span>
                  <ExternalLink className="w-3 h-3 mt-0.5 flex-shrink-0" />
                </a>
              </td>
              <td className="px-4 py-3 capitalize">{l.source.replace('_', ' ')}</td>
              <td className="px-4 py-3 text-right font-medium">
                ${l.price_usd?.toFixed(2) ?? l.price.toFixed(2)}
              </td>
              <td className="px-4 py-3 text-right">{l.delivery_days ?? '?'}</td>
              <td className="px-4 py-3 text-right">
                {l.rating ? `${l.rating.toFixed(1)} ★` : '—'}
                {l.review_count ? <span className="text-gray-400 text-xs ml-1">({l.review_count})</span> : null}
              </td>
              <td className="px-4 py-3 text-right">
                <ScoreBar score={l.final_score} />
              </td>
              <td className="px-4 py-3 text-center">
                <AnomalyBadges anomalies={l.anomalies} />
              </td>
              <td className="px-4 py-3 text-center">
                <button
                  onClick={() => onSelect(l)}
                  className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                    selectedId === l.listing_id
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {selectedId === l.listing_id ? 'Selected' : 'Select'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function RankBadge({ rank }: { rank: number }) {
  const colors: Record<number, string> = {
    1: 'bg-yellow-400 text-yellow-900',
    2: 'bg-gray-300 text-gray-700',
    3: 'bg-amber-600 text-white',
  }
  return (
    <span className={`inline-flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold ${colors[rank] ?? 'bg-gray-100 text-gray-600'}`}>
      {rank}
    </span>
  )
}

function ScoreBar({ score }: { score: number }) {
  const color = score >= 75 ? 'bg-green-500' : score >= 50 ? 'bg-yellow-500' : 'bg-red-400'
  return (
    <div className="flex items-center gap-2 justify-end">
      <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${score}%` }} />
      </div>
      <span className="font-medium text-gray-800 w-8 text-right">{score.toFixed(0)}</span>
    </div>
  )
}

function AnomalyBadges({ anomalies }: { anomalies: AnomalyFlag[] }) {
  if (!anomalies.length) return <span className="text-gray-300">—</span>
  const errors = anomalies.filter(a => a.severity === 'error').length
  const warnings = anomalies.filter(a => a.severity === 'warning').length
  return (
    <div className="flex items-center justify-center gap-1">
      {errors > 0 && (
        <span title="Errors" className="flex items-center gap-0.5 text-red-600">
          <AlertTriangle className="w-3.5 h-3.5" />
          <span className="text-xs">{errors}</span>
        </span>
      )}
      {warnings > 0 && (
        <span title="Warnings" className="flex items-center gap-0.5 text-yellow-600">
          <AlertTriangle className="w-3.5 h-3.5" />
          <span className="text-xs">{warnings}</span>
        </span>
      )}
      {!errors && !warnings && anomalies.length > 0 && (
        <Info className="w-3.5 h-3.5 text-blue-400" />
      )}
    </div>
  )
}
