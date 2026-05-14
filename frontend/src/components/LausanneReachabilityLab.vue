<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as d3 from 'd3'

import { withBase } from '@/utils/assets'

interface Station {
  station_key: string
  station_name: string
  lat: number
  lon: number
  travel_minutes: number | null
}

/** Departure times (minutes from midnight) that have a matching map on the server. */
const MIN_DEPARTURE = 5 * 60
const MAX_DEPARTURE = 22 * 60

const requestedDepMinutes = ref(480)

const windowMinutes = ref(360)

const loading = ref(false)
const mapReady = ref(false)
const error = ref(false)
const stations = ref<Station[]>([])
const boundary = ref<object | null>(null)
const tooltip = ref({ visible: false, x: 0, y: 0, name: '', raw: null as number | null, inWindow: true })

const svgRef = ref<SVGSVGElement | null>(null)
const skeletonUrl = withBase('/data/swiss_boundary_skeleton.svg')
let currentTransform = d3.zoomIdentity
let zoomBehavior: d3.ZoomBehavior<SVGSVGElement, unknown> | null = null

const vbWidth = ref(1000)
const vbHeight = ref(560)
let resizeObserver: ResizeObserver | null = null

function waitForPaint(): Promise<void> {
  return new Promise(resolve => {
    requestAnimationFrame(() => resolve())
  })
}

function depLabel(m: number): string {
  const h = Math.floor(m / 60)
  const min = m % 60
  return `${String(h).padStart(2, '0')}:${String(min).padStart(2, '0')}`
}

function depFileTag(m: number): string {
  return `${String(Math.floor(m / 60)).padStart(2, '0')}${String(m % 60).padStart(2, '0')}`
}

function windowLabel(m: number): string {
  if (m < 60) return `${m} min`
  const h = Math.floor(m / 60)
  const r = m % 60
  if (r === 0) return `${h} h`
  return `${h} h ${r} min`
}

/** Raw graph time from JSON (6 h search). */
function rawMinutes(d: Station): number | null {
  return d.travel_minutes
}

/** Whether station is reachable within the user-chosen time budget (subset of 6 h results). */
function inWindow(d: Station, win: number): boolean {
  const t = rawMinutes(d)
  if (t === null) return false
  return t <= win
}

function displayMinutes(d: Station, win: number): number | null {
  const t = rawMinutes(d)
  if (t === null) return null
  if (t > win) return null
  return t
}

function stationColor(t: number | null, win: number): string {
  if (t === null) return '#ccc8c8'
  return d3.interpolateYlOrRd(1 - t / win)
}

function formatTime(minutes: number | null): string {
  if (minutes === null) return 'Not in window'
  if (minutes === 0) return 'Lausanne'
  const h = Math.floor(minutes / 60)
  const m = Math.round(minutes % 60)
  if (h === 0) return `${m} min`
  if (m === 0) return `${h}h`
  return `${h}h ${m}min`
}

function baseR(d: Station, win: number) {
  const t = displayMinutes(d, win)
  return t === 0 ? 6 : 2.5
}

function hoverR(d: Station, win: number) {
  const t = displayMinutes(d, win)
  return t === 0 ? 8 : 5
}

const reachableStats = computed(() => {
  const win = windowMinutes.value
  let inW = 0
  let rawReach = 0
  for (const s of stations.value) {
    const t = rawMinutes(s)
    if (t !== null) rawReach++
    if (t !== null && t <= win) inW++
  }
  return { inWindow: inW, rawReach, total: stations.value.length }
})

async function loadStations() {
  loading.value = true
  mapReady.value = false
  error.value = false
  try {
    const tag = depFileTag(requestedDepMinutes.value)
    const res = await fetch(withBase(`/data/reachability_lausanne_${tag}.json`))
    if (!res.ok) throw new Error('not found')
    stations.value = await res.json()
    currentTransform = d3.zoomIdentity
  } catch {
    error.value = true
    stations.value = []
  } finally {
    loading.value = false
  }
}

async function loadBoundary() {
  try {
    const res = await fetch(withBase('/data/swiss_boundary_wgs84.geojson'))
    if (res.ok) boundary.value = await res.json()
  } catch {
    boundary.value = null
  }
}

function draw() {
  if (!svgRef.value || stations.value.length === 0) return

  const win = windowMinutes.value
  const svg = d3.select(svgRef.value)
  svg.selectAll('*').remove()

  let projection: d3.GeoProjection
  /* Extra inset so northern/southern stops are not flush against the frame. */
  const padX = 24
  const padY = 24
  if (boundary.value) {
    projection = d3.geoMercator().fitExtent(
      [[padX, padY], [vbWidth.value - padX, vbHeight.value - padY]],
      boundary.value as any,
    )
  } else {
    projection = d3.geoMercator()
      .scale(9000)
      .center([8.23, 46.825])
      .translate([vbWidth.value / 2, vbHeight.value / 2])
  }

  const k = currentTransform.k
  const g = svg.append('g').attr('class', 'zoom-layer').attr('transform', currentTransform.toString())

  if (boundary.value) {
    const pathGen = d3.geoPath(projection)
    g.append('path')
      .datum(boundary.value as any)
      .attr('d', pathGen as any)
      .attr('fill', '#eef0eb')
      .attr('stroke', '#a0a890')
      .attr('stroke-width', 1 / k)
      .style('pointer-events', 'none')
  }

  const sorted = [...stations.value].sort((a, b) => {
    const ta = displayMinutes(a, win)
    const tb = displayMinutes(b, win)
    if (ta === null && tb !== null) return -1
    if (ta !== null && tb === null) return 1
    return (tb ?? 0) - (ta ?? 0)
  })

  g.selectAll<SVGCircleElement, Station>('circle')
    .data(sorted, d => d.station_key)
    .join('circle')
    .attr('cx', d => projection([d.lon, d.lat])![0])
    .attr('cy', d => projection([d.lon, d.lat])![1])
    .attr('r', d => baseR(d, win) / k)
    .attr('fill', d => stationColor(displayMinutes(d, win), win))
    .attr('opacity', d => (displayMinutes(d, win) === null ? 0.35 : 0.9))
    .attr('stroke', d => (displayMinutes(d, win) === 0 ? 'white' : 'none'))
    .attr('stroke-width', 1.5 / k)
    .style('cursor', 'pointer')
    .on('mouseenter', (event: MouseEvent, d: Station) => {
      const raw = rawMinutes(d)
      const inside = raw !== null && raw <= win
      d3.select(event.currentTarget as SVGCircleElement)
        .raise()
        .attr('r', hoverR(d, win) / currentTransform.k)
        .attr('opacity', 1)
      tooltip.value = {
        visible: true,
        x: event.clientX + 14,
        y: event.clientY - 10,
        name: d.station_name,
        raw,
        inWindow: inside,
      }
    })
    .on('mousemove', (event: MouseEvent) => {
      tooltip.value.x = event.clientX + 14
      tooltip.value.y = event.clientY - 10
    })
    .on('mouseleave', (event: MouseEvent, d: Station) => {
      d3.select(event.currentTarget as SVGCircleElement)
        .attr('r', baseR(d, win) / currentTransform.k)
        .attr('opacity', displayMinutes(d, win) === null ? 0.35 : 0.9)
      tooltip.value.visible = false
    })

  zoomBehavior = d3.zoom<SVGSVGElement, unknown>()
    .scaleExtent([1, 20])
    .on('zoom', (event: d3.D3ZoomEvent<SVGSVGElement, unknown>) => {
      currentTransform = event.transform
      const zg = d3.select(svgRef.value!).select<SVGGElement>('g.zoom-layer')
      zg.attr('transform', event.transform.toString())
      const kz = event.transform.k
      zg.selectAll<SVGCircleElement, Station>('circle')
        .attr('r', (d: Station) => baseR(d, win) / kz)
        .attr('stroke-width', (d: Station) => (displayMinutes(d, win) === 0 ? 1.5 / kz : 0))
      zg.select('path').attr('stroke-width', 1 / kz)
    })

  d3.select(svgRef.value).call(zoomBehavior)
  d3.select(svgRef.value).call(zoomBehavior.transform, currentTransform)
}

function resetZoom() {
  if (!svgRef.value || !zoomBehavior) return
  currentTransform = d3.zoomIdentity
  d3.select(svgRef.value).transition().duration(350).call(zoomBehavior.transform, d3.zoomIdentity)
}

async function revealMap() {
  if (error.value || stations.value.length === 0) {
    mapReady.value = false
    return
  }
  draw()
  await waitForPaint()
  mapReady.value = true
}

onMounted(async () => {
  await Promise.all([loadStations(), loadBoundary()])
  await nextTick()
  
  if (svgRef.value && svgRef.value.parentElement) {
    resizeObserver = new ResizeObserver((entries) => {
      const entry = entries[0]
      if (entry) {
        vbWidth.value = Math.round(entry.contentRect.width) || 1000
        vbHeight.value = Math.round(entry.contentRect.height) || 560
        if (stations.value.length > 0 && !error.value) {
          draw()
        }
      }
    })
    resizeObserver.observe(svgRef.value.parentElement)
  }
  await revealMap()
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
})

watch(requestedDepMinutes, async () => {
  await loadStations()
  await nextTick()
  await revealMap()
})

watch([windowMinutes, stations, boundary], async () => {
  if (!mapReady.value || loading.value || error.value || stations.value.length === 0) return
  await nextTick()
  draw()
})
</script>

<template>
  <div class="lab-wrapper">
    <div class="lab-controls">
      <label class="lab-control-group">
        <span class="lab-label">Departure</span>
        <input
          v-model.number="requestedDepMinutes"
          type="range"
          class="lab-range lab-range--departure"
          :min="MIN_DEPARTURE"
          :max="MAX_DEPARTURE"
          step="15"
        >
        <span class="lab-pill">{{ depLabel(requestedDepMinutes) }}</span>
      </label>

      <label class="lab-control-group">
        <span class="lab-label">Window</span>
        <input v-model.number="windowMinutes" type="range" class="lab-range" min="30" max="360" step="15">
        <span class="lab-pill">{{ windowLabel(windowMinutes) }}</span>
      </label>

      <span v-if="loading" class="lab-loading">Loading…</span>

      <div class="lab-controls-right">
        <button type="button" class="lab-reset" @click="resetZoom" title="Reset zoom">⊙ Reset</button>
      </div>
    </div>

    <div class="lab-map-container">
      <div v-if="!error && (!mapReady || loading)" class="lab-skeleton" aria-hidden="true">
        <img :src="skeletonUrl" alt="" class="lab-skeleton__outline" />
      </div>
      <div v-if="error" class="lab-empty">
        <p>This Lausanne map couldn’t load. Check your connection and try a refresh.</p>
      </div>
      <svg
        v-else
        ref="svgRef"
        class="lab-svg"
        :class="{ 'is-ready': mapReady && !loading }"
        :viewBox="`0 0 ${vbWidth} ${vbHeight}`"
        overflow="hidden"
      />
    </div>

    <div class="lab-legend">
      <span class="lab-legend-title">Travel time (≤ {{ windowLabel(windowMinutes) }})</span>
      <div class="lab-gradient-wrap">
        <div class="lab-gradient" />
        <div class="lab-ticks">
          <span>0</span>
          <span>{{ windowLabel(Math.round(windowMinutes / 2)) }}</span>
          <span>{{ windowLabel(windowMinutes) }}</span>
        </div>
      </div>
      <div class="lab-unreach">
        <span class="lab-swatch" />
        Unreachable
      </div>
      <div class="lab-status-mini" v-if="reachableStats.total > 0">
        Reachable: <strong>{{ reachableStats.inWindow }}</strong> / {{ reachableStats.total }}
      </div>
    </div>

    <Teleport to="body">
      <div
        v-if="tooltip.visible"
        :style="{
          position: 'fixed',
          left: tooltip.x + 'px',
          top: tooltip.y + 'px',
          background: 'white',
          border: '1px solid rgba(184,68,75,0.18)',
          borderRadius: '10px',
          padding: '8px 13px',
          pointerEvents: 'none',
          boxShadow: '0 4px 18px rgba(64,24,26,0.13)',
          zIndex: 9999,
          fontSize: '0.84rem',
          color: '#271f20',
          minWidth: '140px',
        }"
      >
        <div style="font-weight: 700; margin-bottom: 2px">{{ tooltip.name }}</div>
        <div style="color: #7a4b4f">
          <template v-if="tooltip.raw === null">No train within six hours in this view</template>
          <template v-else>
            About {{ formatTime(tooltip.raw) }} from Lausanne by rail
            <span v-if="!tooltip.inWindow" style="display: block; margin-top: 4px; font-size: 0.78rem">
              Longer than the time you set — shown grey on the map
            </span>
          </template>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.lab-wrapper {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 22px clamp(18px, 2.5vw, 28px) 24px;
  height: 100%;
}

.lab-controls {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.lab-control-group {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.92rem;
}

.lab-label {
  font-weight: 600;
  color: #5b4b4d;
}

.lab-range {
  width: 120px;
  accent-color: #b8444b;
  height: 6px;
}

.lab-range--departure {
  width: clamp(120px, 14vw, 190px);
}

.lab-pill {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
  color: #5c2a2e;
  background: rgba(200, 79, 86, 0.1);
  border: 1px solid rgba(184, 68, 75, 0.16);
  min-width: 48px;
  text-align: center;
}

.lab-controls-right {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: auto;
}

.lab-reset {
  padding: 5px 12px;
  border: 1px solid rgba(184, 68, 75, 0.22);
  border-radius: 8px;
  font-size: 0.85rem;
  background: white;
  color: #7a3136;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}

.lab-reset:hover {
  background: rgba(200, 79, 86, 0.07);
  border-color: #c84f56;
}

.lab-loading {
  font-size: 0.82rem;
  color: #7a4b4f;
  font-style: italic;
}

.lab-map-container {
  position: relative;
  width: 100%;
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  border-radius: 14px;
  overflow: hidden;
  background: #d8dfe8;
}

.lab-svg {
  display: block;
  width: 100%;
  flex: 1;
  min-height: 0;
  opacity: 0;
  transition: opacity 180ms ease;
}

.lab-svg.is-ready {
  opacity: 1;
}

.lab-skeleton {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: stretch;
  justify-content: stretch;
  background: #d8dfe8;
  z-index: 1;
}

.lab-skeleton__outline {
  width: 100%;
  height: 100%;
}

.lab-skeleton__land {
  fill: rgba(255, 255, 255, 0.52);
  stroke: rgba(125, 138, 122, 0.7);
  stroke-width: 1.25;
}

.lab-empty {
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #7a4b4f;
  font-size: 0.9rem;
}

.lab-legend {
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
  font-size: 0.84rem;
  color: #5b4b4d;
}

.lab-legend-title {
  font-weight: 600;
  white-space: nowrap;
}

.lab-gradient-wrap {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.lab-gradient {
  width: 180px;
  height: 10px;
  border-radius: 5px;
  background: linear-gradient(to right, #800026, #e31a1c, #fd8d3c, #feb24c, #ffffcc);
}

.lab-ticks {
  display: flex;
  justify-content: space-between;
  width: 180px;
  font-size: 0.78rem;
  color: #8a7070;
}

.lab-unreach {
  display: flex;
  align-items: center;
  gap: 6px;
}

.lab-swatch {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ccc8c8;
}

.lab-status-mini {
  margin-left: auto;
  font-size: 0.82rem;
  color: #7a4b4f;
}
</style>
