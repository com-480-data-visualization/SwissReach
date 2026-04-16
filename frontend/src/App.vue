<script setup lang="ts">
import ReachabilityMap from '@/components/ReachabilityMap.vue'
import LausanneReachabilityLab from '@/components/LausanneReachabilityLab.vue'
import BusiestRailChart from '@/components/BusiestRailChart.vue'

const docsUrl = 'https://swissreach.online/docs/'
const finalPlanUrl = `${docsUrl}final-web-plan`
const githubUrl = 'https://github.com/com-480-data-visualization/SwissReach'

/** Avoid root-absolute asset paths in script — Vite may treat them as module imports. */
const asset = (path: string) => `${import.meta.env.BASE_URL}${path}`.replace(/\/{2,}/g, '/')
const heroPreviewUrl = asset('preview/lausanne_reachability_0800_6h.png')
</script>

<template>
  <div class="page-shell">
    <header class="hero">
      <nav class="topbar">
        <div class="brand">
          <img
            alt="SwissReach logo"
            class="brand-logo"
            src="/logo/SwissReach_vectorized.png"
          >
          <span class="brand-name">SwissReach</span>
        </div>

        <div class="topbar-links">
          <a href="#story-transport">Explore</a>
          <a href="#folio-everyday">Everyday</a>
          <a :href="finalPlanUrl" target="_blank" rel="noreferrer">Plan</a>
          <a :href="docsUrl" target="_blank" rel="noreferrer">Docs</a>
          <a :href="githubUrl" target="_blank" rel="noreferrer">GitHub</a>
        </div>
      </nav>

      <section class="hero-content">
        <div class="hero-copy">
          <p class="eyebrow">EPFL COM-480 · SwissReach</p>
          <h1 class="hero-title">Everyday reachability, mapped.</h1>
          <p class="hero-text">
            SwissReach is about one question, told two ways: <strong>where the network lets you go</strong>, and
            <strong>what that means on an ordinary Tuesday</strong> — shops, schools, the errands that make a city
            feel small or huge. Scroll down: the maps and bars are already talking; more chapters will join them.
          </p>

          <div class="hero-actions">
            <a class="button button-primary" :href="docsUrl" target="_blank" rel="noreferrer">
              Open Documentation
            </a>
            <a class="button button-secondary" :href="githubUrl" target="_blank" rel="noreferrer">
              View on GitHub
            </a>
          </div>
        </div>

        <div class="hero-visual">
          <figure class="hero-map-card">
            <div class="hero-map-frame">
              <img
                alt="Swiss railway reachability from Lausanne, departure 08:00, six-hour window"
                class="hero-map-img"
                :src="heroPreviewUrl"
                loading="eager"
                fetchpriority="high"
              >
            </div>
          </figure>
        </div>
      </section>
    </header>

    <main class="content">
      <section id="story-transport" class="chapter chapter-transport">
        <header class="chapter-header">
          <span class="chapter-mark">I</span>
          <div class="chapter-titles">
            <p class="chapter-label">Transport</p>
            <h2 class="chapter-title">The network, then the distance</h2>
          </div>
        </header>

        <div class="chapter-prose">
          <p>
            Picture Switzerland as a single evening conversation: someone in Lausanne, Bern, Geneva, or Zürich
            glances at the clock and wonders, <em>if I leave now, where could I still be before the day ends?</em>
            The map answers in colour — every dot is a station, and the glow is how long the ride would take.
            Below that story, nudge the clock on the bar chart: the same country reshuffles its busiest doorways as
            the morning widens or narrows.
          </p>
        </div>

        <div class="atelier">
          <div class="atelier-cell atelier-map">
            <ReachabilityMap />
            <LausanneReachabilityLab />
          </div>
          <div class="atelier-cell atelier-chart">
            <BusiestRailChart />
          </div>
        </div>
      </section>

      <section id="folio-everyday" class="folio">
        <div class="folio-inner">
          <span class="folio-mark">II</span>
          <div class="folio-copy">
            <h3 class="folio-title">Everyday destinations</h3>
            <p class="folio-text">
              Trains are only half the plot. Here we will park the groceries, the school run, the pharmacy — the
              places that decide whether a timetable feels generous or cruel. Think of it as the epilogue to the
              map above.
            </p>
            <p class="folio-tag">Coming next</p>
          </div>
        </div>
      </section>

      <section id="folio-compare" class="folio folio-muted">
        <div class="folio-inner">
          <span class="folio-mark">III</span>
          <div class="folio-copy">
            <h3 class="folio-title">Comparison &amp; rhythm</h3>
            <p class="folio-text">
              Same country, different doors: how does leaving at dawn compare to leaving at dusk? This corner will
              hold side-by-side stories — still the same colours and hush, just a wider cast of cities and hours.
            </p>
            <p class="folio-tag">Coming next</p>
          </div>
        </div>
      </section>

      <section id="folio-methods" class="folio">
        <div class="folio-inner">
          <span class="folio-mark">IV</span>
          <div class="folio-copy">
            <h3 class="folio-title">Method &amp; provenance</h3>
            <p class="folio-text">
              For readers who like receipts: how we count trips, what counts as a “station,” how tight transfers
              are allowed to be, and where the walking shortcuts sneak in. Plain language, light touch — the drama
              stays upstairs.
            </p>
            <p class="folio-tag">
              <a :href="docsUrl" target="_blank" rel="noreferrer">Docs</a>
              ·
              <a :href="finalPlanUrl" target="_blank" rel="noreferrer">Site plan</a>
            </p>
          </div>
        </div>
      </section>

      <footer class="site-footer">
        <p class="footer-line">
          SwissReach · EPFL COM-480 · public transport timetables, turned into colour and distance
        </p>
        <p class="footer-links">
          <a :href="githubUrl" target="_blank" rel="noreferrer">GitHub</a>
        </p>
      </footer>
    </main>
  </div>
</template>

<style scoped>
:global(html) {
  /* Slightly larger “page zoom” for a calmer, editorial read (closer to the earlier SwissReach landing). */
  font-size: 17px;
}

@media (max-width: 640px) {
  :global(html) {
    font-size: 16px;
  }
}

:global(body) {
  margin: 0;
  font-family:
    Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background:
    radial-gradient(ellipse 120% 80% at 12% -10%, rgba(200, 79, 86, 0.11), transparent 42%),
    linear-gradient(180deg, #fff8f6 0%, #fffefc 38%, #fff 100%);
  color: #271f20;
  scroll-behavior: smooth;
}

:global(a) {
  color: inherit;
  text-decoration: none;
}

:global(a:hover) {
  text-decoration: underline;
  text-underline-offset: 3px;
}

:global(*) {
  box-sizing: border-box;
}

.page-shell {
  min-height: 100vh;
}

.hero {
  max-width: min(1280px, 94vw);
  margin: 0 auto;
  padding: 28px clamp(18px, 3vw, 40px) 48px;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: clamp(28px, 4vw, 48px);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-logo {
  width: 48px;
  height: 48px;
  object-fit: contain;
}

.brand-name {
  font-size: 1.18rem;
  font-weight: 700;
  letter-spacing: 0.01em;
}

.topbar-links {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 14px 18px;
  font-size: 0.92rem;
  font-weight: 600;
  color: #7a4b4f;
}

.topbar-links a:hover {
  color: #b8444b;
  text-decoration: none;
}

.hero-content {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.02fr);
  gap: clamp(24px, 4vw, 44px);
  align-items: center;
}

.eyebrow {
  margin: 0 0 12px;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #b8444b;
}

.hero-title {
  margin: 0;
  font-size: clamp(2.65rem, 1.1rem + 4.8vw, 5.1rem);
  line-height: 1.03;
  letter-spacing: -0.038em;
  font-weight: 800;
}

.hero-text {
  max-width: 46ch;
  margin: 18px 0 0;
  font-size: 1.08rem;
  line-height: 1.68;
  color: #4f4244;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 28px;
}

.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 0 22px;
  border-radius: 999px;
  font-weight: 600;
  font-size: 1.02rem;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    background-color 0.2s ease;
}

.button:hover {
  transform: translateY(-1px);
  text-decoration: none;
}

.button-primary {
  background: #c84f56;
  color: white;
  box-shadow: 0 14px 32px rgba(200, 79, 86, 0.24);
}

.button-primary:hover {
  background: #b8444b;
}

.button-secondary {
  border: 1px solid rgba(184, 68, 75, 0.18);
  background: rgba(255, 255, 255, 0.86);
  color: #7a3136;
}

.hero-visual {
  display: flex;
  justify-content: stretch;
  align-items: flex-start;
}

.hero-map-card {
  margin: 0;
  width: 100%;
  padding: 14px 14px 16px;
  border-radius: 22px;
  border: 1px solid rgba(184, 68, 75, 0.1);
  background: linear-gradient(165deg, #fff 0%, #fffaf9 100%);
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.9) inset,
    0 22px 56px rgba(48, 18, 22, 0.1),
    0 8px 24px rgba(48, 18, 22, 0.05);
}

.hero-map-frame {
  border-radius: 14px;
  overflow: hidden;
  background: #eceef2;
  line-height: 0;
}

/* Hero preview: full image visible (no crop). */
.hero-map-img {
  width: 100%;
  height: auto;
  display: block;
}

.content {
  max-width: min(1240px, 94vw);
  margin: 0 auto;
  padding: 0 clamp(18px, 3vw, 36px) 72px;
  display: grid;
  gap: 26px;
}

.chapter {
  padding: clamp(28px, 3vw, 40px) clamp(24px, 3vw, 40px) 42px;
  border-radius: 28px;
  border: 1px solid rgba(184, 68, 75, 0.11);
  background:
    linear-gradient(165deg, rgba(255, 255, 255, 0.97) 0%, rgba(255, 249, 247, 0.94) 40%, rgba(252, 248, 246, 0.96) 100%);
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.9) inset,
    0 28px 70px rgba(58, 22, 26, 0.06);
}

.chapter-header {
  display: flex;
  align-items: flex-start;
  gap: 22px;
  margin-bottom: 8px;
}

.chapter-mark {
  flex-shrink: 0;
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  font-family: Georgia, 'Times New Roman', ui-serif, serif;
  font-size: 1.45rem;
  font-weight: 600;
  color: #8a353a;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.95), rgba(255, 232, 232, 0.55));
  border: 1px solid rgba(184, 68, 75, 0.2);
  box-shadow: 0 8px 22px rgba(200, 79, 86, 0.12);
}

.chapter-label {
  margin: 0;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: #c84f56;
}

.chapter-title {
  margin: 6px 0 0;
  font-family: Georgia, 'Times New Roman', ui-serif, serif;
  font-size: clamp(1.55rem, 2.2vw, 2rem);
  font-weight: 600;
  letter-spacing: -0.02em;
  color: #1a1415;
  line-height: 1.15;
}

.chapter-prose {
  margin-top: 20px;
  max-width: 58ch;
}

.chapter-prose p {
  margin: 0;
  font-size: 1.06rem;
  line-height: 1.74;
  color: #4a3f41;
}

.chapter-prose em {
  font-style: italic;
  color: #4a3537;
}

.atelier {
  display: grid;
  grid-template-columns: 1fr;
  gap: 32px;
  margin-top: 28px;
  align-items: stretch;
}

.atelier-cell {
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid rgba(184, 68, 75, 0.1);
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 12px 36px rgba(44, 22, 24, 0.04);
}

.atelier-map {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.atelier-map :deep(.map-wrapper) {
  padding-top: 16px;
}

.folio {
  padding: 28px 28px 30px;
  border-radius: 22px;
  border: 1px dashed rgba(184, 68, 75, 0.28);
  background: linear-gradient(105deg, rgba(255, 252, 251, 0.55), rgba(255, 255, 255, 0.35));
}

.folio-muted {
  opacity: 0.92;
}

.folio-inner {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.folio-mark {
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  font-family: Georgia, ui-serif, serif;
  font-size: 1.1rem;
  font-weight: 600;
  color: #a8444b;
  border: 1px solid rgba(184, 68, 75, 0.22);
  background: rgba(255, 255, 255, 0.75);
}

.folio-title {
  margin: 0;
  font-family: Georgia, ui-serif, serif;
  font-size: 1.18rem;
  font-weight: 600;
  color: #241c1e;
}

.folio-text {
  margin: 10px 0 0;
  max-width: 58ch;
  font-size: 0.95rem;
  line-height: 1.65;
  color: #6b5a5c;
}

.folio-tag {
  margin: 14px 0 0;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #b07a80;
}

.folio-tag a {
  color: #b8444b;
  font-weight: 700;
}

.folio-tag a:hover {
  color: #8e2a32;
}

.site-footer {
  margin-top: 8px;
  padding: 22px 8px 8px;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 12px;
  border-top: 1px solid rgba(184, 68, 75, 0.12);
  font-size: 0.84rem;
  color: #8a7578;
}

.footer-line {
  margin: 0;
}

.footer-links {
  margin: 0;
}

.footer-links a {
  font-weight: 600;
  color: #b8444b;
}

@media (max-width: 900px) {
  .hero-content {
    grid-template-columns: 1fr;
  }

  .topbar {
    flex-direction: column;
    align-items: flex-start;
    margin-bottom: 28px;
  }

  .topbar-links {
    justify-content: flex-start;
  }
}

@media (max-width: 640px) {
  .hero,
  .content {
    padding-left: 18px;
    padding-right: 18px;
  }

  .hero-title {
    font-size: clamp(2.1rem, 10vw, 3.2rem);
  }

  .chapter {
    padding: 24px 18px 28px;
  }
}
</style>
