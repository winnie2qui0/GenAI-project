import { FileDown, FileSpreadsheet } from 'lucide-react'
import { getExportUrl } from '../services/api'

interface Props {
  requestId: string
}

export default function ReportExport({ requestId }: Props) {
  return (
    <div className="flex gap-3">
      <a
        href={getExportUrl(requestId, 'excel')}
        download
        className="btn-secondary flex items-center gap-2 text-sm"
      >
        <FileSpreadsheet className="w-4 h-4 text-green-600" />
        Export Excel
      </a>
      <a
        href={getExportUrl(requestId, 'pdf')}
        download
        className="btn-secondary flex items-center gap-2 text-sm"
      >
        <FileDown className="w-4 h-4 text-red-500" />
        Export PDF
      </a>
    </div>
  )
}
