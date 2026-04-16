import { onBeforeUnmount, onMounted, ref } from 'vue'

export function useReducedMotion() {
  const prefersReducedMotion = ref(false)
  let mediaQuery: MediaQueryList | null = null

  const syncPreference = () => {
    prefersReducedMotion.value = mediaQuery?.matches ?? false
  }

  onMounted(() => {
    mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    syncPreference()
    mediaQuery.addEventListener('change', syncPreference)
  })

  onBeforeUnmount(() => {
    mediaQuery?.removeEventListener('change', syncPreference)
  })

  return prefersReducedMotion
}
