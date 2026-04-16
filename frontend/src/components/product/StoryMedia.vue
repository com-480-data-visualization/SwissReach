<script setup lang="ts">
import { type StoryPanelContent } from '@/content/productStory'
import ReachabilityMap from '@/components/ReachabilityMap.vue'
import LausanneReachabilityLab from '@/components/LausanneReachabilityLab.vue'
import BusiestRailChart from '@/components/BusiestRailChart.vue'

defineProps<{
  panel: StoryPanelContent
}>()
</script>

<template>
  <!-- @wheel.stop prevents GSAP from turning slides when scrolling inside the map -->
  <figure class="media-shell section-frame" :data-variant="panel.mediaVariant" @wheel.stop>
    <ReachabilityMap v-if="panel.mediaVariant === 'reachability-map'" class="interactive-embed" />
    <LausanneReachabilityLab v-else-if="panel.mediaVariant === 'reachability-lab'" class="interactive-embed" />
    <BusiestRailChart v-else-if="panel.mediaVariant === 'busiest-rail'" class="interactive-embed" />
  </figure>
</template>

<style scoped>
.media-shell {
  position: relative;
  margin: 0;
  width: 100%;
  height: min(48rem, 80svh); 
  border-radius: var(--radius-shell);
  overflow: hidden;
  padding: 0;
  display: flex;
}

.interactive-embed {
  width: 100%;
  height: 100%;
  border-radius: var(--radius-shell);
  background: white;
}

:deep(.map-wrapper),
:deep(.lab),
:deep(.chart-shell) {
  padding: 1rem;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
}

@media (max-width: 1024px) {
  .media-shell {
    height: 50vh;
  }
}
</style>
