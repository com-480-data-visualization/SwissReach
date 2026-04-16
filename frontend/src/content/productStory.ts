import { withBase } from '@/utils/assets'

export type MetricTone = 'brand' | 'warm' | 'neutral'

export interface MetricItem {
  label: string
  value: string
  tone?: MetricTone
}

export type StoryMediaVariant = 'reachability-map' | 'reachability-lab' | 'busiest-rail'

export interface StoryPanelContent {
  id: string
  navLabel: string
  eyebrow: string
  title: string
  description: string
  highlights: string[]
  metrics: MetricItem[]
  mediaVariant: StoryMediaVariant
  mediaCaption: string
}

export const heroPreviewUrl = withBase('/preview/lausanne_reachability_0800_6h.png')
export const brandLogoUrl = withBase('/logo/SwissReach_vectorized.png')

export const introMetrics: MetricItem[] = [
  {
    value: '4 anchor cities',
    label: 'A consistent view across Lausanne, Bern, Geneva and Zurich.',
    tone: 'brand',
  },
  {
    value: '08:00 focus',
    label: 'A clear morning departure frame keeps comparison grounded in everyday routines.',
    tone: 'neutral',
  },
  {
    value: 'Daily essentials',
    label: 'Coverage is framed around the places people actually need on an ordinary weekday.',
    tone: 'warm',
  },
]

export const storyPanels: StoryPanelContent[] = [
  {
    id: 'positioning',
    navLabel: 'Coverage Map',
    eyebrow: 'National Reachability',
    title: 'SwissReach turns national transit complexity into an interactive daily picture.',
    description:
      'Instead of starting from timetables, interact directly with the map. Select your origin city and departure window to instantly visualize how much of Switzerland is reachable.',
    highlights: [
      'A product surface that keeps national context legible without overwhelming the reader.',
      'Maps, labels and supporting cues share one restrained visual rhythm.',
      'Instantly see real travel times mapped via color gradients.',
    ],
    metrics: [
      {
        value: 'National coverage',
        label: 'One consistent frame for intercity reach.',
        tone: 'brand',
      },
      { value: 'Low-noise layout', label: 'Only the next decision stays in focus.' },
    ],
    mediaVariant: 'reachability-map',
    mediaCaption: 'Interactive National Reachability Map. Scroll inside to zoom, drag to pan.',
  },
  {
    id: 'feature-coverage',
    navLabel: 'Lausanne Lab',
    eyebrow: 'Local Nuance',
    title: 'The Lausanne Reachability Lab breaks down regional connectivity and time gaps.',
    description:
      'Explore deep dives into specific regions like Lausanne. Understanding departure-time coverage reveals how the same network changes character over the day.',
    highlights: [
      'Time-based framing makes mobility differences understandable without dense controls.',
      'Comparisons stay readable because only one departure lens is foregrounded at a time.',
    ],
    metrics: [
      {
        value: '06:00 / 08:00 / 18:00',
        label: 'Departure windows stay easy to scan.',
        tone: 'warm',
      },
      { value: 'City Focus', label: 'Detailed regional distribution.' },
    ],
    mediaVariant: 'reachability-lab',
    mediaCaption: 'Hover over individual plots to examine specific station reaches.',
  },
  {
    id: 'busiest-rail',
    navLabel: 'Busiest Rail',
    eyebrow: 'Network Density',
    title: 'Swiss rail traffic volume reveals the busiest arteries of transport.',
    description:
      'The layout separates regional access, transfer continuity and destination comfort into a compact visual system.',
    highlights: [
      'Traffic flows are sized mathematically to reflect real train numbers.',
      'Quickly identify the operational backbone of the Swiss railway network.',
    ],
    metrics: [
      { value: 'Traffic Scale', label: 'Visualizing absolute train volume.', tone: 'brand' },
      {
        value: 'Nodes & Edges',
        label: 'Direct display of network load.',
        tone: 'neutral',
      },
    ],
    mediaVariant: 'busiest-rail',
    mediaCaption: 'Busiest Rail Network diagram. Thicker lines indicate higher railway traffic.',
  },
]
