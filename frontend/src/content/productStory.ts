import { withBase } from '@/utils/assets'

export type MetricTone = 'brand' | 'warm' | 'neutral'

export interface MetricItem {
  label: string
  value: string
  tone?: MetricTone
}

export type StoryMediaVariant =
  | 'reachability-map'
  | 'reachability-lab'
  | 'busiest-rail'
  | 'retail-density'
  | 'retail-access'
export type StoryMediaPreset =
  | 'transport-story'
  | 'transport-playground'
  | 'transport-load'
  | 'retail-story'
  | 'retail-playground'
  | 'retail-access-story'
  | 'retail-access-playground'
  | 'brand-story'
  | 'brand-playground'

export interface StoryPanelContent {
  id: string
  topic: string
  panelKind: 'Story' | 'Playground'
  navLabel: string
  eyebrow: string
  title: string
  description: string
  highlights: string[]
  metrics: MetricItem[]
  mediaVariant: StoryMediaVariant
  mediaPreset: StoryMediaPreset
  mediaCaption: string
}

export const heroPreviewUrl = withBase('/preview/lausanne_reachability_0800_6h.png')
export const brandLogoUrl = withBase('/logo/SwissReach_vectorized.png')

export const introMetrics: MetricItem[] = [
  {
    value: '08:00 baseline',
    label: 'The retail-access layer stays explicit about the fixed morning departure it uses.',
    tone: 'brand',
  },
  {
    value: '1,663 stations',
    label: 'National comparisons are anchored on logical Swiss rail stations with exported POI counts.',
    tone: 'neutral',
  },
  {
    value: '3,430 supermarkets',
    label: 'Daily opportunity is framed through the supermarket layer, not just through rail geometry.',
    tone: 'warm',
  },
]

export const storyPanels: StoryPanelContent[] = [
  {
    id: 'transport-story',
    topic: 'Transport Reachability',
    panelKind: 'Story',
    navLabel: 'Transport Story',
    eyebrow: 'Transport Reachability',
    title: 'Morning Reachability',
    description:
      'A fixed Lausanne departure at 08:00 reveals where the Swiss rail backbone is dense, where coverage thins out, and how national reach already differs before daily destinations enter the picture.',
    highlights: [
      'A fixed morning case makes the national pattern legible before controls appear.',
      'The same rail geometry will later be reused to explain retail opportunity.',
    ],
    metrics: [
      {
        value: '06:00 / 08:00 / 18:00',
        label: 'The Lausanne lab already exposes the key departure windows.',
        tone: 'brand',
      },
      {
        value: 'Swiss scale',
        label: 'Coverage is still evaluated as a national story, not as one city map.',
        tone: 'neutral',
      },
      {
        value: 'Story first',
        label: 'The selected lens is here to frame the rest of the page before playgrounds take over.',
        tone: 'warm',
      },
    ],
    mediaVariant: 'reachability-lab',
    mediaPreset: 'transport-story',
    mediaCaption: 'Fixed on Lausanne so the first panel reads like an argument, not like a control surface.',
  },
  {
    id: 'transport-playground',
    topic: 'Transport Reachability',
    panelKind: 'Playground',
    navLabel: 'Transport Playground',
    eyebrow: 'Transport Reachability',
    title: 'Explore the Network',
    description:
      'Switch origins, change departure times, and compare how much of Switzerland each major station can realistically pull into reach.',
    highlights: [
      'Origin and departure are the only two controls because the question is still singular.',
      'The map keeps the same national frame so later retail panels feel like the same product.',
    ],
    metrics: [
      {
        value: '4 origins',
        label: 'Lausanne, Bern, Geneve, and Zurich HB remain comparable anchor cases.',
        tone: 'warm',
      },
      {
        value: 'Travel-time gradient',
        label: 'Color continues to encode how quickly the network opens up.',
        tone: 'neutral',
      },
      {
        value: 'Interactive map',
        label: 'Scroll inside to zoom and drag to pan without breaking the page rhythm.',
        tone: 'brand',
      },
    ],
    mediaVariant: 'reachability-map',
    mediaPreset: 'transport-playground',
    mediaCaption: 'Choose an origin, choose a departure, then read the national footprint.',
  },
  {
    id: 'transport-load',
    topic: 'Rail Backbone',
    panelKind: 'Story',
    navLabel: 'Rail Load',
    eyebrow: 'Rail Backbone',
    title: 'Network Load',
    description:
      'The busiest-station ranking makes the backbone visible from a different angle: not just where you can reach, but where rail traffic concentrates most strongly across the day.',
    highlights: [
      'The rail backbone is easier to read once movement intensity is separated from reachability.',
      'A focused ranking view works better here than squeezing the chart into the map panel.',
    ],
    metrics: [
      {
        value: 'Window-based ranking',
        label: 'Drag the morning window and compare how the concentration changes.',
        tone: 'brand',
      },
      {
        value: 'Core corridors',
        label: 'The chart isolates the most heavily used parts of the network.',
        tone: 'neutral',
      },
      {
        value: 'Transport context',
        label: 'This closes the transport section before retail begins.',
        tone: 'warm',
      },
    ],
    mediaVariant: 'busiest-rail',
    mediaPreset: 'transport-load',
    mediaCaption: 'A dedicated rail-load view gives the ranking enough space to read as part of the transport story.',
  },
  {
    id: 'retail-story',
    topic: 'Retail Footprint',
    panelKind: 'Story',
    navLabel: 'Retail Story',
    eyebrow: 'Retail Footprint',
    title: 'Retail Footprint',
    description:
      'Supermarkets do not simply mirror rail intensity. The footprint clusters along the Swiss plateau, thickens around metropolitan corridors, and still reveals brand-specific gaps that a pure transport view would miss.',
    highlights: [
      'This panel stays on the stores themselves to establish retail as its own layer.',
      'Migros and Coop overlap heavily, but not uniformly, across the national footprint.',
    ],
    metrics: [
      {
        value: '743 Migros',
        label: 'Current OSM-based export used in the product layer.',
        tone: 'neutral',
      },
      {
        value: '943 Coop',
        label: 'The Coop network is broader in the current national snapshot.',
        tone: 'warm',
      },
      { value: 'Retail first', label: 'This topic asks where stores gather before asking who can reach them.', tone: 'brand' },
    ],
    mediaVariant: 'retail-density',
    mediaPreset: 'retail-story',
    mediaCaption: 'A national store footprint is enough to show that retail logic is related to transport, but not reducible to it.',
  },
  {
    id: 'retail-playground',
    topic: 'Retail Footprint',
    panelKind: 'Playground',
    navLabel: 'Retail Playground',
    eyebrow: 'Retail Footprint',
    title: 'Compare Store Networks',
    description:
      'Toggle Both, Migros, or Coop and compare how the national retail pattern shifts when one network drops out of view.',
    highlights: [
      'Brand filtering is the main interaction because the spatial comparison should stay immediate.',
      'The control language deliberately matches the rest of SwissReach rather than turning into a dashboard.',
    ],
    metrics: [
      {
        value: 'Both / Migros / Coop',
        label: 'Three states are enough for an MVP retail explorer.',
        tone: 'brand',
      },
      {
        value: 'Hover details',
        label: 'Store names and source links remain available without cluttering the map.',
        tone: 'neutral',
      },
      {
        value: 'National frame',
        label: 'The same Swiss boundary keeps this panel visually tied to the transport topic.',
        tone: 'warm',
      },
    ],
    mediaVariant: 'retail-density',
    mediaPreset: 'retail-playground',
    mediaCaption: 'Filtering the footprint is enough to make retail structure legible in three to five seconds.',
  },
  {
    id: 'retail-access-story',
    topic: 'Retail Access',
    panelKind: 'Story',
    navLabel: 'Retail Access Story',
    eyebrow: 'Retail Access',
    title: 'Retail Access',
    description:
      'Each rail station inherits a 30-minute supermarket count from the fixed 08:00 baseline, showing where strong network access really turns into daily retail choice and where it does not.',
    highlights: [
      'The baseline is explicit: these counts come from a fixed 08:00 departure export.',
      'Opportunity is encoded as reachable supermarkets, not just as nearby track density.',
    ],
    metrics: [
      {
        value: '30-minute supermarkets',
        label: 'The main retail-access metric used in the national story.',
        tone: 'brand',
      },
      {
        value: '08:00 only',
        label: 'The UI states the time limit honestly instead of implying a live routing engine.',
        tone: 'warm',
      },
      {
        value: '1,663 stations',
        label: 'Every point on the map is a logical rail station with exported POI counts.',
        tone: 'neutral',
      },
    ],
    mediaVariant: 'retail-access',
    mediaPreset: 'retail-access-story',
    mediaCaption: 'This view is fixed to the morning baseline, so the takeaway is about opportunity shape rather than arbitrary control changes.',
  },
  {
    id: 'retail-access-playground',
    topic: 'Retail Access',
    panelKind: 'Playground',
    navLabel: 'Retail Access Playground',
    eyebrow: 'Retail Access',
    title: 'Compare Reachable Opportunity',
    description:
      'Compare featured stations, supermarket counts within 30 minutes, and IKEA access within 60 minutes to contrast daily retail with sparse destination retail.',
    highlights: [
      'Featured station shortcuts keep exploration concrete and readable on a single screen.',
      'Switching between supermarkets and IKEA makes “daily opportunity” versus “destination retail” intuitive.',
    ],
    metrics: [
      {
        value: 'Supermarkets / IKEA',
        label: 'Two metrics, same map, different meanings of access.',
        tone: 'brand',
      },
      {
        value: 'Featured stations',
        label: 'A small curated set is faster than a full search box in the first release.',
        tone: 'neutral',
      },
      {
        value: 'Same transport base',
        label: 'Retail access stays downstream of the rail network rather than becoming a separate tool.',
        tone: 'warm',
      },
    ],
    mediaVariant: 'retail-access',
    mediaPreset: 'retail-access-playground',
    mediaCaption: 'The interaction remains honest and light: compare station cases, switch the retail lens, and keep the fixed morning baseline in view.',
  },
  {
    id: 'brand-story',
    topic: 'Brand Contrast',
    panelKind: 'Story',
    navLabel: 'Brand Story',
    eyebrow: 'Brand Contrast',
    title: 'Brand Contrast',
    description:
      'Migros and Coop overlap strongly in major corridors, but the balance is not flat. Comparison mode highlights where one network broadens everyday choice and where the national retail story is effectively being carried by the other.',
    highlights: [
      'This is still a geography question, not a market-share dashboard.',
      'Difference mode is most useful once the user has already seen the full footprint and the access layer.',
    ],
    metrics: [
      {
        value: 'Brand-aware reading',
        label: '“How many stores?” and “which network?” are not interchangeable questions.',
        tone: 'brand',
      },
      {
        value: 'Shared corridors',
        label: 'Overlap is highest where national population and rail intensity already concentrate.',
        tone: 'neutral',
      },
      {
        value: 'Uneven margins',
        label: 'Regional imbalances still matter once one brand is filtered out.',
        tone: 'warm',
      },
    ],
    mediaVariant: 'retail-density',
    mediaPreset: 'brand-story',
    mediaCaption: 'Difference mode is a retail reading of the same Swiss surface, not a detached appendix.',
  },
  {
    id: 'brand-playground',
    topic: 'Brand Contrast',
    panelKind: 'Playground',
    navLabel: 'Brand Playground',
    eyebrow: 'Brand Contrast',
    title: 'Explore Brand Differences',
    description:
      'Flip between Both, Migros, Coop, and Difference to see how brand structure changes the geography of everyday retail.',
    highlights: [
      'The same component handles the comparison to avoid inventing a second visual language.',
      'Ending on an exploratory brand panel makes the retail line feel like a main story rather than a footnote.',
    ],
    metrics: [
      {
        value: 'Difference mode',
        label: 'The strongest contrast view lives in the final retail panel.',
        tone: 'brand',
      },
      {
        value: 'Single-map compare',
        label: 'No separate page, no detached chart, just one continuous product narrative.',
        tone: 'neutral',
      },
      {
        value: 'Retail closes the loop',
        label: 'Transport explains connection; brand structure explains which choices that connection unlocks.',
        tone: 'warm',
      },
    ],
    mediaVariant: 'retail-density',
    mediaPreset: 'brand-playground',
    mediaCaption: 'Brand switching is the last step in the sequence because it depends on the transport and retail layers that came before it.',
  },
]
