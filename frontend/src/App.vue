<script setup lang="ts">
import { computed, ref } from 'vue'

type ProviderMode = 'mock' | 'api'
type DialogueDensity = 'low' | 'medium' | 'high'

interface StageLog {
  stage: string
  status: 'success' | 'warning' | 'error'
  message: string
}

interface ApiErrorDetail {
  message?: string
  hints?: string[]
}

interface ConvertResponse {
  yaml: string
  summary: {
    chapter_count: number
    character_count: number
    scene_count: number
    covered_chapters: string[]
  }
  validation: {
    valid: boolean
    issues: Array<{ path: string; message: string }>
  }
  stages: StageLog[]
}

const novelText = ref('')
const provider = ref<ProviderMode>('mock')
const targetSceneCount = ref(6)
const dialogueDensity = ref<DialogueDensity>('medium')
const preserveNarration = ref(true)
const loading = ref(false)
const result = ref<ConvertResponse | null>(null)
const error = ref('')
const errorHints = ref<string[]>([])
const copyLabel = ref('复制')

const chapterCount = computed(() => {
  const matches = novelText.value.match(/^(?:\s*(?:第[零一二三四五六七八九十百千万\d]+章|Chapter\s+\d+|#{1,3}\s+))/gim)
  return matches?.length ?? 0
})

const chapterState = computed(() => {
  if (!novelText.value.trim()) return '等待输入'
  return chapterCount.value >= 3 ? '章节达标' : '至少需要 3 章'
})

const canConvert = computed(() => novelText.value.trim().length > 0 && !loading.value)

const visibleStages = computed<StageLog[]>(() => {
  if (result.value) return result.value.stages
  if (!loading.value) return []
  return [
    {
      stage: 'pipeline',
      status: 'warning',
      message: '后端正在解析章节、改编分场并校验 YAML。',
    },
  ]
})

const coveredChapters = computed(() => result.value?.summary.covered_chapters.join('、') || '生成后显示')

async function loadSample() {
  resetFeedback()
  try {
    const response = await fetch('/api/sample')
    if (!response.ok) throw new Error('样例加载失败')
    const data = await response.json()
    novelText.value = data.text
  } catch (err) {
    error.value = err instanceof Error ? err.message : '样例加载失败'
  }
}

async function convert() {
  if (!canConvert.value) return
  loading.value = true
  resetFeedback()
  result.value = null
  try {
    const response = await fetch('/api/convert', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: novelText.value,
        provider: provider.value,
        config: {
          target_scene_count: targetSceneCount.value,
          dialogue_density: dialogueDensity.value,
          preserve_narration: preserveNarration.value,
        },
      }),
    })
    const data = await response.json()
    if (!response.ok) {
      const detail = data.detail as ApiErrorDetail
      error.value = detail?.message ?? '转换失败'
      errorHints.value = detail?.hints ?? []
      return
    }
    result.value = data
  } catch (err) {
    error.value = err instanceof Error ? err.message : '网络请求失败'
  } finally {
    loading.value = false
  }
}

async function copyYaml() {
  if (!result.value) return
  await navigator.clipboard.writeText(result.value.yaml)
  copyLabel.value = '已复制'
  window.setTimeout(() => {
    copyLabel.value = '复制'
  }, 1600)
}

function downloadYaml() {
  if (!result.value) return
  const blob = new Blob([result.value.yaml], { type: 'text/yaml;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'screenplay.yaml'
  link.click()
  URL.revokeObjectURL(url)
}

function resetFeedback() {
  error.value = ''
  errorHints.value = []
}
</script>

<template>
  <a class="skip-link" href="#workspace">跳到转换工作区</a>
  <main class="app-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">XEngineer · 第三批次题目三</p>
        <h1>AI 小说转剧本工具</h1>
      </div>
      <div class="tech-tags" aria-label="技术栈">
        <span>Vue</span>
        <span>FastAPI</span>
        <span>YAML Schema</span>
      </div>
    </header>

    <section id="workspace" class="workspace" aria-label="小说转剧本工作区">
      <aside class="input-panel" aria-labelledby="inputTitle">
        <div class="panel-head">
          <div>
            <h2 id="inputTitle">小说输入</h2>
            <p class="panel-subtitle">{{ chapterState }}</p>
          </div>
          <button class="ghost-button icon-button" type="button" @click="loadSample">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M4 4h16v16H4z" />
              <path d="M8 8h8M8 12h8M8 16h5" />
            </svg>
            载入样例
          </button>
        </div>

        <label class="field-label" for="novelText">小说文本</label>
        <textarea
          id="novelText"
          v-model="novelText"
          class="novel-input"
          spellcheck="false"
          placeholder="粘贴至少 3 个章节的小说文本"
        />

        <div class="metrics-row" aria-live="polite">
          <span :class="['metric', chapterCount >= 3 ? 'ok' : 'warn']">{{ chapterCount || '未识别' }} 章</span>
          <span class="metric">{{ novelText.length }} 字符</span>
          <span class="metric">覆盖：{{ coveredChapters }}</span>
        </div>

        <div class="control-grid">
          <label>
            <span>生成模式</span>
            <select v-model="provider">
              <option value="mock">Mock 演示</option>
              <option value="api">API 生成</option>
            </select>
          </label>

          <label>
            <span>场次数量</span>
            <input v-model.number="targetSceneCount" type="number" min="3" max="12" inputmode="numeric" />
          </label>

          <label>
            <span>对白密度</span>
            <select v-model="dialogueDensity">
              <option value="low">低</option>
              <option value="medium">中</option>
              <option value="high">高</option>
            </select>
          </label>

          <label class="toggle-row">
            <input v-model="preserveNarration" type="checkbox" />
            <span>保留旁白</span>
          </label>
        </div>

        <button
          class="primary-button icon-button"
          type="button"
          :disabled="!canConvert"
          :aria-busy="loading"
          @click="convert"
        >
          <span v-if="loading" class="spinner" aria-hidden="true"></span>
          <svg v-else viewBox="0 0 24 24" aria-hidden="true">
            <path d="M12 3v18M5 10l7-7 7 7" />
          </svg>
          {{ loading ? '转换中...' : '生成 YAML 剧本' }}
        </button>

        <section v-if="error" class="error-box" role="alert" aria-live="assertive">
          <strong>{{ error }}</strong>
          <ul v-if="errorHints.length">
            <li v-for="hint in errorHints" :key="hint">{{ hint }}</li>
          </ul>
        </section>
      </aside>

      <section class="result-panel" aria-labelledby="resultTitle" aria-live="polite">
        <div class="panel-head">
          <div>
            <h2 id="resultTitle">剧本结果</h2>
            <p class="panel-subtitle">{{ result ? '结构化 YAML 已生成' : '等待生成' }}</p>
          </div>
          <div class="button-row">
            <button class="ghost-button icon-button" type="button" :disabled="!result" @click="copyYaml">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M8 8h10v12H8z" />
                <path d="M6 16H4V4h12v2" />
              </svg>
              {{ copyLabel }}
            </button>
            <button class="ghost-button icon-button" type="button" :disabled="!result" @click="downloadYaml">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 3v12" />
                <path d="m7 10 5 5 5-5" />
                <path d="M5 21h14" />
              </svg>
              下载
            </button>
          </div>
        </div>

        <div v-if="result" class="summary-grid">
          <article>
            <strong>{{ result.summary.chapter_count }}</strong>
            <span>章节</span>
          </article>
          <article>
            <strong>{{ result.summary.character_count }}</strong>
            <span>角色</span>
          </article>
          <article>
            <strong>{{ result.summary.scene_count }}</strong>
            <span>场次</span>
          </article>
          <article :class="result.validation.valid ? 'pass' : 'fail'">
            <strong>{{ result.validation.valid ? '通过' : '失败' }}</strong>
            <span>Schema</span>
          </article>
        </div>

        <ol v-if="visibleStages.length" class="stage-list" aria-label="转换阶段">
          <li v-for="stage in visibleStages" :key="stage.stage" :class="stage.status">
            <span>{{ stage.stage }}</span>
            <p>{{ stage.message }}</p>
          </li>
        </ol>

        <div v-if="result && !result.validation.valid" class="validation-issues" role="alert">
          <strong>Schema 校验问题</strong>
          <ul>
            <li v-for="issue in result.validation.issues" :key="`${issue.path}-${issue.message}`">
              <code>{{ issue.path }}</code>
              {{ issue.message }}
            </li>
          </ul>
        </div>

        <pre :class="['yaml-output', !result && 'is-empty']" tabindex="0">{{ result?.yaml || '生成后将在这里显示 YAML 剧本' }}</pre>
      </section>
    </section>
  </main>
</template>
