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
import { Textarea } from '@/components/ui/textarea'

interface NewConversationDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onCreate: (title: string, initialQuestion?: string) => Promise<void>
}

export function NewConversationDialog({
  open,
  onOpenChange,
  onCreate,
}: NewConversationDialogProps) {
  const [title, setTitle] = useState('')
  const [initialQuestion, setInitialQuestion] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const trimmedTitle = title.trim() || undefined
    const trimmedQuestion = initialQuestion.trim() || undefined
    setSubmitting(true)
    try {
      await onCreate(trimmedTitle || 'New conversation', trimmedQuestion)
      setTitle('')
      setInitialQuestion('')
      onOpenChange(false)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>New Conversation</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="conv-title">Title</Label>
            <Input
              id="conv-title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Q3 planning questions"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="conv-question">Initial question (optional)</Label>
            <Textarea
              id="conv-question"
              value={initialQuestion}
              onChange={(e) => setInitialQuestion(e.target.value)}
              placeholder="Ask your first question..."
              rows={3}
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={submitting}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={submitting}>
              {submitting ? 'Creating...' : 'Start Conversation'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
