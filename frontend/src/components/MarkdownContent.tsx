import type { ComponentPropsWithoutRef } from 'react'
import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

import { cn } from '@/lib/utils'

interface MarkdownContentProps {
  content: string
  className?: string
}

/**
 * Render markdown content as React elements.
 *
 * The chat model's responses are untrusted input, so this uses react-markdown,
 * which renders to React elements rather than dangerouslySetInnerHTML and
 * does not inject raw HTML by default. Links open in a new tab with safe rel
 * attributes to avoid reverse-tabnabbing.
 */
export function MarkdownContent({ content, className }: MarkdownContentProps) {
  return (
    <div
      className={cn(
        'text-sm leading-relaxed [&>*:last-child]:mb-0',
        '[&>*]:mt-0',
        className,
      )}
    >
      <Markdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ node: _node, ...props }: ComponentPropsWithoutRef<'h1'> & { node?: unknown }) => (
            <h1 className="mb-2 mt-3 text-base font-semibold first:mt-0" {...props} />
          ),
          h2: ({ node: _node, ...props }: ComponentPropsWithoutRef<'h2'> & { node?: unknown }) => (
            <h2 className="mb-2 mt-3 text-base font-semibold first:mt-0" {...props} />
          ),
          h3: ({ node: _node, ...props }: ComponentPropsWithoutRef<'h3'> & { node?: unknown }) => (
            <h3 className="mb-1 mt-2 text-sm font-semibold first:mt-0" {...props} />
          ),
          p: ({ node: _node, ...props }: ComponentPropsWithoutRef<'p'> & { node?: unknown }) => (
            <p className="mb-2 last:mb-0" {...props} />
          ),
          ul: ({ node: _node, ...props }: ComponentPropsWithoutRef<'ul'> & { node?: unknown }) => (
            <ul className="mb-2 list-disc space-y-1 pl-5 last:mb-0" {...props} />
          ),
          ol: ({ node: _node, ...props }: ComponentPropsWithoutRef<'ol'> & { node?: unknown }) => (
            <ol className="mb-2 list-decimal space-y-1 pl-5 last:mb-0" {...props} />
          ),
          li: ({ node: _node, ...props }: ComponentPropsWithoutRef<'li'> & { node?: unknown }) => (
            <li className="pl-1" {...props} />
          ),
          a: ({ node: _node, ...props }: ComponentPropsWithoutRef<'a'> & { node?: unknown }) => (
            <a
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium underline underline-offset-2 hover:opacity-80"
              {...props}
            />
          ),
          blockquote: ({
            node: _node,
            ...props
          }: ComponentPropsWithoutRef<'blockquote'> & { node?: unknown }) => (
            <blockquote
              className="mb-2 border-l-2 pl-3 italic text-muted-foreground last:mb-0"
              {...props}
            />
          ),
          pre: ({ node: _node, ...props }: ComponentPropsWithoutRef<'pre'> & { node?: unknown }) => (
            <pre
              className="mb-2 overflow-x-auto rounded-md bg-muted p-3 font-mono text-xs last:mb-0"
              {...props}
            />
          ),
          code: ({
            node: _node,
            className: codeClass,
            ...props
          }: ComponentPropsWithoutRef<'code'> & { node?: unknown }) => {
            // Fenced code blocks carry a `language-*` class and are wrapped in a
            // <pre>; inline code has no class. Style them differently.
            if (/language-/.test(codeClass ?? '')) {
              return <code className={codeClass} {...props} />
            }
            return (
              <code
                className="rounded bg-muted px-1.5 py-0.5 font-mono text-[0.85em]"
                {...props}
              />
            )
          },
          table: ({ node: _node, ...props }: ComponentPropsWithoutRef<'table'> & { node?: unknown }) => (
            <div className="mb-2 overflow-x-auto last:mb-0">
              <table className="w-full border-collapse text-xs" {...props} />
            </div>
          ),
          th: ({ node: _node, ...props }: ComponentPropsWithoutRef<'th'> & { node?: unknown }) => (
            <th className="border bg-muted px-2 py-1 text-left font-semibold" {...props} />
          ),
          td: ({ node: _node, ...props }: ComponentPropsWithoutRef<'td'> & { node?: unknown }) => (
            <td className="border px-2 py-1 align-top" {...props} />
          ),
          hr: ({ node: _node, ...props }: ComponentPropsWithoutRef<'hr'> & { node?: unknown }) => (
            <hr className="my-3 border-t" {...props} />
          ),
        }}
      >
        {content}
      </Markdown>
    </div>
  )
}