<script setup lang="ts">
import { BookOpenText, Clapperboard, ShieldAlert, ShieldCheck, Users } from '@lucide/vue'

import type { ConvertSummary } from '../types/conversion'

defineProps<{
  summary: ConvertSummary
  valid: boolean
}>()
</script>

<template>
  <div class="summary-grid">
    <article>
      <BookOpenText :size="18" aria-hidden="true" />
      <strong>{{ summary.chapter_count }}</strong>
      <span>章节</span>
    </article>
    <article>
      <Users :size="18" aria-hidden="true" />
      <strong>{{ summary.character_count }}</strong>
      <span>角色</span>
    </article>
    <article>
      <Clapperboard :size="18" aria-hidden="true" />
      <strong>{{ summary.scene_count }}</strong>
      <span>场次</span>
    </article>
    <article :class="valid ? 'pass' : 'fail'">
      <ShieldCheck v-if="valid" :size="18" aria-hidden="true" />
      <ShieldAlert v-else :size="18" aria-hidden="true" />
      <strong>{{ valid ? '通过' : '失败' }}</strong>
      <span>Schema</span>
    </article>
  </div>
</template>
