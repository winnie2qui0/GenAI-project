import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Send, Upload, FileSpreadsheet, X } from 'lucide-react'

interface Props {
  onSubmit: (inputText: string, file?: File) => void
  loading?: boolean
}

export default function ProcurementForm({ onSubmit, loading }: Props) {
  const [text, setText] = useState('')
  const [file, setFile] = useState<File | null>(null)

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted[0]) setFile(accepted[0])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'], 'text/csv': ['.csv'] },
    maxFiles: 1,
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!text.trim() && !file) return
    onSubmit(text, file ?? undefined)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1.5">
          Describe your procurement need
        </label>
        <textarea
          value={text}
          onChange={e => setText(e.target.value)}
          placeholder="Example: I need 500 HP toner cartridges CF410A, budget $40 each, 2 days delivery"
          className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows={4}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1.5">
          Or upload Excel / CSV
        </label>
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
            isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <input {...getInputProps()} />
          {file ? (
            <div className="flex items-center justify-center gap-2 text-green-600">
              <FileSpreadsheet className="w-5 h-5" />
              <span className="text-sm font-medium">{file.name}</span>
              <button
                type="button"
                onClick={e => { e.stopPropagation(); setFile(null) }}
                className="ml-2 text-gray-400 hover:text-gray-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2 text-gray-500">
              <Upload className="w-8 h-8" />
              <span className="text-sm">Drop .xlsx or .csv here, or click to browse</span>
            </div>
          )}
        </div>
      </div>

      <button
        type="submit"
        disabled={loading || (!text.trim() && !file)}
        className="btn-primary w-full flex items-center justify-center gap-2 py-3"
      >
        <Send className="w-4 h-4" />
        {loading ? 'Submitting…' : 'Start Comparison'}
      </button>
    </form>
  )
}
