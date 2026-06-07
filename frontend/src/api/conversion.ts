import type { ApiErrorDetail, ConvertPayload, ConvertResponse, SampleResponse } from '../types/conversion'

export class ConversionApiError extends Error {
  hints: string[]

  constructor(detail: ApiErrorDetail | string) {
    const message = typeof detail === 'string' ? detail : detail.message || '转换失败'
    super(message)
    this.name = 'ConversionApiError'
    this.hints = typeof detail === 'string' ? [] : detail.hints || []
  }
}

export async function loadSampleText(): Promise<string> {
  const data = await requestJson<SampleResponse>('/api/sample')
  return data.text
}

export async function convertNovel(payload: ConvertPayload): Promise<ConvertResponse> {
  return requestJson<ConvertResponse>('/api/convert', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

async function requestJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init)
  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new ConversionApiError(data.detail || '请求失败')
  }

  return data as T
}
