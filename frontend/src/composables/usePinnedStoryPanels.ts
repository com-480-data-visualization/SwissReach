import { computed, onBeforeUnmount, onMounted, ref, type Ref } from 'vue'

interface UsePinnedStoryPanelsOptions {
  panelCount: number
}

function clampIndex(index: number, max: number): number {
  return Math.max(0, Math.min(index, max))
}

export function usePinnedStoryPanels(
  rootRef: Ref<HTMLElement | null>,
  options: UsePinnedStoryPanelsOptions,
) {
  const activeIndex = ref(0)
  const direction = ref<1 | -1>(1)
  const isPinned = ref(false)
  const lastIndex = computed(() => Math.max(0, options.panelCount - 1))

  const getSectionMetrics = () => {
    const root = rootRef.value
    if (!root) {
      return null
    }

    const viewportHeight = window.innerHeight
    const absoluteTop = window.scrollY + root.getBoundingClientRect().top
    const travel = Math.max(root.offsetHeight - viewportHeight, 0)
    const step = lastIndex.value === 0 ? 0 : travel / lastIndex.value

    return {
      absoluteTop,
      travel,
      step,
    }
  }

  const syncFromScroll = () => {
    const metrics = getSectionMetrics()
    if (!metrics) {
      isPinned.value = false
      return
    }

    const current = window.scrollY
    isPinned.value = current >= metrics.absoluteTop && current <= metrics.absoluteTop + metrics.travel

    const nextIndex =
      metrics.step === 0
        ? 0
        : Math.round((current - metrics.absoluteTop) / Math.max(metrics.step, 1))
    const clampedIndex = clampIndex(nextIndex, lastIndex.value)

    direction.value = clampedIndex >= activeIndex.value ? 1 : -1
    activeIndex.value = clampedIndex
  }

  const goTo = (index: number) => {
    const metrics = getSectionMetrics()
    if (!metrics) {
      return
    }

    const clampedIndex = clampIndex(index, lastIndex.value)
    direction.value = clampedIndex >= activeIndex.value ? 1 : -1
    activeIndex.value = clampedIndex

    window.scrollTo({
      top: metrics.absoluteTop + metrics.step * clampedIndex,
      behavior: 'smooth',
    })
  }

  onMounted(() => {
    syncFromScroll()
    window.addEventListener('scroll', syncFromScroll, { passive: true })
    window.addEventListener('resize', syncFromScroll, { passive: true })
  })

  onBeforeUnmount(() => {
    window.removeEventListener('scroll', syncFromScroll)
    window.removeEventListener('resize', syncFromScroll)
  })

  return {
    activeIndex,
    direction,
    isPinned,
    goTo,
  }
}
