<script setup lang="ts">
import { Braces, Copy, Download } from '@lucide/vue'

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
  <section class="result-panel work-panel" aria-labelledby="resultTitle" aria-live="polite">
    <div class="panel-head">
      <div class="section-title">
        <span class="section-icon" aria-hidden="true">
          <Braces :size="18" />
        </span>
        <div>
          <h2 id="resultTitle">剧本结果</h2>
          <p class="panel-subtitle">{{ result ? '结构化 YAML 已生成' : '等待生成' }}</p>
        </div>
      </div>
      <div class="button-row">
        <button class="ghost-button icon-button" type="button" :disabled="!result" @click="$emit('copyYaml')">
          <Copy :size="18" aria-hidden="true" />
          {{ copyLabel }}
        </button>
        <button class="ghost-button icon-button" type="button" :disabled="!result" @click="$emit('downloadYaml')">
          <Download :size="18" aria-hidden="true" />
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

    <div class="yaml-frame">
      <div class="yaml-toolbar" aria-hidden="true">
        <span></span>
        <span></span>
        <span></span>
        <code>screenplay.yaml</code>
      </div>
      <pre :class="['yaml-output', !result && 'is-empty']" tabindex="0">{{ result?.yaml || '生成后将在这里显示 YAML 剧本' }}</pre>
    </div>
  </section>
</template>
