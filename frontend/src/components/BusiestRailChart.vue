<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as d3 from 'd3'

type Row = { name: string; trips: number }
type Preset = { start: number; end: number; stations: Row[] }

const dataUrl = `${import.meta.env.BASE_URL}data/busiest_rail_windows.json`.replace(/\/{2,}/g, '/')

const presets = ref<Preset[]>([])
const loadError = ref(false)

const startMin = ref(360)
const endMin = ref(600)

const wrap = ref<HTMLDivElement | null>(null)
const svgRef = ref<SVGSVGElement | null>(null)
let ro: ResizeObserver | null = null

function fmt(m: number): string {
  const h = Math.floor(m / 60)
  const min = m % 60
  return `${String(h).padStart(2, '0')}:${String(min).padStart(2, '0')}`
}

function nearestPreset(s: number, e: number): Preset {
  const list = presets.value
  if (!list.length) return { start: s, end: e, stations: [] }
  let best = list[0]!
  let bestD = Infinity
  for (const p of list) {
    const d = Math.abs(p.start - s) + Math.abs(p.end - e)
    if (d < bestD) {
      bestD = d
      best = p
    }
  }
  return best
}

const activePreset = computed(() => nearestPreset(startMin.value, endMin.value))

const windowLabel = computed(() => `${fmt(startMin.value)} – ${fmt(endMin.value)}`)

const approxNote = computed(() => {
  const p = activePreset.value
  if (p.start === startMin.value && p.end === endMin.value) return ''
  return `Rankings shown for ${fmt(p.start)} – ${fmt(p.end)} — the closest match to the window you picked.`
})

function stationColor(trips: number, minT: number, maxT: number): string {
  const t = (trips - minT) / Math.max(maxT - minT, 1)
  const c = d3.interpolateYlOrRd(0.22 + 0.72 * t)
  return c
}

function draw() {
  const svgEl = svgRef.value
  const container = wrap.value
  if (!svgEl || !container || !activePreset.value.stations.length) return

  const rows = [...activePreset.value.stations].reverse()
  const w = container.clientWidth || 640
  const h = 360
  const margin = { top: 8, right: 28, bottom: 36, left: 132 }

  const innerW = w - margin.left - margin.right
  const innerH = h - margin.top - margin.bottom

  const maxT = d3.max(rows, d => d.trips) ?? 1
  const minT = d3.min(rows, d => d.trips) ?? 0

  const x = d3.scaleLinear().domain([0, maxT * 1.06]).range([0, innerW])
  const y = d3
    .scaleBand()
    .domain(rows.map(d => d.name))
    .range([innerH, 0])
    .padding(0.12)

  const svg = d3.select(svgEl)
  svg.selectAll('*').remove()
  svg.attr('viewBox', `0 0 ${w} ${h}`).attr('width', '100%').attr('height', h)

  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

  g.append('g')
    .attr('class', 'x-grid')
    .attr('transform', `translate(0,${innerH})`)
    .call(
      d3
        .axisBottom(x)
        .ticks(5)
        .tickSize(-innerH)
        /* Grid only: tick lines, no labels (labels come from .x-axis below). */
        .tickFormat(() => ''),
    )
    .call(g2 => {
      g2.select('.domain').remove()
      g2.selectAll('text').remove()
    })
    .selectAll('line')
    .attr('stroke', 'rgba(120,90,92,0.12)')
    .attr('stroke-dasharray', '3 4')

  g.append('g')
    .attr('class', 'x-axis')
    .attr('transform', `translate(0,${innerH})`)
    .call(d3.axisBottom(x).ticks(5).tickSizeOuter(0))
    .call(g2 => {
      g2.selectAll('text').attr('fill', '#7a6568').attr('font-size', '11px')
      g2.selectAll('path, line').attr('stroke', 'rgba(120,90,92,0.35)')
    })

  g.append('text')
    .attr('x', innerW)
    .attr('y', innerH + 30)
    .attr('text-anchor', 'end')
    .attr('fill', '#8a7070')
    .attr('font-size', '11px')
    .text('Unique rail trips')

  g.selectAll('rect.bar')
    .data(rows)
    .join('rect')
    .attr('class', 'bar')
    .attr('x', 0)
    .attr('y', d => y(d.name)!)
    .attr('height', y.bandwidth())
    .attr('rx', 4)
    .attr('fill', d => stationColor(d.trips, minT, maxT))
    .attr('stroke', 'rgba(255,255,255,0.85)')
    .attr('stroke-width', 0.5)
    .attr('width', 0)
    .transition()
    .duration(420)
    .ease(d3.easeCubicOut)
    .attr('width', d => x(d.trips))

  g.selectAll('text.label')
    .data(rows)
    .join('text')
    .attr('class', 'label')
    .attr('x', -10)
    .attr('y', d => (y(d.name)! + y.bandwidth() / 2) as number)
    .attr('dy', '0.35em')
    .attr('text-anchor', 'end')
    .attr('fill', '#3d3335')
    .attr('font-size', '11px')
    .attr('font-weight', '600')
    .text(d => d.name)

  g.selectAll('text.val')
    .data(rows)
    .join('text')
    .attr('class', 'val')
    .attr('x', d => x(d.trips) + 6)
    .attr('y', d => (y(d.name)! + y.bandwidth() / 2) as number)
    .attr('dy', '0.35em')
    .attr('fill', '#5b4b4d')
    .attr('font-size', '10px')
    .attr('opacity', 0)
    .text(d => d.trips)
    .transition()
    .delay(200)
    .duration(280)
    .attr('opacity', 1)
}

onMounted(async () => {
  try {
    const res = await fetch(dataUrl)
    if (!res.ok) throw new Error('missing')
    const j = await res.json()
    presets.value = j.presets ?? []
  } catch {
    loadError.value = true
  }
  await nextTick()
  draw()
  ro = new ResizeObserver(() => draw())
  if (wrap.value) ro.observe(wrap.value)
})

onBeforeUnmount(() => {
  ro?.disconnect()
})

watch([startMin, endMin, presets], async () => {
  await nextTick()
  draw()
})

function clampStart(v: number) {
  const x = Math.round(v / 15) * 15
  return Math.min(Math.max(x, 300), 21 * 60)
}

function clampEnd(v: number) {
  const x = Math.round(v / 15) * 15
  return Math.min(Math.max(x, startMin.value + 30), 22 * 60)
}

function onStartInput(e: Event) {
  const v = clampStart(Number((e.target as HTMLInputElement).value))
  startMin.value = v
  if (endMin.value <= v + 30) endMin.value = Math.min(v + 120, 22 * 60)
}

function onEndInput(e: Event) {
  const v = clampEnd(Number((e.target as HTMLInputElement).value))
  endMin.value = Math.max(v, startMin.value + 30)
}
</script>

<template>
  <div class="chart-shell">
    <div class="chart-heading">
      <span class="chart-kicker">Load</span>
      <h3 class="chart-title">Where the morning concentrates</h3>
      <p class="chart-lead">
        Drag the morning open or shut. Each bar is a doorway: how many <em>different</em> trains touch that platform
        while your window is running. The reds are the crowd favourites; the pale yellows are still busy, just not
        centre stage.
      </p>
    </div>

    <div v-if="loadError" class="chart-fallback">
      <p>This little ranking couldn’t load. Refresh the page, or try again later — the rest of the story still
        works.</p>
    </div>

    <div v-else class="chart-body">
      <div class="sliders">
        <label class="slider-block">
          <span class="slider-label">Start</span>
          <input
            type="range"
            class="slider"
            :min="300"
            :max="21 * 60"
            step="15"
            :value="startMin"
            @input="onStartInput"
          >
          <span class="slider-value">{{ fmt(startMin) }}</span>
        </label>
        <label class="slider-block">
          <span class="slider-label">End</span>
          <input
            type="range"
            class="slider"
            :min="330"
            :max="22 * 60"
            step="15"
            :value="endMin"
            @input="onEndInput"
          >
          <span class="slider-value">{{ fmt(endMin) }}</span>
        </label>
      </div>
      <p class="window-line">
        <span class="window-pill">{{ windowLabel }}</span>
        <span v-if="approxNote" class="window-approx">{{ approxNote }}</span>
      </p>

      <div ref="wrap" class="chart-wrap">
        <svg ref="svgRef" class="chart-svg" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.chart-shell {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 22px 24px 26px;
  border-radius: 20px;
  border: 1px solid rgba(184, 68, 75, 0.12);
  background:
    linear-gradient(165deg, rgba(255, 252, 251, 0.98) 0%, rgba(248, 244, 242, 0.95) 48%, rgba(255, 255, 255, 0.92) 100%);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.75), 0 18px 48px rgba(64, 24, 26, 0.06);
}

.chart-heading {
  max-width: 42ch;
}

.chart-kicker {
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: #c84f56;
}

.chart-title {
  margin: 6px 0 0;
  font-family: var(--swissreach-font-sans);
  font-size: 1.35rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  color: #1f1819;
}

.chart-lead {
  margin: 10px 0 0;
  font-size: 0.88rem;
  line-height: 1.55;
  color: #6b5c5e;
}

.chart-fallback {
  font-size: 0.86rem;
  color: #7a4b4f;
  line-height: 1.55;
}

.chart-fallback code {
  font-family: ui-monospace, monospace;
  font-size: 0.8rem;
  background: rgba(200, 79, 86, 0.08);
  padding: 2px 6px;
  border-radius: 4px;
}

.sliders {
  display: flex;
  flex-wrap: wrap;
  gap: 20px 28px;
  align-items: flex-end;
}

.slider-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 200px;
  flex: 1;
}

.slider-label {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #9a787c;
}

.slider {
  width: 100%;
  accent-color: #b8444b;
  height: 6px;
}

.slider-value {
  font-size: 0.82rem;
  font-weight: 600;
  color: #4a3d3f;
  font-variant-numeric: tabular-nums;
}

.window-line {
  margin: 4px 0 0;
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 10px 14px;
}

.window-pill {
  display: inline-block;
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: #6a3034;
  background: rgba(200, 79, 86, 0.1);
  border: 1px solid rgba(184, 68, 75, 0.18);
}

.window-approx {
  font-size: 0.76rem;
  color: #8a7578;
  font-style: italic;
  max-width: 52ch;
  line-height: 1.4;
}

.chart-wrap {
  width: 100%;
  margin-top: 6px;
}

.chart-svg {
  display: block;
  width: 100%;
}
</style>
