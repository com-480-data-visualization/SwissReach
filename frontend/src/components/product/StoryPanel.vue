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
        <div class="story-panel__count">
          <span>{{ String(panelIndex + 1).padStart(2, '0') }}</span>
          <span>{{ String(panelCount).padStart(2, '0') }}</span>
        </div>

        <p class="story-panel__eyebrow">{{ panel.eyebrow }}</p>
        <h3 class="story-panel__title">{{ panel.title }}</h3>
        <p class="story-panel__description">{{ panel.description }}</p>

        <ul class="story-panel__highlights">
          <li v-for="highlight in panel.highlights" :key="highlight">
            {{ highlight }}
          </li>
        </ul>

        <div class="story-panel__metrics">
          <article v-for="metric in panel.metrics" :key="metric.value" class="metric-chip">
            <span class="metric-chip__value" :data-tone="metric.tone ?? 'neutral'">
              {{ metric.value }}
            </span>
            <span class="metric-chip__label">{{ metric.label }}</span>
          </article>
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
  max-width: 1440px;
  max-height: calc(100svh - 12rem);
  display: grid;
  grid-template-columns: minmax(0, 0.84fr) minmax(0, 1.04fr);
  gap: clamp(1.5rem, 3vw, 3.2rem);
  align-items: center;
  margin: 0 auto;
  padding: clamp(0.6rem, 1.4vw, 1rem);
}

.story-panel__copy {
  display: grid;
  gap: 0.8rem;
  align-content: center;
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
  max-width: 14ch;
  color: var(--ink-strong);
  font-size: clamp(1.85rem, 2.6vw, 2.8rem);
  line-height: 1.05;
  letter-spacing: -0.045em;
  font-weight: 700;
}

.story-panel__description {
  margin: 0;
  max-width: 38rem;
  color: var(--ink-soft);
  font-size: 0.96rem;
  line-height: 1.65;
}

.story-panel__highlights {
  display: grid;
  gap: 0.55rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.story-panel__highlights li {
  position: relative;
  padding-left: 1rem;
  color: var(--ink);
  line-height: 1.55;
}

.story-panel__highlights li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0.7rem;
  width: 0.42rem;
  height: 0.42rem;
  border-radius: 999px;
  background: rgba(189, 45, 45, 0.55);
}

.story-panel__metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem;
}

.story-panel__media-wrap {
  display: grid;
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
    grid-template-columns: 1fr;
    max-height: calc(100svh - 11rem);
    gap: 1rem;
    overflow-y: auto;
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
