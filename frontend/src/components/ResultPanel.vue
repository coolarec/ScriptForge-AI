<script setup lang="ts">
import type { ConvertResponse, StageLog } from '../types/conversion'
import StageList from './StageList.vue'
import SummaryGrid from './SummaryGrid.vue'

defineProps<{
  result: ConvertResponse | null
  stages: StageLog[]
  copyLabel: string
}>()

defineEmits<{
  copyYaml: []
  downloadYaml: []
}>()
</script>

<template>
  <section class="result-panel" aria-labelledby="resultTitle" aria-live="polite">
    <div class="panel-head">
      <div>
        <h2 id="resultTitle">剧本结果</h2>
        <p class="panel-subtitle">{{ result ? '结构化 YAML 已生成' : '等待生成' }}</p>
      </div>
      <div class="button-row">
        <button class="ghost-button icon-button" type="button" :disabled="!result" @click="$emit('copyYaml')">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M8 8h10v12H8z" />
            <path d="M6 16H4V4h12v2" />
          </svg>
          {{ copyLabel }}
        </button>
        <button class="ghost-button icon-button" type="button" :disabled="!result" @click="$emit('downloadYaml')">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M12 3v12" />
            <path d="m7 10 5 5 5-5" />
            <path d="M5 21h14" />
          </svg>
          下载
        </button>
      </div>
    </div>

    <SummaryGrid v-if="result" :summary="result.summary" :valid="result.validation.valid" />

    <StageList v-if="stages.length" :stages="stages" />

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
</template>
