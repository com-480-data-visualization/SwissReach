<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import * as d3 from 'd3'

import type { StoryMediaPreset } from '@/content/productStory'
import { withBase } from '@/utils/assets'

type BrandMode = 'both' | 'migros' | 'coop' | 'difference'

interface StorePoint {
  brand: 'Migros' | 'Coop'
  name: string
  lat: number
  lon: number
  city: string | null
  postcode: string | null
  source_url: string
}

interface HexBin {
  key: string
  q: number
  r: number
  cx: number
  cy: number
  total: number
  migros: number
  coop: number
}

const props = defineProps<{
  preset: StoryMediaPreset
}>()

const HEX_SIZE = 11.5
const SQRT_3 = Math.sqrt(3)
const HEX_ORIGIN_X = 118
const HEX_ORIGIN_Y = 62

const boundary = ref<object | null>(null)
const migrosStores = ref<StorePoint[]>([])
const coopStores = ref<StorePoint[]>([])
const loading = ref(true)
const loadError = ref(false)
const tooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  title: '',
  lines: [] as string[],
})

const boundaryUrl = withBase('/data/swiss_boundary_wgs84.geojson')
const migrosUrl = withBase('/data/migros_stores_min.json')
const coopUrl = withBase('/data/coop_stores_min.json')

const presetMode = computed<BrandMode>(() => {
  if (props.preset === 'brand-story' || props.preset === 'brand-playground') {
    return 'difference'
  }
  return 'both'
})

const showControls = computed(() => props.preset === 'retail-playground' || props.preset === 'brand-playground')
const brandMode = ref<BrandMode>(presetMode.value)

const allStores = computed(() => [...migrosStores.value, ...coopStores.value])

const projection = computed(() => {
  if (!boundary.value) {
    return null
  }
  return d3.geoMercator().fitExtent(
    [[22, 18], [978, 446]],
    boundary.value as any,
  )
})

const boundaryPath = computed(() => {
  if (!projection.value || !boundary.value) {
    return ''
  }
  return d3.geoPath(projection.value)(boundary.value as any) ?? ''
})

const plottedStores = computed(() => {
  if (!projection.value) {
    return []
  }

  return allStores.value
    .map(store => {
      const projected = projection.value?.([store.lon, store.lat])
      if (!projected) {
        return null
      }
      return {
        ...store,
        cx: projected[0],
        cy: projected[1],
      }
    })
    .filter((item): item is StorePoint & { cx: number; cy: number } => item !== null)
})

const displayedCount = computed(() => {
  if (brandMode.value === 'migros') {
    return migrosStores.value.length
  }
  if (brandMode.value === 'coop') {
    return coopStores.value.length
  }
  return allStores.value.length
})

const totalCount = computed(() => allStores.value.length)
const migrosShare = computed(() => {
  if (!totalCount.value) {
    return '0%'
  }
  return `${Math.round((migrosStores.value.length / totalCount.value) * 100)}%`
})
const coopShare = computed(() => {
  if (!totalCount.value) {
    return '0%'
  }
  return `${Math.round((coopStores.value.length / totalCount.value) * 100)}%`
})

const mapTitle = computed(() => {
  if (props.preset === 'brand-story' || props.preset === 'brand-playground') {
    return 'Brand contrast'
  }
  return 'Retail footprint'
})

const mapNote = computed(() => {
  if (brandMode.value === 'difference') {
    return 'Hex cells show where one supermarket network outweighs the other, instead of forcing both brands into the same point cloud.'
  }
  if (brandMode.value === 'both') {
    return 'Hex cells summarize the shared Swiss supermarket footprint so clusters read at a glance.'
  }
  return `Hex cells isolate the ${brandMode.value === 'migros' ? 'Migros' : 'Coop'} network without losing the national pattern.`
})

function pixelToAxial(x: number, y: number) {
  const localX = x - HEX_ORIGIN_X
  const localY = y - HEX_ORIGIN_Y
  const q = ((SQRT_3 / 3) * localX - localY / 3) / HEX_SIZE
  const r = ((2 / 3) * localY) / HEX_SIZE
  return { q, r }
}

function axialRound(q: number, r: number) {
  const x = q
  const z = r
  const y = -x - z

  let rx = Math.round(x)
  let ry = Math.round(y)
  let rz = Math.round(z)

  const xDiff = Math.abs(rx - x)
  const yDiff = Math.abs(ry - y)
  const zDiff = Math.abs(rz - z)

  if (xDiff > yDiff && xDiff > zDiff) {
    rx = -ry - rz
  } else if (yDiff > zDiff) {
    ry = -rx - rz
  } else {
    rz = -rx - ry
  }

  return { q: rx, r: rz }
}

function axialToPixel(q: number, r: number) {
  const x = HEX_SIZE * SQRT_3 * (q + r / 2) + HEX_ORIGIN_X
  const y = HEX_SIZE * 1.5 * r + HEX_ORIGIN_Y
  return { x, y }
}

function hexPath(cx: number, cy: number) {
  const points = Array.from({ length: 6 }, (_, index) => {
    const angle = ((60 * index - 30) * Math.PI) / 180
    const x = cx + HEX_SIZE * Math.cos(angle)
    const y = cy + HEX_SIZE * Math.sin(angle)
    return `${x},${y}`
  })
  return `M${points.join(' L')} Z`
}

const hexBins = computed<HexBin[]>(() => {
  const bins = new Map<string, HexBin>()

  for (const store of plottedStores.value) {
    const axial = pixelToAxial(store.cx, store.cy)
    const rounded = axialRound(axial.q, axial.r)
    const key = `${rounded.q},${rounded.r}`
    const existing = bins.get(key)

    if (existing) {
      existing.total += 1
      if (store.brand === 'Migros') {
        existing.migros += 1
      } else {
        existing.coop += 1
      }
      continue
    }

    const center = axialToPixel(rounded.q, rounded.r)
    bins.set(key, {
      key,
      q: rounded.q,
      r: rounded.r,
      cx: center.x,
      cy: center.y,
      total: 1,
      migros: store.brand === 'Migros' ? 1 : 0,
      coop: store.brand === 'Coop' ? 1 : 0,
    })
  }

  return [...bins.values()]
})

const maxBinTotal = computed(() => d3.max(hexBins.value, bin => bin.total) ?? 1)
const maxBinDiff = computed(() => d3.max(hexBins.value, bin => Math.abs(bin.migros - bin.coop)) ?? 1)

function fillFor(bin: HexBin): string {
  if (brandMode.value === 'difference') {
    const diff = bin.migros - bin.coop
    if (diff === 0) {
      return 'rgba(161, 145, 128, 0.52)'
    }
    const strength = Math.abs(diff) / Math.max(maxBinDiff.value, 1)
    return diff > 0
      ? d3.interpolateRgb('rgba(246,226,220,0.76)', 'rgba(189,45,45,0.92)')(0.28 + strength * 0.72)
      : d3.interpolateRgb('rgba(241,232,210,0.78)', 'rgba(180,126,26,0.96)')(0.28 + strength * 0.72)
  }

  const intensity = bin.total / Math.max(maxBinTotal.value, 1)
  if (brandMode.value === 'migros') {
    return d3.interpolateRgb('rgba(248,228,223,0.74)', 'rgba(189,45,45,0.94)')(0.22 + intensity * 0.78)
  }
  if (brandMode.value === 'coop') {
    return d3.interpolateRgb('rgba(243,235,214,0.76)', 'rgba(180,126,26,0.96)')(0.22 + intensity * 0.78)
  }
  return d3.interpolateRgb('rgba(247,238,226,0.72)', 'rgba(145,97,33,0.96)')(0.2 + intensity * 0.8)
}

function strokeFor(bin: HexBin): string {
  if (brandMode.value === 'difference') {
    if (bin.migros === bin.coop) {
      return 'rgba(122, 111, 100, 0.3)'
    }
    return bin.migros > bin.coop ? 'rgba(151, 31, 31, 0.62)' : 'rgba(142, 96, 18, 0.62)'
  }
  return 'rgba(88, 73, 62, 0.22)'
}

function showTooltip(event: MouseEvent, bin: HexBin) {
  const lines =
    brandMode.value === 'difference'
      ? [`Migros ${bin.migros}`, `Coop ${bin.coop}`, `Difference ${Math.abs(bin.migros - bin.coop)}`]
      : [`Total ${bin.total}`, `Migros ${bin.migros}`, `Coop ${bin.coop}`]

  tooltip.value = {
    visible: true,
    x: event.clientX + 14,
    y: event.clientY - 16,
    title: brandMode.value === 'difference' ? 'Brand balance' : 'Store density',
    lines,
  }
}

function moveTooltip(event: MouseEvent) {
  tooltip.value.x = event.clientX + 14
  tooltip.value.y = event.clientY - 16
}

function hideTooltip() {
  tooltip.value.visible = false
}

function setBrandMode(nextMode: BrandMode) {
  brandMode.value = nextMode
}

onMounted(async () => {
  brandMode.value = presetMode.value

  try {
    const [boundaryRes, migrosRes, coopRes] = await Promise.all([
      fetch(boundaryUrl),
      fetch(migrosUrl),
      fetch(coopUrl),
    ])

    if (!boundaryRes.ok || !migrosRes.ok || !coopRes.ok) {
      throw new Error('retail data missing')
    }

    const [boundaryJson, migrosJson, coopJson] = await Promise.all([
      boundaryRes.json(),
      migrosRes.json(),
      coopRes.json(),
    ])

    boundary.value = boundaryJson
    migrosStores.value = migrosJson
    coopStores.value = coopJson
  } catch {
    loadError.value = true
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section class="retail-density section-frame">
    <div class="retail-density__top">
      <div class="retail-density__heading">
        <span class="retail-density__kicker">{{ mapTitle }}</span>
        <h3 class="retail-density__title">Retail density in Switzerland</h3>
        <p class="retail-density__text">{{ mapNote }}</p>
      </div>

      <div v-if="showControls" class="retail-density__controls" role="tablist" aria-label="Brand filters">
        <button class="retail-pill" :class="{ 'is-active': brandMode === 'both' }" type="button" @click="setBrandMode('both')">
          Both
        </button>
        <button class="retail-pill" :class="{ 'is-active': brandMode === 'migros' }" type="button" @click="setBrandMode('migros')">
          Migros
        </button>
        <button class="retail-pill" :class="{ 'is-active': brandMode === 'coop' }" type="button" @click="setBrandMode('coop')">
          Coop
        </button>
        <button
          v-if="preset === 'brand-playground'"
          class="retail-pill"
          :class="{ 'is-active': brandMode === 'difference' }"
          type="button"
          @click="setBrandMode('difference')"
        >
          Difference
        </button>
      </div>
    </div>

    <div v-if="loadError" class="retail-density__fallback">
      <p>The retail footprint could not load. The rest of the story remains available.</p>
    </div>

    <div v-else class="retail-density__map-wrap">
      <div v-if="loading" class="retail-density__loading">Loading retail footprint…</div>
      <svg v-else class="retail-density__map" viewBox="0 0 1000 464" aria-label="Swiss retail density hex map">
        <path :d="boundaryPath" class="retail-density__boundary" />
        <path
          v-for="bin in hexBins"
          :key="bin.key"
          :d="hexPath(bin.cx, bin.cy)"
          :fill="fillFor(bin)"
          :stroke="strokeFor(bin)"
          class="retail-density__hex"
          @mouseenter="showTooltip($event, bin)"
          @mousemove="moveTooltip"
          @mouseleave="hideTooltip"
        />
      </svg>
    </div>

    <div class="retail-density__legend">
      <span class="legend-chip"><i class="legend-dot legend-dot--migros" /> Migros</span>
      <span class="legend-chip"><i class="legend-dot legend-dot--coop" /> Coop</span>
      <span v-if="brandMode === 'difference'" class="legend-chip"><i class="legend-dot legend-dot--neutral" /> Balanced</span>
      <span class="legend-text">{{ displayedCount }} stores · {{ hexBins.length }} hex cells · Migros {{ migrosShare }} · Coop {{ coopShare }}</span>
    </div>
  </section>

  <div
    v-if="tooltip.visible"
    class="retail-tooltip"
    :style="{ left: `${tooltip.x}px`, top: `${tooltip.y}px` }"
  >
    <strong>{{ tooltip.title }}</strong>
    <span v-for="line in tooltip.lines" :key="line">{{ line }}</span>
  </div>
</template>

<style scoped>
.retail-density {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  gap: 0.9rem;
  padding: 0.85rem 0.85rem 0.75rem;
  border-radius: var(--radius-shell);
}

.retail-density__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.retail-density__heading {
  max-width: 34rem;
}

.retail-density__kicker {
  color: var(--brand);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.retail-density__title {
  margin: 0.22rem 0 0;
  color: var(--ink-strong);
  font-size: 1.02rem;
  letter-spacing: -0.03em;
}

.retail-density__text {
  margin: 0.32rem 0 0;
  color: var(--ink-soft);
  font-size: 0.82rem;
  line-height: 1.45;
}

.retail-density__controls {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: flex-end;
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

.retail-density__map-wrap {
  min-height: 0;
  position: relative;
  border-radius: calc(var(--radius-shell) - 10px);
  overflow: hidden;
  border: 1px solid rgba(33, 28, 26, 0.07);
  background:
    radial-gradient(circle at top, rgba(255, 255, 255, 0.95), rgba(248, 244, 241, 0.96) 58%, rgba(241, 235, 230, 0.98));
  height: 100%;
}

.retail-density__map {
  width: 100%;
  height: 100%;
  display: block;
}

.retail-density__boundary {
  fill: #f4efe9;
  stroke: rgba(117, 103, 96, 0.6);
  stroke-width: 1.15;
}

.retail-density__hex {
  transition:
    transform 120ms ease,
    opacity 120ms ease,
    stroke 120ms ease;
  opacity: 0.96;
  stroke-width: 0.8;
}

.retail-density__hex:hover {
  opacity: 1;
  stroke: rgba(33, 28, 26, 0.66);
}

.retail-density__legend {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.8rem;
}

.legend-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.42rem;
  color: var(--ink);
  font-size: 0.8rem;
}

.legend-dot {
  width: 0.65rem;
  height: 0.65rem;
  border-radius: 999px;
}

.legend-dot--migros {
  background: rgba(189, 45, 45, 0.92);
}

.legend-dot--coop {
  background: rgba(180, 126, 26, 0.92);
}

.legend-dot--neutral {
  background: rgba(161, 145, 128, 0.9);
}

.legend-text {
  color: var(--ink-soft);
  font-size: 0.78rem;
}

.retail-density__loading,
.retail-density__fallback {
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
  .retail-density__top {
    display: grid;
    grid-template-columns: 1fr;
  }

  .retail-density__controls {
    justify-content: flex-start;
  }
}

@media (max-width: 720px) {
  .retail-density {
    padding: 0.72rem;
  }

  .retail-density__title {
    font-size: 0.96rem;
  }
}
</style>
