export interface KnowledgeSource {
  id: number
  title: string
  source_type: 'pdf' | 'txt' | 'url'
  source_type_display: string
  file?: string
  url?: string
  status: 'pending' | 'processing' | 'ready' | 'error'
  status_display: string
  metadata?: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface SourceChunk {
  source: string
  source_type: string
  source_id?: number
  chunk_index: number
  text: string
}

export interface Message {
  id: number
  role: 'user' | 'assistant'
  role_display: string
  content: string
  source_chunks?: SourceChunk[]
  created_at: string
}

export interface Conversation {
  id: number
  title: string
  messages: Message[]
  created_at: string
  updated_at: string
}

export interface CreateConversationRequest {
  title?: string
  initial_question?: string
}

export interface AskRequest {
  question: string
  output_language?: string
}
