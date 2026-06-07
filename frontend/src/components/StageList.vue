<script setup lang="ts">
import type { StageLog } from '../types/conversion'

defineProps<{
  stages: StageLog[]
}>()
</script>

<template>
  <ol class="stage-list" aria-label="转换阶段">
    <li v-for="stage in stages" :key="stage.stage" :class="stage.status">
      <span>{{ stage.stage }}</span>
      <p>{{ stage.message }}</p>
    </li>
  </ol>
</template>
