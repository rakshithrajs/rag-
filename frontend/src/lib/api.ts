import axios from 'axios'
import type {
  Conversation,
  CreateConversationRequest,
  KnowledgeSource,
  Message,
  AskRequest,
} from '@/lib/types'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    Accept: 'application/json',
  },
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const responseData = error?.response?.data
    const firstFieldError =
      responseData && typeof responseData === 'object'
        ? Object.values(responseData).flat()[0]
        : null
    const detail =
      firstFieldError ||
      responseData?.detail ||
      responseData?.message ||
      error.message ||
      'Something went wrong'
    return Promise.reject(new Error(detail))
  }
)

interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export async function listSources(): Promise<KnowledgeSource[]> {
  const { data } = await api.get<PaginatedResponse<KnowledgeSource>>(
    '/sources/sources/'
  )
  return data.results
}

export async function createSource(formData: FormData): Promise<KnowledgeSource> {
  const { data } = await api.post<KnowledgeSource>('/sources/sources/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function deleteSource(id: number): Promise<void> {
  await api.delete(`/sources/sources/${id}/`)
}

export async function reprocessSource(id: number): Promise<void> {
  await api.post(`/sources/sources/${id}/reprocess/`)
}

export async function listConversations(): Promise<Conversation[]> {
  const { data } = await api.get<Conversation[]>('/chat/conversations/')
  return data
}

export async function createConversation(
  payload: CreateConversationRequest
): Promise<Conversation> {
  const { data } = await api.post<Conversation>('/chat/conversations/', payload)
  return data
}

export async function getConversation(id: number): Promise<Conversation> {
  const { data } = await api.get<Conversation>(`/chat/conversations/${id}/`)
  return data
}

export async function askQuestion(
  conversationId: number,
  payload: AskRequest
): Promise<Message> {
  const { data } = await api.post<Message>(
    `/chat/conversations/${conversationId}/ask/`,
    payload
  )
  return data
}

export default api
