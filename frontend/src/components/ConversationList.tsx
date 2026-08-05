import { MessageSquare, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import type { Conversation } from '@/lib/types'

interface ConversationListProps {
  conversations: Conversation[]
  selectedId?: number
  onSelect: (id: number) => void
  onNew: () => void
}

export function ConversationList({
  conversations,
  selectedId,
  onSelect,
  onNew,
}: ConversationListProps) {
  return (
    <div className="flex flex-1 flex-col gap-2 overflow-hidden p-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
          Conversations
        </h2>
        <Button size="icon" variant="ghost" onClick={onNew} aria-label="New conversation">
          <Plus className="size-4" />
        </Button>
      </div>
      <ScrollArea className="flex-1 pr-2">
        {conversations.length === 0 ? (
          <p className="text-sm text-muted-foreground">Start a new conversation to ask questions.</p>
        ) : (
          <ul className="flex flex-col gap-1">
            {conversations.map((conversation) => (
              <li key={conversation.id}>
                <Button
                  variant={selectedId === conversation.id ? 'secondary' : 'ghost'}
                  className="h-auto w-full justify-start gap-2 px-2 py-2 font-normal"
                  onClick={() => onSelect(conversation.id)}
                >
                  <MessageSquare className="size-4 shrink-0 text-muted-foreground" />
                  <span className="truncate text-sm">
                    {conversation.title || `Conversation ${conversation.id}`}
                  </span>
                </Button>
              </li>
            ))}
          </ul>
        )}
      </ScrollArea>
    </div>
  )
}
