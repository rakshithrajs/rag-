import { Bot, User } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import type { Message } from '@/lib/types'
import { SourceAttribution } from './SourceAttribution'

interface MessageBubbleProps {
  message: Message
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'

  return (
    <div
      className={`flex w-full gap-3 ${
        isUser ? 'flex-row-reverse' : 'flex-row'
      }`}
    >
      <div
        className={`flex size-8 shrink-0 items-center justify-center rounded-full ${
          isUser ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'
        }`}
      >
        {isUser ? <User className="size-4" /> : <Bot className="size-4" />}
      </div>
      <div className={`flex min-w-0 max-w-[80%] flex-1 flex-col gap-2 ${isUser ? 'items-end' : 'items-start'}`}>
        <Card className={isUser ? 'bg-primary text-primary-foreground' : 'bg-card'}>
          <CardContent className="p-3">
            <p className="whitespace-pre-wrap text-sm">{message.content}</p>
          </CardContent>
        </Card>
        {!isUser && message.source_chunks && (
          <SourceAttribution chunks={message.source_chunks} />
        )}
      </div>
    </div>
  )
}
