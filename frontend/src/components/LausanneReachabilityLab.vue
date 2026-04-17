<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import * as d3 from 'd3'

interface Station {
  station_key: string
  station_name: string
  lat: number
  lon: number
  travel_minutes: number | null
}

/** Departure times (minutes from midnight) that have a matching map on the server. */
const DEPARTURES_MIN = [360, 480, 720, 1080] as const

const depIndex = ref(1)
const depMinutes = computed(() => DEPARTURES_MIN[depIndex.value]!)

const windowMinutes = ref(360)

const loading = ref(false)
const error = ref(false)
const stations = ref<Station[]>([])
const boundary = ref<object | null>(null)
const tooltip = ref({ visible: false, x: 0, y: 0, name: '', raw: null as number | null, inWindow: true })

const svgRef = ref<SVGSVGElement | null>(null)
let currentTransform = d3.zoomIdentity
let zoomBehavior: d3.ZoomBehavior<SVGSVGElement, unknown> | null = null

const VB_W = 1000
const VB_H = 560

const dataBase = `${import.meta.env.BASE_URL}data/`.replace(/\/{2,}/g, '/')

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
  error.value = false
  try {
    const tag = depFileTag(depMinutes.value)
    const res = await fetch(`${dataBase}reachability_lausanne_${tag}.json`)
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
    const res = await fetch(`${dataBase}swiss_boundary_wgs84.geojson`)
    if (res.ok) boundary.value = await res.json()
  } catch {
    /* optional */
  }
}

function draw() {
  if (!svgRef.value || stations.value.length === 0) return

  const win = windowMinutes.value
  const svg = d3.select(svgRef.value)
  svg.selectAll('*').remove()

  let projection: d3.GeoProjection
  /* Extra inset so northern/southern stops are not flush against the frame. */
  const padX = 58
  const padY = 50
  if (boundary.value) {
    projection = d3.geoMercator().fitExtent(
      [[padX, padY], [VB_W - padX, VB_H - padY]],
      boundary.value as any,
    )
  } else {
    projection = d3.geoMercator()
      .scale(9000)
      .center([8.23, 46.825])
      .translate([VB_W / 2, VB_H / 2])
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
    .translateExtent([[0, 0], [VB_W, VB_H]])
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

onMounted(async () => {
  await Promise.all([loadStations(), loadBoundary()])
  await nextTick()
  draw()
})

watch(depIndex, async () => {
  await loadStations()
  await nextTick()
  draw()
})

watch([windowMinutes, stations, boundary], async () => {
  await nextTick()
  draw()
})
</script>

<template>
  <div class="lab">
    <div class="lab-heading">
      <span class="lab-kicker">Lausanne</span>
      <h3 class="lab-title">Departure &amp; window</h3>
      <p class="lab-lead">
        Stay in Lausanne. Slide <strong>when you leave</strong> — dawn, coffee time, noon, or the evening rush —
        and watch the country repaint itself. Then tighten or loosen <strong>how much time you are willing to
        spend</strong>: inside that budget the dots stay warm; anything that would take longer quietly steps back
        into the fog.
      </p>
    </div>

    <div class="lab-controls">
      <div class="lab-slider-block">
        <span class="lab-label">Departure</span>
        <input
          v-model.number="depIndex"
          type="range"
          class="lab-range"
          min="0"
          max="3"
          step="1"
        >
        <div class="lab-slider-meta">
          <span class="lab-pill">{{ depLabel(depMinutes) }}</span>
          <span class="lab-hint">06:00 · 08:00 · 12:00 · 18:00</span>
        </div>
      </div>

      <div class="lab-slider-block">
        <span class="lab-label">Window</span>
        <input
          v-model.number="windowMinutes"
          type="range"
          class="lab-range"
          min="30"
          max="360"
          step="15"
        >
        <div class="lab-slider-meta">
          <span class="lab-pill">{{ windowLabel(windowMinutes) }}</span>
          <span class="lab-hint">up to six hours on the map</span>
        </div>
      </div>

      <div class="lab-controls-right">
        <button type="button" class="lab-reset" @click="resetZoom">⊙ Reset</button>
        <span v-if="loading" class="lab-loading">Loading…</span>
      </div>
    </div>

    <p class="lab-status">
      Departure {{ depLabel(depMinutes) }} · window {{ windowLabel(windowMinutes) }} · reachable in window
      <strong>{{ reachableStats.inWindow }}</strong>
      <span class="lab-status-muted">/ {{ reachableStats.total }} stations</span>
      <span v-if="reachableStats.rawReach < reachableStats.total" class="lab-status-muted">
        · {{ reachableStats.rawReach }} stations reachable within six hours on this map
      </span>
    </p>

    <div class="lab-map-card">
      <div class="lab-map">
        <div v-if="error" class="lab-empty">
          <p>This Lausanne map couldn’t load. Check your connection and try a refresh.</p>
        </div>
        <svg
          v-else
          ref="svgRef"
          class="lab-svg"
          :viewBox="`0 0 ${VB_W} ${VB_H}`"
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
          Beyond your time limit
        </div>
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
.lab {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.lab-heading {
  max-width: 70ch;
}

.lab-kicker {
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: #c84f56;
}

.lab-title {
  margin: 6px 0 0;
  font-family: var(--swissreach-font-sans);
  font-size: 1.22rem;
  font-weight: 700;
  color: #1a1415;
}

.lab-lead {
  margin: 8px 0 0;
  font-size: 0.88rem;
  line-height: 1.55;
  color: #6b5c5e;
}

.lab-controls {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px 32px;
  align-items: end;
}

.lab-slider-block {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.lab-label {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #9a787c;
}

.lab-range {
  width: 100%;
  accent-color: #b8444b;
  height: 6px;
}

.lab-slider-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.lab-pill {
  display: inline-block;
  padding: 4px 11px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
  color: #5c2a2e;
  background: rgba(200, 79, 86, 0.1);
  border: 1px solid rgba(184, 68, 75, 0.16);
}

.lab-hint {
  font-size: 0.76rem;
  color: #9a8588;
}

.lab-controls-right {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 6px;
}

.lab-reset {
  flex-shrink: 0;
  padding: 7px 14px;
  border: 1px solid rgba(184, 68, 75, 0.22);
  border-radius: 8px;
  font-size: 0.85rem;
  background: white;
  color: #7a3136;
  cursor: pointer;
}

.lab-reset:hover {
  background: rgba(200, 79, 86, 0.07);
}

.lab-loading {
  font-size: 0.82rem;
  color: #7a4b4f;
  font-style: italic;
}

.lab-status {
  margin: 0 0 4px;
  padding: 6px 6px 12px;
  font-size: 0.82rem;
  color: #5b4b4d;
  line-height: 1.55;
}

.lab-status-muted {
  color: #9a8588;
  font-weight: 400;
}

.lab-map-card {
  border-radius: 16px;
  overflow: hidden;
  background: #e4e9f0;
  box-sizing: border-box;
}

.lab-map {
  padding: 14px 16px 8px;
  box-sizing: border-box;
  background: #d8dfe8;
  display: flex;
  flex-direction: column;
}

.lab-svg {
  display: block;
  width: 100%;
  flex: 1;
  min-height: 0;
  border-radius: 10px;
}

.lab-empty {
  min-height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #7a4b4f;
  font-size: 0.9rem;
}

.lab-legend {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 14px 22px;
  row-gap: 12px;
  font-size: 0.82rem;
  color: #5b4b4d;
  padding: 12px 18px 16px;
  background: rgba(255, 253, 252, 0.92);
}

.lab-legend-title {
  font-weight: 600;
  flex: 1 1 12rem;
  min-width: 0;
}

.lab-gradient-wrap {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1 1 200px;
  min-width: min(200px, 100%);
  max-width: 280px;
}

.lab-gradient {
  width: 100%;
  max-width: 260px;
  height: 10px;
  border-radius: 5px;
  background: linear-gradient(to right, #800026, #e31a1c, #fd8d3c, #feb24c, #ffffcc);
}

.lab-ticks {
  display: flex;
  justify-content: space-between;
  width: 100%;
  max-width: 260px;
  font-size: 0.76rem;
  color: #8a7070;
}

.lab-unreach {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1 1 200px;
  min-width: 0;
  padding-right: 4px;
  line-height: 1.35;
}

@media (max-width: 640px) {
  .lab-controls {
    grid-template-columns: 1fr;
  }
}

.lab-swatch {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ccc8c8;
}
</style>
