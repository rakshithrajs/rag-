import { useRef, useState, useEffect } from 'react'
import { Send, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Textarea } from '@/components/ui/textarea'
import { Skeleton } from '@/components/ui/skeleton'
import type { Conversation } from '@/lib/types'
import { MessageBubble } from './MessageBubble'

interface ChatWindowProps {
  conversation: Conversation | null
  onAsk: (question: string) => Promise<void>
  asking: boolean
  hasReadySources: boolean
}

export function ChatWindow({ conversation, onAsk, asking, hasReadySources }: ChatWindowProps) {
  const [question, setQuestion] = useState('')
  const viewportRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const viewport = viewportRef.current
    if (viewport) {
      viewport.scrollTop = viewport.scrollHeight
    }
  }, [conversation?.messages, asking])

  const submitQuestion = async () => {
    if (!question.trim() || asking) return
    const q = question.trim()
    setQuestion('')
    await onAsk(q)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    void submitQuestion()
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      void submitQuestion()
    }
  }

  if (!conversation) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center text-muted-foreground">
        <p className="text-lg font-medium">Welcome to your Knowledge Assistant</p>
        <p className="text-sm">Create a conversation or select one to start asking questions.</p>
      </div>
    )
  }

  return (
    <>
      <div className="shrink-0 border-b border-border px-4 py-3">
        <h1 className="font-semibold text-foreground">
          {conversation.title || `Conversation ${conversation.id}`}
        </h1>
        <p className="text-xs text-muted-foreground">
          {conversation.messages.length} message{conversation.messages.length === 1 ? '' : 's'}
        </p>
      </div>

      <ScrollArea className="min-h-0 flex-1 px-4 py-4" viewportRef={viewportRef}>
        <div className="flex flex-col gap-6">
          {conversation.messages.map((message, idx) => (
            <MessageBubble key={`${message.id}-${idx}`} message={message} />
          ))}
          {asking && (
            <div className="flex gap-3">
              <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-muted text-muted-foreground">
                <Send className="size-4" />
              </div>
              <div className="flex flex-col gap-2">
                <Skeleton className="h-4 w-48" />
                <Skeleton className="h-4 w-32" />
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      <div className="shrink-0 border-t border-border bg-card p-3">
        {!hasReadySources && (
          <div className="mb-2 flex items-center gap-2 rounded-md bg-amber-50 px-3 py-2 text-xs text-amber-800 dark:bg-amber-950 dark:text-amber-200">
            <AlertCircle className="size-4 shrink-0" />
            <span>No ready sources yet. Upload a source and wait for it to finish processing before asking questions.</span>
          </div>
        )}
        <form onSubmit={handleSubmit} className="flex items-end gap-2">
          <Textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              hasReadySources
                ? 'Ask something grounded in your sources...'
                : 'Add a ready source first...'
            }
            className="min-h-[60px] flex-1 resize-none"
            rows={2}
            disabled={!hasReadySources}
          />
          <Button
            type="submit"
            disabled={asking || !question.trim() || !hasReadySources}
            className="shrink-0"
          >
            <Send className="mr-1 size-4" />
            Send
          </Button>
        </form>
      </div>
    </>
  )
}
