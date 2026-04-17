<script setup lang="ts">
import { computed, ref } from 'vue'

import StoryPanel from '@/components/product/StoryPanel.vue'
import { storyPanels, type StoryPanelContent } from '@/content/productStory'
import { usePinnedStoryPanels } from '@/composables/usePinnedStoryPanels'

const storyRef = ref<HTMLElement | null>(null)
const { activeIndex, direction, isPinned, goTo } = usePinnedStoryPanels(storyRef, {
  panelCount: storyPanels.length,
})

const sectionStyle = computed(() => ({
  '--panel-count': String(storyPanels.length),
}))

const activePanel = computed<StoryPanelContent>(() => storyPanels[activeIndex.value] ?? storyPanels[0]!)
const transitionName = computed(() => (direction.value > 0 ? 'story-forward' : 'story-backward'))
</script>

<template>
  <section
    id="story"
    ref="storyRef"
    class="story-shell"
    :style="sectionStyle"
    aria-label="SwissReach core product story"
  >
    <div class="story-stage">
      <div class="story-panels" :class="{ 'is-pinned': isPinned }">
        <Transition :name="transitionName" mode="out-in">
          <StoryPanel
            :key="activePanel.id"
            :panel="activePanel"
            :is-active="true"
            :panel-index="activeIndex"
            :panel-count="storyPanels.length"
          />
        </Transition>
      </div>

      <div class="story-pagination" role="tablist" aria-label="Story panels">
        <button
          v-for="(panel, index) in storyPanels"
          :key="panel.id"
          :aria-selected="activeIndex === index"
          :aria-label="panel.navLabel"
          class="button-dot"
          :class="{ 'is-active': activeIndex === index }"
          role="tab"
          type="button"
          @click="goTo(index)"
        />
      </div>
    </div>
  </section>
</template>

<style scoped>
.story-shell {
  position: relative;
  height: calc(var(--panel-count) * 100svh);
}

.story-stage {
  position: sticky;
  top: 0;
  height: 100svh;
  overflow: clip;
  background: var(--page-bg);
}

.story-pagination {
  position: absolute;
  left: 50%;
  bottom: clamp(1.4rem, 3vw, 2.4rem);
  z-index: 4;
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.65rem 0.9rem;
  border-radius: 999px;
  background: rgba(247, 243, 239, 0.78);
  backdrop-filter: blur(10px);
  transform: translateX(-50%);
}

.story-panels {
  height: 100%;
  position: relative;
  overflow: hidden;
}

.story-panels.is-pinned {
  cursor: ew-resize;
}

.story-forward-enter-active,
.story-forward-leave-active,
.story-backward-enter-active,
.story-backward-leave-active {
  transition:
    opacity 280ms ease,
    transform 360ms cubic-bezier(0.24, 0.86, 0.22, 1);
}

.story-forward-enter-from,
.story-backward-leave-to {
  opacity: 0;
  transform: translate3d(28px, 0, 0);
}

.story-forward-leave-to,
.story-backward-enter-from {
  opacity: 0;
  transform: translate3d(-28px, 0, 0);
}

@media (max-width: 720px) {
  .story-shell {
    height: calc(var(--panel-count) * 100dvh);
  }

  .story-stage {
    height: 100dvh;
    min-height: 100dvh;
  }
}
</style>
