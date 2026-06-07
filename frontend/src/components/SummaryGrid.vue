<script setup lang="ts">
import type { ConvertSummary } from '../types/conversion'

defineProps<{
  summary: ConvertSummary
  valid: boolean
}>()
</script>

<template>
  <div class="summary-grid">
    <article>
      <strong>{{ summary.chapter_count }}</strong>
      <span>章节</span>
    </article>
    <article>
      <strong>{{ summary.character_count }}</strong>
      <span>角色</span>
    </article>
    <article>
      <strong>{{ summary.scene_count }}</strong>
      <span>场次</span>
    </article>
    <article :class="valid ? 'pass' : 'fail'">
      <strong>{{ valid ? '通过' : '失败' }}</strong>
      <span>Schema</span>
    </article>
  </div>
</template>
