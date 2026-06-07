<script setup lang="ts">
import { BookOpenText, CheckCircle2, DatabaseZap, FileInput, LoaderCircle, SlidersHorizontal, Sparkles } from '@lucide/vue'

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

function selectProvider(mode: ProviderMode) {
  provider.value = mode
}
</script>

<template>
  <aside class="input-panel work-panel" aria-labelledby="inputTitle">
    <div class="panel-head">
      <div class="section-title">
        <span class="section-icon" aria-hidden="true">
          <BookOpenText :size="18" />
        </span>
        <div>
          <h2 id="inputTitle">小说输入</h2>
          <p class="panel-subtitle">{{ chapterState }}</p>
        </div>
      </div>
      <button class="ghost-button icon-button" type="button" @click="$emit('loadSample')">
        <FileInput :size="18" aria-hidden="true" />
        载入样例
      </button>
    </div>

    <div class="editor-frame">
      <label class="field-label" for="novelText">小说文本</label>
      <textarea
        id="novelText"
        v-model="novelText"
        class="novel-input"
        spellcheck="false"
        placeholder="粘贴至少 3 个章节的小说文本"
      />
    </div>

    <div class="metrics-row" aria-live="polite">
      <span :class="['metric', chapterCount >= 3 ? 'ok' : 'warn']">
        <CheckCircle2 v-if="chapterCount >= 3" :size="15" aria-hidden="true" />
        {{ chapterCount || '未识别' }} 章
      </span>
      <span class="metric">{{ novelText.length }} 字符</span>
      <span class="metric">覆盖：{{ coveredChapters }}</span>
    </div>

    <div class="subsection-title">
      <SlidersHorizontal :size="17" aria-hidden="true" />
      <span>改编参数</span>
    </div>

    <div class="control-grid">
      <fieldset class="mode-control">
        <legend>生成模式</legend>
        <div class="segmented-control">
          <button
            type="button"
            :class="['segment-option', provider === 'mock' && 'is-active']"
            :aria-pressed="provider === 'mock'"
            @click="selectProvider('mock')"
          >
            <DatabaseZap :size="16" aria-hidden="true" />
            Mock 演示
          </button>
          <button
            type="button"
            :class="['segment-option', provider === 'api' && 'is-active']"
            :aria-pressed="provider === 'api'"
            @click="selectProvider('api')"
          >
            <Sparkles :size="16" aria-hidden="true" />
            API 生成
          </button>
        </div>
      </fieldset>

      <label>
        <span>场次数量</span>
        <div class="range-control">
          <input v-model.number="targetSceneCount" type="range" min="3" max="12" />
          <input v-model.number="targetSceneCount" type="number" min="3" max="12" inputmode="numeric" />
        </div>
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
      <LoaderCircle v-if="loading" class="spin-icon" :size="18" aria-hidden="true" />
      <Sparkles v-else :size="18" aria-hidden="true" />
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
