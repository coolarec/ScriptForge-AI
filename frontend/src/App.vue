<script setup lang="ts">
import { computed, ref } from 'vue'

type ProviderMode = 'mock' | 'api'
type DialogueDensity = 'low' | 'medium' | 'high'

interface StageLog {
  stage: string
  status: 'success' | 'warning' | 'error'
  message: string
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

const chapterCount = computed(() => {
  const matches = novelText.value.match(/^(?:\s*(?:第[零一二三四五六七八九十百千万\d]+章|Chapter\s+\d+|#{1,3}\s+))/gim)
  return matches?.length ?? 0
})

const canConvert = computed(() => novelText.value.trim().length > 0 && !loading.value)

async function loadSample() {
  error.value = ''
  const response = await fetch('/api/sample')
  const data = await response.json()
  novelText.value = data.text
}

async function convert() {
  if (!canConvert.value) return
  loading.value = true
  error.value = ''
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
      error.value = data.detail?.message ?? '转换失败'
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
</script>

<template>
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

    <section class="workspace">
      <aside class="input-panel">
        <div class="panel-head">
          <h2>小说输入</h2>
          <button class="ghost-button" type="button" @click="loadSample">载入样例</button>
        </div>

        <textarea
          v-model="novelText"
          class="novel-input"
          spellcheck="false"
          placeholder="粘贴至少 3 个章节的小说文本"
        />

        <div class="metrics-row">
          <span :class="['metric', chapterCount >= 3 ? 'ok' : 'warn']">{{ chapterCount || '未识别' }} 章</span>
          <span class="metric">{{ novelText.length }} 字符</span>
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
            <input v-model.number="targetSceneCount" type="number" min="3" max="12" />
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

        <button class="primary-button" type="button" :disabled="!canConvert" @click="convert">
          {{ loading ? '转换中...' : '生成 YAML 剧本' }}
        </button>
        <p v-if="error" class="error-box">{{ error }}</p>
      </aside>

      <section class="result-panel">
        <div class="panel-head">
          <h2>剧本结果</h2>
          <div class="button-row">
            <button class="ghost-button" type="button" :disabled="!result" @click="copyYaml">复制</button>
            <button class="ghost-button" type="button" :disabled="!result" @click="downloadYaml">下载</button>
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

        <ol v-if="result" class="stage-list">
          <li v-for="stage in result.stages" :key="stage.stage" :class="stage.status">
            <span>{{ stage.stage }}</span>
            <p>{{ stage.message }}</p>
          </li>
        </ol>

        <pre class="yaml-output">{{ result?.yaml || '生成后将在这里显示 YAML 剧本' }}</pre>
      </section>
    </section>
  </main>
</template>
