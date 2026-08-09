import { useState } from 'react'
import { ChevronDown, ChevronUp, FileText, Globe, Info } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import type { SourceChunk } from '@/lib/types'

const typeIcons: Record<string, React.ReactNode> = {
  pdf: <FileText className="size-3.5" />,
  txt: <FileText className="size-3.5" />,
  url: <Globe className="size-3.5" />,
}

interface SourceAttributionProps {
  chunks: SourceChunk[]
}

export function SourceAttribution({ chunks }: SourceAttributionProps) {
  const [open, setOpen] = useState(false)

  if (chunks.length === 0) {
    return (
      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
        <Info className="size-3.5" />
        <span>No sources matched your question.</span>
      </div>
    )
  }

  const sourcesByTitle = new Map<string, number>()
  for (const chunk of chunks) {
    sourcesByTitle.set(chunk.source, (sourcesByTitle.get(chunk.source) ?? 0) + 1)
  }

  return (
    <div className="w-full">
      <div className="flex items-center gap-1.5 text-xs">
        <span className="text-muted-foreground">
          {chunks.length} chunk{chunks.length === 1 ? '' : 's'} from {sourcesByTitle.size} source{sourcesByTitle.size === 1 ? '' : 's'}:
        </span>
        <div className="flex flex-wrap items-center gap-1">
          {Array.from(sourcesByTitle.entries()).map(([title, count]) => (
            <span
              key={title}
              className="inline-flex items-center gap-1 rounded-md border border-border bg-muted px-1.5 py-0.5 text-xs font-medium text-foreground"
            >
              <Globe className="size-3" />
              <span className="max-w-[180px] truncate">{title}</span>
              {count > 1 && <span className="text-muted-foreground">×{count}</span>}
            </span>
          ))}
          <Button
            variant="ghost"
            size="sm"
            className="h-auto px-1 text-xs text-muted-foreground hover:text-foreground"
            onClick={() => setOpen((v) => !v)}
          >
            {open ? <ChevronUp className="size-3.5" /> : <ChevronDown className="size-3.5" />}
            {open ? 'Hide excerpts' : 'Show excerpts'}
          </Button>
        </div>
      </div>
      {open && (
        <ScrollArea className="mt-2 max-h-[min(30vh,240px)] w-full pr-2">
          <div className="flex flex-col gap-2">
            {chunks.map((chunk, idx) => (
              <Card key={idx} className="border-l-4 border-l-primary">
                <CardContent className="space-y-1 p-2">
                  <div className="flex items-center gap-1.5 text-xs font-medium text-foreground">
                    <span className="text-muted-foreground">{typeIcons[chunk.source_type] || <FileText className="size-3.5" />}</span>
                    <span className="truncate">{chunk.source}</span>
                  </div>
                  <p className="text-xs text-muted-foreground line-clamp-3">{chunk.text}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </ScrollArea>
      )}
    </div>
  )
}
