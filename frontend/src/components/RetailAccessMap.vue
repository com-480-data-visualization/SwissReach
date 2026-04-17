<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import * as d3 from 'd3'

import type { StoryMediaPreset } from '@/content/productStory'
import { withBase } from '@/utils/assets'

type MetricMode = 'supermarkets_30min' | 'ikea_60min'

interface StationMetric {
  station_key: string
  station_name: string
  stop_lat: number
  stop_lon: number
  supermarkets_30min: number
  schools_30min: number
  hospitals_30min: number
  ikea_60min: number
  has_ikea_60min: boolean
}

interface SummaryPayload {
  departure_time: string
  station_count: number
  poi_counts: {
    schools: number
    hospitals: number
    ikea: number
    supermarkets: number
  }
  top_supermarket_station_30min: {
    station_name: string
    value: number
  }
}

const props = defineProps<{
  preset: StoryMediaPreset
}>()

const boundary = ref<object | null>(null)
const stations = ref<StationMetric[]>([])
const summary = ref<SummaryPayload | null>(null)
const loading = ref(true)
const loadError = ref(false)
const metricMode = ref<MetricMode>('supermarkets_30min')
const selectedStationKey = ref('')
const tooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  name: '',
  value: '',
})

const boundaryUrl = withBase('/data/swiss_boundary_wgs84.geojson')
const metricsUrl = withBase('/data/story_station_metrics_0800.json')
const summaryUrl = withBase('/data/story_pois_summary.json')

const showControls = computed(() => props.preset === 'retail-access-playground')

const featuredNames = ['Lausanne', 'Zürich HB', 'Bern', 'Genève', 'Basel SBB']

const projection = computed(() => {
  if (!boundary.value) {
    return null
  }
  return d3.geoMercator().fitExtent(
    [[22, 18], [978, 444]],
    boundary.value as any,
  )
})

const boundaryPath = computed(() => {
  if (!projection.value || !boundary.value) {
    return ''
  }
  return d3.geoPath(projection.value)(boundary.value as any) ?? ''
})

const featuredStations = computed(() =>
  featuredNames
    .map(name => stations.value.find(station => station.station_name === name))
    .filter((station): station is StationMetric => Boolean(station)),
)

const selectedStation = computed(
  () => stations.value.find(station => station.station_key === selectedStationKey.value) ?? featuredStations.value[0] ?? null,
)

const metricConfig = computed(() => {
  if (metricMode.value === 'ikea_60min') {
    return {
      label: 'IKEA within 60 min',
      shortLabel: 'IKEA 60 min',
      max: d3.max(stations.value, station => station.ikea_60min) ?? 1,
      formatter: (value: number) => `${value} IKEA`,
      key: 'ikea_60min' as const,
    }
  }

  return {
    label: 'Supermarkets within 30 min',
    shortLabel: 'Supermarkets 30 min',
    max: d3.max(stations.value, station => station.supermarkets_30min) ?? 1,
    formatter: (value: number) => `${value} stores`,
    key: 'supermarkets_30min' as const,
  }
})

const plottedStations = computed(() => {
  if (!projection.value) {
    return []
  }

  return stations.value
    .map(station => {
      const projected = projection.value?.([station.stop_lon, station.stop_lat])
      if (!projected) {
        return null
      }
      const value = station[metricConfig.value.key]
      return {
        ...station,
        value,
        cx: projected[0],
        cy: projected[1],
      }
    })
    .filter((station): station is StationMetric & { value: number; cx: number; cy: number } => station !== null)
})

const selectedValue = computed(() => {
  if (!selectedStation.value) {
    return 'N/A'
  }
  return metricConfig.value.formatter(selectedStation.value[metricConfig.value.key])
})

const topStationLabel = computed(() => {
  if (metricMode.value === 'ikea_60min') {
    const top = [...stations.value].sort((a, b) => b.ikea_60min - a.ikea_60min)[0]
    if (!top) {
      return 'N/A'
    }
    return `${top.station_name} · ${top.ikea_60min}`
  }
  if (!summary.value) {
    return 'N/A'
  }
  return `${summary.value.top_supermarket_station_30min.station_name} · ${summary.value.top_supermarket_station_30min.value}`
})

function colorFor(value: number): string {
  const max = Math.max(metricConfig.value.max, 1)
  return d3.interpolateYlOrRd(0.14 + (value / max) * 0.78)
}

function radiusFor(value: number, stationKey: string): number {
  const base = metricMode.value === 'ikea_60min' ? 1.8 : 1.9
  const scaled = base + Math.sqrt(Math.max(value, 0)) * (metricMode.value === 'ikea_60min' ? 0.48 : 0.34)
  return selectedStationKey.value === stationKey ? scaled + 1.3 : scaled
}

function selectStation(stationKey: string) {
  selectedStationKey.value = stationKey
}

function selectMetric(nextMetric: MetricMode) {
  metricMode.value = nextMetric
}

function showTooltip(event: MouseEvent, station: StationMetric & { value: number }) {
  tooltip.value = {
    visible: true,
    x: event.clientX + 14,
    y: event.clientY - 16,
    name: station.station_name,
    value: metricConfig.value.formatter(station.value),
  }
}

function moveTooltip(event: MouseEvent) {
  tooltip.value.x = event.clientX + 14
  tooltip.value.y = event.clientY - 16
}

function hideTooltip() {
  tooltip.value.visible = false
}

onMounted(async () => {
  if (props.preset === 'retail-access-story') {
    metricMode.value = 'supermarkets_30min'
  }

  try {
    const [boundaryRes, metricsRes, summaryRes] = await Promise.all([
      fetch(boundaryUrl),
      fetch(metricsUrl),
      fetch(summaryUrl),
    ])

    if (!boundaryRes.ok || !metricsRes.ok || !summaryRes.ok) {
      throw new Error('retail access missing')
    }

    const [boundaryJson, metricsJson, summaryJson] = await Promise.all([
      boundaryRes.json(),
      metricsRes.json(),
      summaryRes.json(),
    ])

    boundary.value = boundaryJson
    stations.value = metricsJson
    summary.value = summaryJson

    const defaultName = props.preset === 'retail-access-story' ? 'Lausanne' : 'Zürich HB'
    selectedStationKey.value =
      stations.value.find(station => station.station_name === defaultName)?.station_key ??
      featuredStations.value[0]?.station_key ??
      metricsJson[0]?.station_key ??
      ''
  } catch {
    loadError.value = true
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section class="retail-access section-frame">
    <div class="retail-access__top">
      <div class="retail-access__heading">
        <span class="retail-access__kicker">Retail access</span>
        <h3 class="retail-access__title">What the transport network buys in reachable retail</h3>
        <p class="retail-access__text">
          {{ metricConfig.label }} from a fixed <strong>08:00</strong> national export. The baseline is explicit so the map reads as a comparative product story, not as a live routing promise.
        </p>
      </div>

      <div v-if="showControls" class="retail-access__metric-toggle" role="tablist" aria-label="Retail access metrics">
        <button
          class="retail-pill"
          :class="{ 'is-active': metricMode === 'supermarkets_30min' }"
          type="button"
          @click="selectMetric('supermarkets_30min')"
        >
          Supermarkets
        </button>
        <button
          class="retail-pill"
          :class="{ 'is-active': metricMode === 'ikea_60min' }"
          type="button"
          @click="selectMetric('ikea_60min')"
        >
          IKEA
        </button>
      </div>
    </div>

    <div v-if="showControls" class="retail-access__station-pills" aria-label="Featured stations">
      <button
        v-for="station in featuredStations"
        :key="station.station_key"
        class="retail-pill"
        :class="{ 'is-active': selectedStationKey === station.station_key }"
        type="button"
        @click="selectStation(station.station_key)"
      >
        {{ station.station_name }}
      </button>
    </div>

    <div v-if="loadError" class="retail-access__fallback">
      <p>The retail-access layer could not load. Other sections of the page still work.</p>
    </div>

    <div v-else class="retail-access__map-wrap">
      <div v-if="loading" class="retail-access__loading">Loading retail access…</div>
      <svg v-else class="retail-access__map" viewBox="0 0 1000 462" aria-label="Swiss retail access map">
        <path :d="boundaryPath" class="retail-access__boundary" />
        <circle
          v-for="station in plottedStations"
          :key="station.station_key"
          :cx="station.cx"
          :cy="station.cy"
          :r="radiusFor(station.value, station.station_key)"
          :fill="colorFor(station.value)"
          class="retail-access__point"
          :class="{ 'is-selected': station.station_key === selectedStationKey }"
          @click="selectStation(station.station_key)"
          @mouseenter="showTooltip($event, station)"
          @mousemove="moveTooltip"
          @mouseleave="hideTooltip"
        />
      </svg>
    </div>

    <div class="retail-access__footer">
      <div class="retail-access__legend">
        <span class="legend-text">{{ metricConfig.shortLabel }}</span>
        <span class="legend-ramp" />
        <span class="legend-text">Higher access</span>
      </div>
      <p class="retail-access__note">
        {{ summary?.departure_time ?? '08:00' }} baseline · {{ selectedStation?.station_name ?? 'Station' }}: {{ selectedValue }} · top station: {{ topStationLabel }}
      </p>
    </div>
  </section>

  <div
    v-if="tooltip.visible"
    class="retail-tooltip"
    :style="{ left: `${tooltip.x}px`, top: `${tooltip.y}px` }"
  >
    <strong>{{ tooltip.name }}</strong>
    <span>{{ tooltip.value }}</span>
  </div>
</template>

<style scoped>
.retail-access {
  display: grid;
  grid-template-rows: auto auto minmax(0, 1fr) auto;
  gap: 0.85rem;
  padding: 0.85rem 0.85rem 0.78rem;
  border-radius: var(--radius-shell);
}

.retail-access__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.retail-access__heading {
  max-width: 38rem;
}

.retail-access__kicker {
  color: var(--brand);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.retail-access__title {
  margin: 0.22rem 0 0;
  color: var(--ink-strong);
  font-size: 1.02rem;
  letter-spacing: -0.03em;
}

.retail-access__text {
  margin: 0.32rem 0 0;
  color: var(--ink-soft);
  font-size: 0.82rem;
  line-height: 1.45;
}

.retail-access__metric-toggle,
.retail-access__station-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.retail-pill {
  min-height: 2.2rem;
  padding: 0 0.85rem;
  border-radius: 999px;
  border: 1px solid rgba(33, 28, 26, 0.08);
  background: rgba(255, 255, 255, 0.82);
  color: var(--ink-soft);
  cursor: pointer;
  transition:
    border-color 180ms ease,
    background-color 180ms ease,
    color 180ms ease,
    transform 180ms ease;
}

.retail-pill.is-active {
  border-color: rgba(189, 45, 45, 0.18);
  background: rgba(189, 45, 45, 0.12);
  color: var(--brand);
}

.retail-pill:hover {
  transform: translateY(-1px);
}

.retail-access__map-wrap {
  min-height: 0;
  position: relative;
  border-radius: calc(var(--radius-shell) - 10px);
  overflow: hidden;
  border: 1px solid rgba(33, 28, 26, 0.07);
  background:
    radial-gradient(circle at top, rgba(255, 255, 255, 0.95), rgba(248, 244, 241, 0.96) 58%, rgba(241, 235, 230, 0.98));
  height: 100%;
}

.retail-access__map {
  width: 100%;
  height: 100%;
  display: block;
}

.retail-access__boundary {
  fill: #efe9e2;
  stroke: rgba(117, 103, 96, 0.65);
  stroke-width: 1.1;
}

.retail-access__point {
  cursor: pointer;
  opacity: 0.9;
  stroke: rgba(255, 255, 255, 0.55);
  stroke-width: 0.6;
  transition:
    opacity 120ms ease,
    stroke 120ms ease;
}

.retail-access__point.is-selected {
  stroke: rgba(33, 28, 26, 0.7);
  stroke-width: 1.2;
}

.retail-access__point:hover {
  opacity: 1;
}

.retail-access__footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem;
}

.retail-access__legend {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
}

.legend-text {
  color: var(--ink-soft);
  font-size: 0.78rem;
}

.legend-ramp {
  width: 7rem;
  height: 0.5rem;
  border-radius: 999px;
  background: linear-gradient(90deg, #f4d7b4, #e99a54, #c95529, #9f1d1d);
}

.retail-access__note {
  margin: 0;
  color: var(--ink-soft);
  font-size: 0.8rem;
}

.retail-access__loading,
.retail-access__fallback {
  display: grid;
  place-items: center;
  min-height: 12rem;
  color: var(--ink-soft);
  text-align: center;
}

.retail-tooltip {
  position: fixed;
  z-index: 30;
  display: grid;
  gap: 0.16rem;
  min-width: 10rem;
  padding: 0.72rem 0.82rem;
  border-radius: 16px;
  background: rgba(33, 28, 26, 0.92);
  color: #fff;
  pointer-events: none;
  box-shadow: 0 12px 32px rgba(33, 28, 26, 0.22);
}

.retail-tooltip strong {
  font-size: 0.86rem;
}

.retail-tooltip span {
  font-size: 0.76rem;
  color: rgba(255, 255, 255, 0.78);
}

@media (max-width: 960px) {
  .retail-access__top {
    display: grid;
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .retail-access {
    padding: 0.72rem;
  }

  .retail-access__title {
    font-size: 0.96rem;
  }
}
</style>
