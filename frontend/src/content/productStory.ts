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
    eyebrow: '',
    title: 'National Reachability',
    description: 'Select an origin city and departure window to instantly visualize travel times across Switzerland.',
    highlights: [
      'Interactive real-time maps.',
      'Travel times mapped via clear color gradients.',
    ],
    metrics: [
      {
        value: 'National coverage',
        label: 'Explore intercity connections.',
        tone: 'brand',
      },
      { value: 'Instant feedback', label: 'Click to discover.' },
    ],
    mediaVariant: 'reachability-map',
    mediaCaption: 'Interactive Reachability Map. Scroll inside to zoom, drag to pan.',
  },
  {
    id: 'feature-coverage',
    navLabel: 'Lausanne Lab',
    eyebrow: 'Local Nuance',
    title: 'Lausanne Reachability Lab',
    description: 'See how the transit network evolves throughout the day by comparing different departure windows.',
    highlights: [
      'Time-based comparative analysis.',
      'Detailed regional distribution and isolated gaps.',
    ],
    metrics: [
      {
        value: '06:00 / 08:00 / 18:00',
        label: 'Key departure times.',
        tone: 'warm',
      },
      { value: 'Station Focus', label: 'Local distribution data.' },
    ],
    mediaVariant: 'reachability-lab',
    mediaCaption: 'Hover over plots to examine specific station reaches.',
  },
  {
    id: 'busiest-rail',
    navLabel: 'Busiest Rail',
    eyebrow: 'Network Density',
    title: 'Swiss Rail Backbone',
    description: 'Visualizing the busiest arteries and transfer hubs in the network based on daily train traffic.',
    highlights: [
      'Flows scaled to actual train volumes.',
      'Highlighting the core network structure.',
    ],
    metrics: [
      { value: 'Network Load', label: 'Daily train density.', tone: 'brand' },
      {
        value: 'Nodes & Edges',
        label: 'Key transport hubs.',
        tone: 'neutral',
      },
    ],
    mediaVariant: 'busiest-rail',
    mediaCaption: 'Busiest Rail Network. Thicker lines indicate higher traffic.',
  },
]
