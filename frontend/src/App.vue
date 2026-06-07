<script setup lang="ts">
import AppHeader from './components/AppHeader.vue'
import NovelInputPanel from './components/NovelInputPanel.vue'
import ResultPanel from './components/ResultPanel.vue'
import { useConversion } from './composables/useConversion'

const conversion = useConversion()
</script>

<template>
  <a class="skip-link" href="#workspace">跳到转换工作区</a>
  <main class="app-shell">
    <AppHeader />

    <section id="workspace" class="workspace" aria-label="小说转剧本工作区">
      <NovelInputPanel
        v-model:novel-text="conversion.novelText.value"
        v-model:provider="conversion.provider.value"
        v-model:target-scene-count="conversion.targetSceneCount.value"
        v-model:dialogue-density="conversion.dialogueDensity.value"
        v-model:preserve-narration="conversion.preserveNarration.value"
        :chapter-count="conversion.chapterCount.value"
        :chapter-state="conversion.chapterState.value"
        :covered-chapters="conversion.coveredChapters.value"
        :can-convert="conversion.canConvert.value"
        :loading="conversion.loading.value"
        :error="conversion.error.value"
        :error-hints="conversion.errorHints.value"
        @load-sample="conversion.loadSample"
        @convert="conversion.convert"
      />

      <ResultPanel
        :result="conversion.result.value"
        :stages="conversion.visibleStages.value"
        :copy-label="conversion.copyLabel.value"
        @copy-yaml="conversion.copyYaml"
        @download-yaml="conversion.downloadYaml"
      />
    </section>
  </main>
</template>
