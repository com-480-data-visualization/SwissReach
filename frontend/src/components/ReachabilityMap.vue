<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import * as d3 from 'd3'

interface Station {
  station_key: string
  station_name: string
  lat: number
  lon: number
  travel_minutes: number | null
}

const ORIGINS = [
  { slug: 'lausanne',  label: 'Lausanne'  },
  { slug: 'bern',      label: 'Bern'      },
  { slug: 'geneve',    label: 'Genève'    },
  { slug: 'zurich_hb', label: 'Zürich HB' },
]

const DEPARTURES = [
  { value: '0600', label: '06:00' },
  { value: '0800', label: '08:00' },
  { value: '1200', label: '12:00' },
  { value: '1800', label: '18:00' },
]

const origin    = ref('lausanne')
const departure = ref('0800')
const loading   = ref(false)
const error     = ref(false)
const stations  = ref<Station[]>([])
const boundary  = ref<object | null>(null)
const tooltip   = ref({ visible: false, x: 0, y: 0, name: '', minutes: null as number | null })

const svgRef = ref<SVGSVGElement | null>(null)

// Persist zoom across origin/departure switches
let currentTransform = d3.zoomIdentity
let zoomBehavior: d3.ZoomBehavior<SVGSVGElement, unknown> | null = null

// Fixed SVG coordinate space (taller canvas ≈ “zoomed in” map on the page)
const VB_W = 1000
const VB_H = 560

function stationColor(t: number | null): string {
  if (t === null) return '#ccc8c8'
  return d3.interpolateYlOrRd(1 - t / 360)
}

function formatTime(minutes: number | null): string {
  if (minutes === null) return 'Not reachable'
  if (minutes === 0)    return 'Origin station'
  const h = Math.floor(minutes / 60)
  const m = Math.round(minutes % 60)
  if (h === 0) return `${m} min`
  if (m === 0) return `${h}h`
  return `${h}h ${m}min`
}

function baseR(d: Station) { return d.travel_minutes === 0 ? 6 : 2.5 }
function hoverR(d: Station) { return d.travel_minutes === 0 ? 8 : 5 }

async function loadStations() {
  loading.value = true
  error.value   = false
  try {
    const res = await fetch(`/data/reachability_${origin.value}_${departure.value}.json`)
    if (!res.ok) throw new Error('not found')
    stations.value = await res.json()
  } catch {
    error.value    = true
    stations.value = []
  } finally {
    loading.value = false
  }
}

async function loadBoundary() {
  try {
    const res = await fetch('/data/swiss_boundary_wgs84.geojson')
    if (res.ok) boundary.value = await res.json()
  } catch { /* boundary is optional */ }
}

function draw() {
  if (!svgRef.value || stations.value.length === 0) return

  const svg = d3.select(svgRef.value)
  svg.selectAll('*').remove()

  // ── Projection ──────────────────────────────────────────────────────
  // Use the actual Swiss boundary for fitExtent so D3 sees real geometry.
  // Fall back to hardcoded values if boundary hasn't loaded yet.
  let projection: d3.GeoProjection
  if (boundary.value) {
    projection = d3.geoMercator().fitExtent(
      [[48, 42], [VB_W - 48, VB_H - 42]],
      boundary.value as any,
    )
  } else {
    projection = d3.geoMercator()
      .scale(9000)
      .center([8.23, 46.825])
      .translate([VB_W / 2, VB_H / 2])
  }

  const k = currentTransform.k

  // ── Zoom layer ───────────────────────────────────────────────────────
  const g = svg.append('g')
    .attr('class', 'zoom-layer')
    .attr('transform', currentTransform.toString())

  // Swiss boundary outline
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

  // Station circles — unreachable first so reachable render on top
  const sorted = [...stations.value].sort((a, b) => {
    if (a.travel_minutes === null && b.travel_minutes !== null) return -1
    if (a.travel_minutes !== null && b.travel_minutes === null) return 1
    return (b.travel_minutes ?? 0) - (a.travel_minutes ?? 0)
  })

  g.selectAll<SVGCircleElement, Station>('circle')
    .data(sorted, d => d.station_key)
    .join('circle')
    .attr('cx', d => projection([d.lon, d.lat])![0])
    .attr('cy', d => projection([d.lon, d.lat])![1])
    .attr('r',            d => baseR(d) / k)
    .attr('fill',         d => stationColor(d.travel_minutes))
    .attr('opacity',      d => d.travel_minutes === null ? 0.35 : 0.9)
    .attr('stroke',       d => d.travel_minutes === 0 ? 'white' : 'none')
    .attr('stroke-width', 1.5 / k)
    .style('cursor', 'pointer')
    .on('mouseenter', (event: MouseEvent, d: Station) => {
      d3.select(event.currentTarget as SVGCircleElement)
        .raise()
        .attr('r', hoverR(d) / currentTransform.k)
        .attr('opacity', 1)
      tooltip.value = { visible: true, x: event.clientX + 14, y: event.clientY - 10, name: d.station_name, minutes: d.travel_minutes }
    })
    .on('mousemove', (event: MouseEvent) => {
      tooltip.value.x = event.clientX + 14
      tooltip.value.y = event.clientY - 10
    })
    .on('mouseleave', (event: MouseEvent, d: Station) => {
      d3.select(event.currentTarget as SVGCircleElement)
        .attr('r', baseR(d) / currentTransform.k)
        .attr('opacity', d.travel_minutes === null ? 0.35 : 0.9)
      tooltip.value.visible = false
    })

  // ── Zoom behavior ────────────────────────────────────────────────────
  zoomBehavior = d3.zoom<SVGSVGElement, unknown>()
    .scaleExtent([1, 20])
    .translateExtent([[0, 0], [VB_W, VB_H]])
    .on('zoom', (event: d3.D3ZoomEvent<SVGSVGElement, unknown>) => {
      currentTransform = event.transform
      const zg = d3.select(svgRef.value!).select<SVGGElement>('g.zoom-layer')
      zg.attr('transform', event.transform.toString())
      const kz = event.transform.k
      zg.selectAll<SVGCircleElement, Station>('circle')
        .attr('r',            (d: Station) => baseR(d) / kz)
        .attr('stroke-width', (d: Station) => d.travel_minutes === 0 ? 1.5 / kz : 0)
      zg.select('path')
        .attr('stroke-width', 1 / kz)
    })

  d3.select(svgRef.value).call(zoomBehavior)
  d3.select(svgRef.value).call(zoomBehavior.transform, currentTransform)
}

function resetZoom() {
  if (!svgRef.value || !zoomBehavior) return
  currentTransform = d3.zoomIdentity
  d3.select(svgRef.value)
    .transition().duration(350)
    .call(zoomBehavior.transform, d3.zoomIdentity)
}

onMounted(async () => {
  await Promise.all([loadStations(), loadBoundary()])
  await nextTick()
  draw()
})

watch([origin, departure], async () => {
  await loadStations()
  await nextTick()
  draw()
})
</script>

<template>
  <div class="map-wrapper">

    <!-- Controls -->
    <div class="controls">
      <label class="control-group">
        <span class="control-label">Origin</span>
        <select v-model="origin" class="control-select">
          <option v-for="o in ORIGINS" :key="o.slug" :value="o.slug">{{ o.label }}</option>
        </select>
      </label>

      <label class="control-group">
        <span class="control-label">Departure</span>
        <select v-model="departure" class="control-select">
          <option v-for="d in DEPARTURES" :key="d.value" :value="d.value">{{ d.label }}</option>
        </select>
      </label>

      <span v-if="loading" class="loading-badge">Loading…</span>

      <div class="controls-right">
        <button class="reset-btn" @click="resetZoom" title="Reset zoom">⊙ Reset</button>
        <span class="zoom-hint">Scroll to zoom · drag to pan</span>
      </div>
    </div>

    <!-- Map -->
    <div class="map-container">
      <div v-if="error" class="map-empty">
        <p>The map data isn’t here yet.</p>
        <p>Try refreshing — if it keeps happening, the site may still be updating.</p>
      </div>
      <svg
        v-else
        ref="svgRef"
        class="map-svg"
        :viewBox="`0 0 ${VB_W} ${VB_H}`"
        overflow="hidden"
      />
    </div>

    <!-- Legend -->
    <div class="legend">
      <span class="legend-title">Travel time (6h window)</span>
      <div class="legend-gradient-wrap">
        <div class="legend-gradient" />
        <div class="legend-ticks">
          <span>0 min</span><span>3h</span><span>6h</span>
        </div>
      </div>
      <div class="legend-unreachable">
        <span class="legend-swatch" />
        Unreachable
      </div>
    </div>

  </div>

  <!-- Tooltip -->
  <Teleport to="body">
    <div
      v-if="tooltip.visible"
      :style="{
        position: 'fixed',
        left: tooltip.x + 'px',
        top:  tooltip.y + 'px',
        background: 'white',
        border: '1px solid rgba(184,68,75,0.18)',
        borderRadius: '10px',
        padding: '8px 13px',
        pointerEvents: 'none',
        boxShadow: '0 4px 18px rgba(64,24,26,0.13)',
        zIndex: 9999,
        fontSize: '0.84rem',
        color: '#271f20',
        minWidth: '130px',
      }"
    >
      <div style="font-weight: 700; margin-bottom: 2px">{{ tooltip.name }}</div>
      <div style="color: #7a4b4f">{{ formatTime(tooltip.minutes) }}</div>
    </div>
  </Teleport>
</template>

<style scoped>
.map-wrapper {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 22px clamp(18px, 2.5vw, 28px) 24px;
}

/* ── Controls ── */
.controls {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.92rem;
}

.control-label {
  font-weight: 600;
  color: #5b4b4d;
}

.control-select {
  border: 1px solid rgba(184, 68, 75, 0.22);
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 0.92rem;
  background: white;
  color: #271f20;
  cursor: pointer;
  appearance: auto;
}

.control-select:focus {
  outline: none;
  border-color: #c84f56;
  box-shadow: 0 0 0 3px rgba(200, 79, 86, 0.12);
}

.loading-badge {
  font-size: 0.85rem;
  color: #7a4b4f;
  font-style: italic;
}

.controls-right {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: auto;
}

.reset-btn {
  padding: 5px 12px;
  border: 1px solid rgba(184, 68, 75, 0.22);
  border-radius: 8px;
  font-size: 0.85rem;
  background: white;
  color: #7a3136;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}

.reset-btn:hover {
  background: rgba(200, 79, 86, 0.07);
  border-color: #c84f56;
}

.zoom-hint {
  font-size: 0.78rem;
  color: #a08888;
  white-space: nowrap;
}

/* ── Map ── */
.map-container {
  position: relative;
  width: 100%;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(184, 68, 75, 0.1);
  background: #d8dfe8;   /* ocean/background color outside Switzerland */
}

.map-svg {
  display: block;
  width: 100%;
  height: auto;
}

.map-empty {
  min-height: 300px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  text-align: center;
  color: #7a4b4f;
  font-size: 0.9rem;
  padding: 32px;
}

.map-empty code {
  font-family: ui-monospace, monospace;
  font-size: 0.82rem;
  background: rgba(200, 79, 86, 0.08);
  padding: 3px 7px;
  border-radius: 5px;
}

/* ── Legend ── */
.legend {
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
  font-size: 0.84rem;
  color: #5b4b4d;
}

.legend-title {
  font-weight: 600;
  white-space: nowrap;
}

.legend-gradient-wrap {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.legend-gradient {
  width: 180px;
  height: 10px;
  border-radius: 5px;
  background: linear-gradient(to right, #800026, #e31a1c, #fd8d3c, #feb24c, #ffffcc);
}

.legend-ticks {
  display: flex;
  justify-content: space-between;
  width: 180px;
  font-size: 0.78rem;
  color: #8a7070;
}

.legend-unreachable {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-swatch {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ccc8c8;
}
</style>
