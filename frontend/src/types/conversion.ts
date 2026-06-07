export type ProviderMode = 'mock' | 'api'
export type DialogueDensity = 'low' | 'medium' | 'high'
export type StageStatus = 'success' | 'warning' | 'error'

export interface StageLog {
  stage: string
  status: StageStatus
  message: string
}

export interface ConvertConfig {
  target_scene_count: number
  dialogue_density: DialogueDensity
  preserve_narration: boolean
}

export interface ConvertPayload {
  text: string
  provider: ProviderMode
  config: ConvertConfig
}

export interface ConvertSummary {
  chapter_count: number
  character_count: number
  scene_count: number
  covered_chapters: string[]
}

export interface ValidationIssue {
  path: string
  message: string
}

export interface ConvertResponse {
  yaml: string
  summary: ConvertSummary
  validation: {
    valid: boolean
    issues: ValidationIssue[]
  }
  stages: StageLog[]
}

export interface ApiErrorDetail {
  code?: string
  message?: string
  stage?: string
  hints?: string[]
}

export interface SampleResponse {
  text: string
}
