<script setup lang="ts">
import { type StoryPanelContent } from '@/content/productStory'
import ReachabilityMap from '@/components/ReachabilityMap.vue'
import LausanneReachabilityLab from '@/components/LausanneReachabilityLab.vue'
import BusiestRailChart from '@/components/BusiestRailChart.vue'
import RetailDensityMap from '@/components/RetailDensityMap.vue'
import RetailAccessMap from '@/components/RetailAccessMap.vue'

defineProps<{
  panel: StoryPanelContent
}>()
</script>

<template>
  <!-- @wheel.stop prevents GSAP from turning slides when scrolling inside the map -->
  <figure class="media-shell" :data-variant="panel.mediaVariant" @wheel.stop>
    <ReachabilityMap v-if="panel.mediaVariant === 'reachability-map'" class="interactive-embed" />
    <LausanneReachabilityLab v-else-if="panel.mediaVariant === 'reachability-lab'" class="interactive-embed" />
    <BusiestRailChart v-else-if="panel.mediaVariant === 'busiest-rail'" class="interactive-embed" />
    <RetailDensityMap
      v-else-if="panel.mediaVariant === 'retail-density'"
      class="interactive-embed"
      :preset="panel.mediaPreset"
    />
    <RetailAccessMap
      v-else-if="panel.mediaVariant === 'retail-access'"
      class="interactive-embed"
      :preset="panel.mediaPreset"
    />
  </figure>
</template>

<style scoped>
.media-shell {
  position: relative;
  margin: 0;
  width: 100%;
  height: 100%; 
  min-height: 0;
  overflow: hidden;
  padding: 0;
  display: flex;
}

.interactive-embed {
  width: 100%;
  height: 100%;
}

:deep(.map-wrapper),
:deep(.lab),
:deep(.retail-density),
:deep(.retail-access) {
  width: 100%;
  height: 100%;
  box-sizing: border-box;
}
</style>
