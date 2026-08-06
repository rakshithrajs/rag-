import { useRef, useState, useEffect } from 'react'
import { Send } from 'lucide-react'
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
}

export function ChatWindow({ conversation, onAsk, asking }: ChatWindowProps) {
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

      <form
        onSubmit={handleSubmit}
        className="shrink-0 flex items-end gap-2 border-t border-border bg-card p-3"
      >
        <Textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask something grounded in your sources..."
          className="min-h-[60px] flex-1 resize-none"
          rows={2}
        />
        <Button type="submit" disabled={asking || !question.trim()} className="shrink-0">
          <Send className="mr-1 size-4" />
          Send
        </Button>
      </form>
    </>
  )
}
