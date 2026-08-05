import { FileText, Globe, Loader2, RefreshCw, Trash2, Upload } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import type { KnowledgeSource } from '@/lib/types'

const sourceIcons: Record<KnowledgeSource['source_type'], React.ReactNode> = {
  pdf: <FileText className="size-4" />,
  txt: <FileText className="size-4" />,
  url: <Globe className="size-4" />,
}

const statusVariant: Record<KnowledgeSource['status'], 'default' | 'secondary' | 'outline' | 'destructive'> = {
  pending: 'secondary',
  processing: 'secondary',
  ready: 'default',
  error: 'destructive',
}

interface SourceListProps {
  sources: KnowledgeSource[]
  onUpload: () => void
  onReprocess: (id: number) => void
  onDelete: (id: number) => void
}

export function SourceList({ sources, onUpload, onReprocess, onDelete }: SourceListProps) {
  return (
    <div className="flex flex-col gap-2 border-b border-border p-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
          Knowledge Sources
        </h2>
        <Button size="icon" variant="ghost" onClick={onUpload} aria-label="Upload source">
          <Upload className="size-4" />
        </Button>
      </div>
      <ScrollArea className="h-56 pr-2">
        {sources.length === 0 ? (
          <p className="text-sm text-muted-foreground">No sources yet. Add PDFs, text files, or URLs.</p>
        ) : (
          <ul className="flex flex-col gap-2">
            {sources.map((source) => (
              <li
                key={source.id}
                className="flex items-start justify-between gap-2 rounded-lg border border-border bg-background p-2"
              >
                <div className="flex min-w-0 items-center gap-2">
                  <span className="text-muted-foreground">{sourceIcons[source.source_type]}</span>
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium" title={source.title}>
                      {source.title}
                    </p>
                    <Badge variant={statusVariant[source.status]} className="text-xs">
                      {source.status === 'processing' && (
                        <Loader2 className="mr-1 inline size-3 animate-spin" />
                      )}
                      {source.status_display}
                    </Badge>
                  </div>
                </div>
                <div className="flex shrink-0 gap-1">
                  <Button
                    size="icon"
                    variant="ghost"
                    className="size-7"
                    onClick={() => onReprocess(source.id)}
                    aria-label="Reprocess"
                  >
                    <RefreshCw className="size-3.5" />
                  </Button>
                  <Button
                    size="icon"
                    variant="ghost"
                    className="size-7 hover:text-destructive"
                    onClick={() => onDelete(source.id)}
                    aria-label="Delete"
                  >
                    <Trash2 className="size-3.5" />
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </ScrollArea>
    </div>
  )
}
