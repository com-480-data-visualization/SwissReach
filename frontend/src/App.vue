<script setup lang="ts">
import { onBeforeUnmount, onMounted } from 'vue'
import { Top } from '@element-plus/icons-vue'

import gsap from 'gsap'
import { Observer } from 'gsap/Observer'

import ProductTopbar from '@/components/product/ProductTopbar.vue'
import HeroSection from '@/components/product/HeroSection.vue'
import IntroSection from '@/components/product/IntroSection.vue'
import CoreStorySection from '@/components/product/CoreStorySection.vue'
import OutroSection from '@/components/product/OutroSection.vue'
import { storyPanels } from '@/content/productStory'

gsap.registerPlugin(Observer)

/** 
 * Keep URL constants and asset helper from main branch synchronization 
 */
const docsUrl = 'https://swissreach.online/docs/'
const finalPlanUrl = `${docsUrl}final-web-plan`
const githubUrl = 'https://github.com/com-480-data-visualization/SwissReach'

/** Avoid root-absolute asset paths in script — Vite may treat them as module imports. */
const asset = (path: string) => `${import.meta.env.BASE_URL}${path}`.replace(/\/{2,}/g, '/')

interface AnchorPoint {
  top: number
}

let observer: Observer | null = null
let scrollLock = false
let unlockTimer: number | null = null
let settleTimer: number | null = null

const clearUnlockTimer = () => {
  if (unlockTimer !== null) {
    window.clearTimeout(unlockTimer)
    unlockTimer = null
  }
}

const clearSettleTimer = () => {
  if (settleTimer !== null) {
    window.clearTimeout(settleTimer)
    settleTimer = null
  }
}

const getStoryAnchors = (): AnchorPoint[] => {
  const story = document.getElementById('story')
  if (!story) {
    return []
  }

  const viewportHeight = window.innerHeight
  const storyTop = story.offsetTop
  const travel = Math.max(story.offsetHeight - viewportHeight, 0)
  const maxIndex = Math.max(storyPanels.length - 1, 0)
  const step = maxIndex === 0 ? 0 : travel / maxIndex

  return Array.from({ length: storyPanels.length }, (_, index) => ({
    top: storyTop + step * index,
  }))
}

const getAnchors = (): AnchorPoint[] => {
  const hero = document.getElementById('hero')
  const intro = document.getElementById('intro')
  const outro = document.getElementById('outro')
  if (!hero || !intro || !outro) {
    return []
  }

  return [
    { top: hero.offsetTop },
    { top: intro.offsetTop },
    ...getStoryAnchors(),
    { top: outro.offsetTop },
  ]
}

const isInDiscreteRange = () => {
  const anchors = getAnchors()
  if (anchors.length === 0) {
    return false
  }

  const first = anchors[0]?.top ?? 0
  const last = anchors[anchors.length - 1]?.top ?? 0
  const proximity = window.innerHeight * 0.35
  const current = window.scrollY

  return current >= first - proximity && current <= last + proximity
}

const getNearestAnchorIndex = () => {
  const anchors = getAnchors()
  if (anchors.length === 0) {
    return 0
  }

  const current = window.scrollY
  return anchors.reduce((nearestIndex, anchor, index, all) => {
    const nearestTop = all[nearestIndex]?.top ?? all[0]?.top ?? 0
    return Math.abs(anchor.top - current) < Math.abs(nearestTop - current) ? index : nearestIndex
  }, 0)
}

const jumpToAnchor = (index: number) => {
  const anchors = getAnchors()
  if (anchors.length === 0) {
    return
  }

  const clampedIndex = Math.max(0, Math.min(index, anchors.length - 1))
  const targetTop = anchors[clampedIndex]?.top ?? anchors[0]?.top ?? 0

  if (Math.abs(window.scrollY - targetTop) <= 2) {
    return
  }

  scrollLock = true
  clearUnlockTimer()
  window.scrollTo({
    top: targetTop,
    behavior: 'smooth',
  })
  unlockTimer = window.setTimeout(() => {
    scrollLock = false
    unlockTimer = null
  }, 600)
}

const stepAnchor = (direction: 1 | -1) => {
  if (scrollLock || !isInDiscreteRange()) {
    return
  }

  const anchors = getAnchors()
  if (anchors.length === 0) {
    return
  }

  const currentIndex = getNearestAnchorIndex()
  const nextIndex = Math.max(0, Math.min(currentIndex + direction, anchors.length - 1))

  if (nextIndex === currentIndex) {
    return
  }

  jumpToAnchor(nextIndex)
}

const settleToNearestAnchor = () => {
  if (scrollLock || !isInDiscreteRange()) {
    return
  }

  jumpToAnchor(getNearestAnchorIndex())
}

const handleKeydown = (event: KeyboardEvent) => {
  if (!isInDiscreteRange()) {
    return
  }

  let direction: 1 | -1 | null = null

  switch (event.key) {
    case 'ArrowDown':
    case 'PageDown':
    case ' ':
      direction = 1
      break
    case 'ArrowUp':
    case 'PageUp':
      direction = -1
      break
    default:
      direction = null
  }

  if (!direction) {
    return
  }

  event.preventDefault()
  stepAnchor(direction)
}

const handleScroll = () => {
  if (isInDiscreteRange()) {
    observer?.enable()
    clearSettleTimer()
    settleTimer = window.setTimeout(() => {
      settleToNearestAnchor()
    }, 120)
    return
  }

  observer?.disable()
}

const handleBacktopClick = () => {
  scrollLock = true
  clearUnlockTimer()
  // Element Plus Backtop scroll takes 500ms via requestAnimationFrame
  // We lock for 600ms to safely bypass our GSAP observers
  unlockTimer = window.setTimeout(() => {
    scrollLock = false
    unlockTimer = null
  }, 600)
}

onMounted(() => {
  observer = Observer.create({
    target: window,
    type: 'wheel,touch',
    tolerance: 18,
    preventDefault: true,
    onDown: () => stepAnchor(1),
    onUp: () => stepAnchor(-1),
  })
  observer.disable()

  handleScroll()
  window.addEventListener('scroll', handleScroll, { passive: true })
  window.addEventListener('scrollend', settleToNearestAnchor)
  window.addEventListener('resize', handleScroll, { passive: true })
  window.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  clearUnlockTimer()
  clearSettleTimer()
  observer?.kill()
  observer = null
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('scrollend', settleToNearestAnchor)
  window.removeEventListener('resize', handleScroll)
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <div class="app-shell">
    <ProductTopbar />
    <main>
      <HeroSection />
      <IntroSection />
      <CoreStorySection />
      <OutroSection />
    </main>

    <el-backtop 
      :right="24" 
      :bottom="24" 
      :visibility-height="500"
      @click="handleBacktopClick"
    >
      <el-icon class="custom-backtop-arrow"><Top /></el-icon>
    </el-backtop>
  </div>
</template>

<style>
@import '../../docs/public/fonts/misans/misans.css';
</style>

<style scoped>
.app-shell {
  min-height: 100vh;
}

:deep(.el-backtop) {
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.88) !important;
  box-shadow: 0 14px 28px rgba(49, 34, 27, 0.1) !important;
  color: var(--ink-strong) !important;
  backdrop-filter: blur(12px) !important;
  transition: transform 180ms ease, background-color 180ms ease, color 180ms ease !important;
}

:deep(.el-backtop:hover) {
  background: rgba(255, 255, 255, 0.96) !important;
  color: var(--brand) !important;
  transform: translateY(-1px) !important;
}

.custom-backtop-arrow {
  font-size: 1.3rem; /* Using font-size for el-icon */
  font-weight: bold;
}
</style>
