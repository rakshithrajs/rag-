import type { ReactNode } from 'react'

export function Layout({ sidebar, children }: { sidebar: ReactNode; children: ReactNode }) {
  return (
    <div className="flex h-dvh w-full overflow-hidden bg-background">
      <aside className="flex h-full w-80 shrink-0 flex-col border-r border-border bg-card">
        {sidebar}
      </aside>
      <main className="flex h-full min-h-0 flex-1 flex-col overflow-hidden">
        {children}
      </main>
    </div>
  )
}
