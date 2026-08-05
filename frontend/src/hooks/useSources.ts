import { useCallback, useEffect, useState } from 'react'
import {
  createSource,
  deleteSource,
  listSources,
  reprocessSource,
} from '@/lib/api'
import type { KnowledgeSource } from '@/lib/types'

export function useSources() {
  const [sources, setSources] = useState<KnowledgeSource[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const fetchSources = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await listSources()
      setSources(data)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load sources'))
    } finally {
      setLoading(false)
    }
  }, [])

  const addSource = useCallback(async (formData: FormData) => {
    const source = await createSource(formData)
    setSources((prev) => [source, ...prev])
    return source
  }, [])

  const removeSource = useCallback(async (id: number) => {
    await deleteSource(id)
    setSources((prev) => prev.filter((s) => s.id !== id))
  }, [])

  const reprocess = useCallback(async (id: number) => {
    await reprocessSource(id)
    setSources((prev) =>
      prev.map((s) => (s.id === id ? { ...s, status: 'pending' as const } : s))
    )
  }, [])

  useEffect(() => {
    fetchSources()
  }, [fetchSources])

  return {
    sources,
    loading,
    error,
    refresh: fetchSources,
    addSource,
    removeSource,
    reprocess,
  }
}
