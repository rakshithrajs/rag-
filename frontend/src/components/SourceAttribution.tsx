import { useState } from 'react'
import { ChevronDown, ChevronUp, FileText, Globe } from 'lucide-react'
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

  return (
    <div className="w-full">
      <Button
        variant="ghost"
        size="sm"
        className="h-auto gap-1 p-0 text-xs text-muted-foreground hover:text-foreground"
        onClick={() => setOpen((v) => !v)}
      >
        {open ? <ChevronUp className="size-3.5" /> : <ChevronDown className="size-3.5" />}
        {chunks.length} source{chunks.length === 1 ? '' : 's'} used
      </Button>
      {open && (
        <ScrollArea className="mt-2 max-h-[40vh] pr-2">
          <div className="flex flex-col gap-2">
            {chunks.map((chunk, idx) => (
              <Card key={idx} className="border-l-4 border-l-primary">
                <CardContent className="space-y-1 p-2">
                  <div className="flex items-center gap-1.5 text-xs font-medium text-foreground">
                    <span className="text-muted-foreground">{typeIcons[chunk.source_type] || <FileText className="size-3.5" />}</span>
                    {chunk.source}
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
