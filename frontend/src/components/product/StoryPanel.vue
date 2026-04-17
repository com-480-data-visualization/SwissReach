<script setup lang="ts">
import StoryMedia from '@/components/product/StoryMedia.vue'
import type { StoryPanelContent } from '@/content/productStory'

defineProps<{
  panel: StoryPanelContent
  isActive: boolean
  panelIndex: number
  panelCount: number
}>()
</script>

<template>
  <article
    class="story-panel page-section"
    :class="{ 'is-active': isActive }"
    :aria-label="panel.title"
  >
    <div class="story-panel__inner">
      <div class="story-panel__copy">
        <div class="story-panel__copy-main">
          <p class="story-panel__eyebrow">{{ panel.eyebrow }}</p>
          <h3 class="story-panel__title">{{ panel.title }}</h3>
        </div>
        <div class="story-panel__copy-side">
          <p class="story-panel__description">{{ panel.description }}</p>
        </div>
      </div>

      <div class="story-panel__media-wrap">
        <StoryMedia :panel="panel" />
        <p class="story-panel__caption">{{ panel.mediaCaption }}</p>
      </div>
    </div>
  </article>
</template>

<style scoped>
.story-panel {
  width: 100%;
  height: 100svh;
  display: flex;
  align-items: center;
  padding:
    clamp(6.5rem, 10vw, 7.75rem)
    clamp(2rem, 5vw, 4.5rem)
    clamp(4.5rem, 8vw, 6rem);
}

.story-panel__inner {
  width: 100%;
  height: 100%;
  max-width: 1440px;
  max-height: calc(100svh - 8rem);
  display: flex;
  flex-direction: column;
  gap: clamp(1.2rem, 2.5vw, 2.2rem);
  margin: 0 auto;
  padding: clamp(0.6rem, 1.4vw, 1rem);
}

.story-panel__copy {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: clamp(2rem, 5vw, 5rem);
  align-items: center;
  width: 100%;
}

.story-panel__copy-main {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.story-panel__copy-side {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.story-panel__count {
  display: inline-flex;
  align-items: center;
  gap: 0.85rem;
  width: fit-content;
  padding: 0.6rem 0.8rem;
  border-radius: 999px;
  border: 1px solid rgba(33, 28, 26, 0.06);
  background: rgba(255, 255, 255, 0.9);
  color: var(--ink-soft);
  font-size: 0.8rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.story-panel__eyebrow {
  margin: 0;
  color: var(--brand);
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.story-panel__title {
  margin: 0;
  max-width: 25ch;
  color: var(--ink-strong);
  font-size: clamp(2rem, 3vw, 3.2rem);
  line-height: 1.02;
  letter-spacing: -0.045em;
  font-weight: 700;
}

.story-panel__description {
  margin: 0;
  max-width: 55rem;
  color: var(--ink-soft);
  font-size: 1.1rem;
  line-height: 1.5;
  padding-bottom: 0;
}

.story-panel__media-wrap {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  gap: 0.8rem;
  align-self: stretch;
}

.story-panel__caption {
  margin: 0;
  max-width: 42rem;
  color: var(--ink-soft);
  font-size: 0.84rem;
  line-height: 1.48;
}

.is-active .story-panel__title,
.is-active .story-panel__description,
.is-active .story-panel__caption {
  opacity: 1;
}

@media (max-width: 1024px) {
  .story-panel__inner {
    max-height: calc(100svh - 11rem);
    padding-right: 0.25rem;
  }


  .story-panel__title {
    max-width: none;
  }
}

@media (max-width: 720px) {
  .story-panel {
    height: 100dvh;
    padding: 5.7rem 0.75rem 4.5rem;
  }

  .story-panel__description {
    font-size: 0.92rem;
  }

  .story-panel__inner {
    max-height: calc(100dvh - 10.2rem);
    padding: 0.4rem;
    border-radius: 24px;
  }
}
</style>
