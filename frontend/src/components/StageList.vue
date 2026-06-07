<script setup lang="ts">
import { AlertTriangle, CheckCircle2, Clock3 } from '@lucide/vue'

import type { StageLog } from '../types/conversion'

defineProps<{
  stages: StageLog[]
}>()
</script>

<template>
  <ol class="stage-list" aria-label="转换阶段">
    <li v-for="stage in stages" :key="stage.stage" :class="stage.status">
      <span class="stage-dot" aria-hidden="true">
        <CheckCircle2 v-if="stage.status === 'success'" :size="16" />
        <AlertTriangle v-else-if="stage.status === 'error'" :size="16" />
        <Clock3 v-else :size="16" />
      </span>
      <span>{{ stage.stage }}</span>
      <p>{{ stage.message }}</p>
    </li>
  </ol>
</template>
