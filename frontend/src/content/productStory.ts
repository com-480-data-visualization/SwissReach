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
    value: '1,938 stations',
    label: 'Swiss GTFS is collapsed from raw stops into logical rail stations.',
    tone: 'neutral',
  },
  {
    value: 'Daily essentials',
    label: 'Coverage is framed around supermarkets, schools, hospitals, and more.',
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
    eyebrow: 'Lausanne',
    title: 'Departure & Window',
    description: 'Stay in Lausanne and adjust your departure time — 06:00, 08:00, or 18:00 — to observe the shift in national reachability. Budget your travel time to see which stations remain accessible and where the coverage begins to thin out.',
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
    description: 'Visualizing the busiest arteries and transfer hubs in the network based on daily train traffic. Drag the morning window open or shut to see how many different trains touch each platform, and where the crowd favourites start to dominate.',
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
