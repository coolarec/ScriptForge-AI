import { computed, ref } from 'vue'

import { ConversionApiError, convertNovel, loadSampleText } from '../api/conversion'
import type { ConvertResponse, DialogueDensity, ProviderMode, StageLog } from '../types/conversion'

const CHAPTER_HEADING_PATTERN = /^(?:\s*(?:第[零一二三四五六七八九十百千万\d]+章|Chapter\s+\d+|#{1,3}\s+))/gim

export function useConversion() {
  const novelText = ref('')
  const provider = ref<ProviderMode>('mock')
  const targetSceneCount = ref(6)
  const dialogueDensity = ref<DialogueDensity>('medium')
  const preserveNarration = ref(true)
  const loading = ref(false)
  const result = ref<ConvertResponse | null>(null)
  const error = ref('')
  const errorHints = ref<string[]>([])
  const copyLabel = ref('复制')

  const chapterCount = computed(() => novelText.value.match(CHAPTER_HEADING_PATTERN)?.length ?? 0)

  const chapterState = computed(() => {
    if (!novelText.value.trim()) return '等待输入'
    return chapterCount.value >= 3 ? '章节达标' : '至少需要 3 章'
  })

  const canConvert = computed(() => novelText.value.trim().length > 0 && !loading.value)

  const visibleStages = computed<StageLog[]>(() => {
    if (result.value) return result.value.stages
    if (!loading.value) return []
    return [
      {
        stage: 'pipeline',
        status: 'warning',
        message: '后端正在解析章节、改编分场并校验 YAML。',
      },
    ]
  })

  const coveredChapters = computed(() => result.value?.summary.covered_chapters.join('、') || '生成后显示')

  async function loadSample() {
    resetFeedback()
    try {
      novelText.value = await loadSampleText()
    } catch (err) {
      assignError(err, '样例加载失败')
    }
  }

  async function convert() {
    if (!canConvert.value) return
    loading.value = true
    resetFeedback()
    result.value = null

    try {
      result.value = await convertNovel({
        text: novelText.value,
        provider: provider.value,
        config: {
          target_scene_count: targetSceneCount.value,
          dialogue_density: dialogueDensity.value,
          preserve_narration: preserveNarration.value,
        },
      })
    } catch (err) {
      assignError(err, '网络请求失败')
    } finally {
      loading.value = false
    }
  }

  async function copyYaml() {
    if (!result.value) return
    await navigator.clipboard.writeText(result.value.yaml)
    copyLabel.value = '已复制'
    window.setTimeout(() => {
      copyLabel.value = '复制'
    }, 1600)
  }

  function downloadYaml() {
    if (!result.value) return
    const blob = new Blob([result.value.yaml], { type: 'text/yaml;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'screenplay.yaml'
    link.click()
    URL.revokeObjectURL(url)
  }

  function resetFeedback() {
    error.value = ''
    errorHints.value = []
  }

  function assignError(err: unknown, fallback: string) {
    error.value = err instanceof Error ? err.message : fallback
    errorHints.value = err instanceof ConversionApiError ? err.hints : []
  }

  return {
    novelText,
    provider,
    targetSceneCount,
    dialogueDensity,
    preserveNarration,
    loading,
    result,
    error,
    errorHints,
    copyLabel,
    chapterCount,
    chapterState,
    canConvert,
    visibleStages,
    coveredChapters,
    loadSample,
    convert,
    copyYaml,
    downloadYaml,
  }
}
