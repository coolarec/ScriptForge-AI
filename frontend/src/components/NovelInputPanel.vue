<script setup lang="ts">
import type { DialogueDensity, ProviderMode } from '../types/conversion'

const novelText = defineModel<string>('novelText', { required: true })
const provider = defineModel<ProviderMode>('provider', { required: true })
const targetSceneCount = defineModel<number>('targetSceneCount', { required: true })
const dialogueDensity = defineModel<DialogueDensity>('dialogueDensity', { required: true })
const preserveNarration = defineModel<boolean>('preserveNarration', { required: true })

defineProps<{
  chapterCount: number
  chapterState: string
  coveredChapters: string
  canConvert: boolean
  loading: boolean
  error: string
  errorHints: string[]
}>()

defineEmits<{
  loadSample: []
  convert: []
}>()
</script>

<template>
  <aside class="input-panel" aria-labelledby="inputTitle">
    <div class="panel-head">
      <div>
        <h2 id="inputTitle">小说输入</h2>
        <p class="panel-subtitle">{{ chapterState }}</p>
      </div>
      <button class="ghost-button icon-button" type="button" @click="$emit('loadSample')">
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
      @click="$emit('convert')"
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
</template>
