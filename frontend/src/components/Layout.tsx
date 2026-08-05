import type { ReactNode } from 'react'

export function Layout({ sidebar, children }: { sidebar: ReactNode; children: ReactNode }) {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-background">
      <aside className="flex w-80 flex-col border-r border-border bg-card">{sidebar}</aside>
      <main className="flex flex-1 flex-col overflow-hidden">{children}</main>
    </div>
  )
}
