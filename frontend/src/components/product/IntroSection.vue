<script setup lang="ts">
import { introMetrics } from '@/content/productStory'
</script>

<template>
  <section id="intro" class="page-section intro-shell">
    <div class="intro-copy">
      <p class="section-label">Overview</p>
      <h2 class="section-title">
        Strong transport coverage does not automatically turn into strong daily retail opportunity.
      </h2>
      <p class="section-text">
        SwissReach starts with the national rail backbone, then asks the more practical question hiding underneath it: once the network is there, what kind of everyday choice does it actually unlock? That is why the page moves from reachability, to store geography, to retail access, instead of treating supermarkets as a small add-on at the end.
      </p>
    </div>

    <div class="intro-metrics">
      <article v-for="metric in introMetrics" :key="metric.value" class="metric-chip">
        <span class="metric-chip__value" :data-tone="metric.tone ?? 'neutral'">
          {{ metric.value }}
        </span>
        <span class="metric-chip__label">{{ metric.label }}</span>
      </article>
    </div>
  </section>
</template>

<style scoped>
.intro-shell {
  height: 100svh;
  min-height: 100svh;
  box-sizing: border-box;
  padding-top: var(--section-top-padding);
  padding-bottom: var(--section-bottom-padding);
  display: grid;
  align-content: center;
  gap: 2.25rem;
}

.intro-copy {
  max-width: 50rem;
}

.intro-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

@media (max-width: 900px) {
  .intro-metrics {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .intro-shell {
    height: 100dvh;
    min-height: 100dvh;
    align-content: start;
  }
}
</style>
