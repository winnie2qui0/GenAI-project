import { Trophy, AlertTriangle, TrendingUp } from 'lucide-react'
import type { RankedListing } from '../services/types'

interface Props {
  topListing: RankedListing
  explanation?: string
}

export default function RecommendationCard({ topListing, explanation }: Props) {
  return (
    <div className="card border-l-4 border-l-yellow-400 space-y-4">
      <div className="flex items-start gap-3">
        <Trophy className="w-6 h-6 text-yellow-500 flex-shrink-0 mt-0.5" />
        <div>
          <h3 className="font-bold text-gray-900 text-lg">Recommended: #{topListing.rank}</h3>
          <p className="text-sm text-gray-600 mt-0.5 line-clamp-2">{topListing.title}</p>
        </div>
        <div className="ml-auto text-right">
          <p className="text-2xl font-bold text-blue-600">{topListing.final_score.toFixed(1)}</p>
          <p className="text-xs text-gray-500">score</p>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-3">
        <ScorePill label="Price" score={topListing.score_breakdown.price_score} />
        <ScorePill label="Delivery" score={topListing.score_breakdown.delivery_score} />
        <ScorePill label="Rating" score={topListing.score_breakdown.rating_score} />
        <ScorePill label="Trust" score={topListing.score_breakdown.trust_score} />
      </div>

      {topListing.anomalies.length > 0 && (
        <div className="space-y-1">
          {topListing.anomalies.map((a, i) => (
            <div
              key={i}
              className={`flex items-start gap-2 text-sm rounded-lg px-3 py-2 ${
                a.severity === 'error'
                  ? 'bg-red-50 text-red-700'
                  : a.severity === 'warning'
                  ? 'bg-yellow-50 text-yellow-700'
                  : 'bg-blue-50 text-blue-700'
              }`}
            >
              <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>{a.message}</span>
            </div>
          ))}
        </div>
      )}

      {explanation && (
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2 text-gray-700">
            <TrendingUp className="w-4 h-4" />
            <span className="text-sm font-semibold">AI Analysis</span>
          </div>
          <div
            className="text-sm text-gray-600 prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{ __html: markdownToHtml(explanation) }}
          />
        </div>
      )}
    </div>
  )
}

function ScorePill({ label, score }: { label: string; score: number }) {
  const color = score >= 75 ? 'bg-green-100 text-green-800' : score >= 50 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
  return (
    <div className={`rounded-lg px-3 py-2 text-center ${color}`}>
      <p className="text-lg font-bold">{score.toFixed(0)}</p>
      <p className="text-xs">{label}</p>
    </div>
  )
}

function markdownToHtml(md: string): string {
  return md
    .replace(/^### (.+)$/gm, '<h3 class="font-semibold mt-3 mb-1">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 class="font-bold mt-4 mb-1">$1</h2>')
    .replace(/^# (.+)$/gm, '<h1 class="font-bold text-lg mt-4 mb-2">$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/^- (.+)$/gm, '<li class="ml-4 list-disc">$1</li>')
    .replace(/\n\n/g, '<br/><br/>')
    .replace(/\n/g, '<br/>')
}
