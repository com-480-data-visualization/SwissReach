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
          <div class="story-panel__meta">
            <span class="story-panel__topic">{{ panel.topic }}</span>
            <span class="story-panel__kind">{{ panel.panelKind }}</span>
          </div>
          <h3 class="story-panel__title">{{ panel.title }}</h3>
        </div>
        <div class="story-panel__copy-side">
          <p class="story-panel__description">{{ panel.description }}</p>
        </div>
      </div>

      <div class="story-panel__media-wrap">
        <StoryMedia :panel="panel" />
        <div class="story-panel__footer">
          <p class="story-panel__caption">{{ panel.mediaCaption }}</p>
        </div>
      </div>
    </div>
  </article>
</template>

<style scoped>
.story-panel {
  height: 100svh;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  padding:
    var(--section-top-padding)
    0
    var(--section-bottom-padding);
}

.story-panel__inner {
  width: 100%;
  height: 100%;
  max-height: calc(100svh - var(--section-top-padding) - var(--section-bottom-padding));
  display: flex;
  flex-direction: column;
  gap: clamp(0.7rem, 1.5vw, 1rem);
  padding: clamp(0.25rem, 1vw, 0.5rem);
}

.story-panel__copy {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
  gap: clamp(1rem, 2vw, 1.6rem);
  align-items: end;
  width: 100%;
}

.story-panel__copy-main {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 0;
}

.story-panel__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.story-panel__topic,
.story-panel__kind {
  display: inline-flex;
  align-items: center;
  min-height: 1.7rem;
  padding: 0 0.62rem;
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.story-panel__topic {
  background: rgba(189, 45, 45, 0.12);
  color: var(--brand);
}

.story-panel__kind {
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid var(--line);
  color: var(--ink-soft);
}

.story-panel__copy-side {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
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

.story-panel__title {
  margin: 0;
  max-width: 22ch;
  color: var(--ink-strong);
  font-size: clamp(1.45rem, 2vw, 2.05rem);
  line-height: 1.02;
  letter-spacing: -0.045em;
  font-weight: 700;
  text-wrap: balance;
}

.story-panel__description {
  margin: 0;
  max-width: 48rem;
  color: var(--ink-soft);
  font-size: 0.94rem;
  line-height: 1.54;
  padding-bottom: 0;
}

.story-panel__media-wrap {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  gap: 0.7rem;
  align-self: stretch;
}

.story-panel__footer {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}

.story-panel__caption {
  margin: 0;
  max-width: 48rem;
  color: var(--ink-soft);
  font-size: 0.78rem;
  line-height: 1.48;
}

.is-active .story-panel__title,
.is-active .story-panel__description,
.is-active .story-panel__caption {
  opacity: 1;
}

@media (max-width: 1024px) {
  .story-panel__inner {
    max-height: calc(100svh - var(--section-top-padding) - var(--section-bottom-padding));
    padding-right: 0.25rem;
  }

  .story-panel__copy {
    grid-template-columns: 1fr;
    gap: 0.7rem;
  }

  .story-panel__title {
    max-width: none;
  }
}

@media (max-width: 720px) {
  .story-panel {
    height: 100dvh;
    padding: var(--section-top-padding) 0 var(--section-bottom-padding);
  }

  .story-panel__description {
    font-size: 0.92rem;
  }

  .story-panel__inner {
    max-height: calc(100dvh - var(--section-top-padding) - var(--section-bottom-padding));
    padding: 0.2rem;
  }

  .story-panel__caption {
    font-size: 0.8rem;
  }
}
</style>
