<script setup lang="ts">
import { Braces, CircuitBoard, Sparkles } from '@lucide/vue'
</script>

<template>
  <header class="topbar">
    <div class="brand-block">
      <span class="brand-mark" aria-hidden="true">
        <Sparkles :size="20" />
      </span>
      <div>
        <p class="eyebrow">XEngineer · AI Screenplay Studio</p>
        <h1>AI 小说转剧本工具</h1>
      </div>
    </div>

    <div class="workflow-strip" aria-label="工作流">
      <span>
        <CircuitBoard :size="16" />
        Vue 工作台
      </span>
      <span>
        <Sparkles :size="16" />
        AI 改编
      </span>
      <span>
        <Braces :size="16" />
        YAML Schema
      </span>
    </div>
  </header>
</template>
