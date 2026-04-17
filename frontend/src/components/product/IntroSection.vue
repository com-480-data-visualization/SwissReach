<script setup lang="ts">
import { introMetrics } from '@/content/productStory'
</script>

<template>
  <section id="intro" class="page-section intro-shell">
    <div class="intro-copy">
      <p class="section-label">Overview</p>
      <h2 class="section-title">
        Understanding practical reach, not just abstract network scale.
      </h2>
      <p class="section-text">
        SwissReach illustrates where the railway network carries weight, where coverage begins to thin out, and why that difference matters once daily routines—like accessing schools or hospitals—enter the picture. We connect transit schedules with everyday points of interest.
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
  min-height: 100svh;
  padding-top: clamp(5rem, 8vw, 7rem);
  padding-bottom: clamp(4.5rem, 7vw, 6.5rem);
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
    min-height: 100dvh;
    align-content: start;
    padding-top: 6.5rem;
    padding-bottom: 3rem;
  }
}
</style>
