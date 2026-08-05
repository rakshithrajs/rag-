import { useCallback, useEffect, useState } from 'react'
import { createConversation, getConversation, listConversations } from '@/lib/api'
import type { Conversation, CreateConversationRequest } from '@/lib/types'

export function useConversations() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const fetchConversations = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await listConversations()
      setConversations(data)
    } catch (err) {
      setError(
        err instanceof Error ? err : new Error('Failed to load conversations')
      )
    } finally {
      setLoading(false)
    }
  }, [])

  const addConversation = useCallback(
    async (payload: CreateConversationRequest) => {
      const conversation = await createConversation(payload)
      setConversations((prev) => [conversation, ...prev])
      return conversation
    },
    []
  )

  const refreshConversation = useCallback(async (id: number) => {
    const conversation = await getConversation(id)
    setConversations((prev) =>
      prev.map((c) => (c.id === id ? conversation : c))
    )
    return conversation
  }, [])

  useEffect(() => {
    fetchConversations()
  }, [fetchConversations])

  return {
    conversations,
    loading,
    error,
    refresh: fetchConversations,
    addConversation,
    refreshConversation,
  }
}
