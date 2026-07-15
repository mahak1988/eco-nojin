'use client'
import { UploadCloud, File as FileIcon, X } from 'lucide-react'
import { useState, useRef } from 'react'
import { Button } from '@/components/ui/button'

export function FileUpload({ accept = '*', maxSize = 10, onUpload, label = 'آپلود فایل' }: {
  accept?: string; maxSize?: number; onUpload: (file: File) => Promise<void>; label?: string
}) {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = (f: File) => {
    if (f.size > maxSize * 1024 * 1024) return
    setFile(f)
  }

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)
    try { await onUpload(file); setFile(null) } finally { setLoading(false) }
  }

  return (
    <div className='space-y-3'>
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]) }}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${dragOver ? 'border-green-500 bg-green-500/5' : 'border-border hover:border-green-500/50'}`}
      >
        <UploadCloud className='w-10 h-10 mx-auto mb-3 text-green-500' />
        <p className='text-sm font-medium'>{label}</p>
        <p className='text-xs text-muted-foreground mt-1'>حداکثر {maxSize}MB</p>
        <input ref={inputRef} type='file' accept={accept} className='hidden' onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])} />
      </div>
      {file && (
        <div className='flex items-center justify-between p-3 rounded-lg border border-border bg-muted/30'>
          <div className='flex items-center gap-2'>
            <FileIcon className='w-5 h-5 text-green-500' />
            <div><div className='text-sm font-medium'>{file.name}</div><div className='text-xs text-muted-foreground'>{(file.size / 1024).toFixed(1)} KB</div></div>
          </div>
          <div className='flex gap-2'>
            <Button size='sm' onClick={handleUpload} disabled={loading}>{loading ? 'در حال آپلود...' : 'آپلود'}</Button>
            <Button size='sm' variant='ghost' onClick={() => setFile(null)}><X className='w-4 h-4' /></Button>
          </div>
        </div>
      )}
    </div>
  )
}
