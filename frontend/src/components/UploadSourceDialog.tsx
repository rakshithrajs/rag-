import { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

interface UploadSourceDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onUpload: (formData: FormData) => Promise<void>
}

export function UploadSourceDialog({
  open,
  onOpenChange,
  onUpload,
}: UploadSourceDialogProps) {
  const [title, setTitle] = useState('')
  const [sourceType, setSourceType] = useState('txt')
  const [file, setFile] = useState<File | null>(null)
  const [url, setUrl] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const reset = () => {
    setTitle('')
    setSourceType('txt')
    setFile(null)
    setUrl('')
    setError(null)
  }

  const handleOpenChange = (next: boolean) => {
    if (!next) {
      // Clear form state whenever the dialog is dismissed so the next open
      // doesn't show stale fields or a leftover error message.
      reset()
    }
    onOpenChange(next)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) return
    const formData = new FormData()
    formData.append('title', title.trim())
    formData.append('source_type', sourceType)
    if (sourceType === 'url') {
      if (!url.trim()) return
      formData.append('url', url.trim())
    } else {
      if (!file) return
      formData.append('file', file)
    }
    setSubmitting(true)
    setError(null)
    try {
      await onUpload(formData)
      reset()
      onOpenChange(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload source')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add Knowledge Source</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="source-title">Title</Label>
            <Input
              id="source-title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Annual Report 2025"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="source-type">Source Type</Label>
            <Select
              value={sourceType}
              onValueChange={(value) => value && setSourceType(value)}
            >
              <SelectTrigger id="source-type">
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="pdf">PDF</SelectItem>
                <SelectItem value="txt">Text File</SelectItem>
                <SelectItem value="url">URL</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {sourceType === 'url' ? (
            <div className="space-y-2">
              <Label htmlFor="source-url">URL</Label>
              <Input
                id="source-url"
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com/article"
                required
              />
            </div>
          ) : (
            <div className="space-y-2">
              <Label htmlFor="source-file">File</Label>
              <Input
                id="source-file"
                type="file"
                accept={sourceType === 'pdf' ? '.pdf' : '.txt,.text'}
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                required
              />
            </div>
          )}

          {error && (
            <div
              role="alert"
              className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive"
            >
              {error}
            </div>
          )}

          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => handleOpenChange(false)}
              disabled={submitting}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={submitting}>
              {submitting ? 'Uploading...' : 'Add Source'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
