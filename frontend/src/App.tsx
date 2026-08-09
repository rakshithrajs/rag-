import { useEffect, useMemo, useState } from 'react'
import { Toaster, toast } from 'sonner'
import { Layout } from '@/components/Layout'
import { ConversationList } from '@/components/ConversationList'
import { SourceList } from '@/components/SourceList'
import { ChatWindow } from '@/components/ChatWindow'
import { UploadSourceDialog } from '@/components/UploadSourceDialog'
import { NewConversationDialog } from '@/components/NewConversationDialog'
import { askQuestion } from '@/lib/api'
import { useConversations } from '@/hooks/useConversations'
import { useSources } from '@/hooks/useSources'
import './index.css'

function App() {
  const {
    conversations,
    addConversation,
    removeConversation,
    refreshConversation,
  } = useConversations()
  const {
    sources,
    refresh: refreshSources,
    addSource,
    removeSource,
    reprocess,
  } = useSources()

  const [selectedId, setSelectedId] = useState<number | undefined>(undefined)
  const [uploadOpen, setUploadOpen] = useState(false)
  const [newConvOpen, setNewConvOpen] = useState(false)
  const [asking, setAsking] = useState(false)

  const selectedConversation = useMemo(
    () => conversations.find((c) => c.id === selectedId) || null,
    [conversations, selectedId]
  )

  const hasReadySources = useMemo(
    () => sources.some((s) => s.status === 'ready'),
    [sources]
  )

  // Poll source statuses while any source is processing.
  useEffect(() => {
    const hasProcessing = sources.some(
      (s) => s.status === 'pending' || s.status === 'processing'
    )
    if (!hasProcessing) return
    const id = setInterval(() => {
      void refreshSources()
    }, 10000)
    return () => clearInterval(id)
  }, [sources, refreshSources])

  const handleNewConversation = async (
    title: string,
    initialQuestion?: string
  ) => {
    try {
      const conversation = await addConversation({ title })
      setSelectedId(conversation.id)
      if (initialQuestion) {
        await handleAsk(conversation.id, initialQuestion)
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to create conversation')
    }
  }

  const handleAsk = async (conversationId: number, question: string) => {
    setAsking(true)
    try {
      await askQuestion(conversationId, { question })
      await refreshConversation(conversationId)
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to get answer')
    } finally {
      setAsking(false)
    }
  }

  const handleUpload = async (formData: FormData) => {
    try {
      await addSource(formData)
      toast.success('Source uploaded and queued for processing')
    } catch (err) {
      throw err instanceof Error ? err : new Error('Failed to upload source')
    }
  }

  const handleDeleteSource = async (id: number) => {
    try {
      await removeSource(id)
      toast.success('Source removed')
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to remove source')
    }
  }

  const handleDeleteConversation = async (id: number) => {
    try {
      await removeConversation(id)
      if (selectedId === id) {
        setSelectedId(undefined)
      }
      toast.success('Conversation deleted')
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to delete conversation')
    }
  }

  const handleReprocess = async (id: number) => {
    try {
      await reprocess(id)
      toast.info('Re-processing queued')
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to requeue source')
    }
  }

  const sidebar = (
    <>
      <div className="border-b border-border p-4">
        <span className="font-semibold">Knowledge Assistant</span>
      </div>
      <SourceList
        sources={sources}
        onUpload={() => setUploadOpen(true)}
        onReprocess={handleReprocess}
        onDelete={handleDeleteSource}
      />
      <ConversationList
        conversations={conversations}
        selectedId={selectedId}
        onSelect={setSelectedId}
        onNew={() => setNewConvOpen(true)}
        onDelete={handleDeleteConversation}
      />
    </>
  )

  return (
    <>
      <Toaster position="top-right" />
      <Layout sidebar={sidebar}>
        <ChatWindow
          conversation={selectedConversation}
          asking={asking}
          hasReadySources={hasReadySources}
          onAsk={async (question) => {
            if (selectedId) {
              await handleAsk(selectedId, question)
            }
          }}
        />
      </Layout>
      <UploadSourceDialog
        open={uploadOpen}
        onOpenChange={setUploadOpen}
        onUpload={handleUpload}
      />
      <NewConversationDialog
        open={newConvOpen}
        onOpenChange={setNewConvOpen}
        onCreate={handleNewConversation}
      />
    </>
  )
}

export default App
