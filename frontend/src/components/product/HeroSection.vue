<script setup lang="ts">
import { heroPreviewUrl } from '@/content/productStory'
</script>

<template>
  <section id="hero" class="page-section hero-shell">
    <div class="hero-grid">
      <div class="hero-copy">
        <span class="eyebrow-pill">Swiss Mobility & Infrastructure Reachability Analysis</span>
        <h1 class="hero-title">
          <span class="text-brand">SwissReach</span><br />
          everyday reachability, visualized Switzerland
        </h1>

        <p class="hero-summary">
          Swiss public transport, retail density, and everyday access in one national view.
        </p>

        <div class="button-row hero-actions">
          <a class="button-primary" href="#story">Enter</a>
          <a class="button-secondary" href="https://swissreach.online/docs/">Docs</a>
        </div>

        <div class="hero-guidance">
          <span class="hero-guidance__line" />
          <span class="hero-guidance__text">Scroll to continue</span>
        </div>
      </div>

      <div class="hero-visual section-frame">
        <figure class="hero-figure">
          <div class="hero-figure__head">
            <span>Morning reachability</span>
            <span>Lausanne, 08:00</span>
          </div>

          <div class="hero-figure__image-wrap">
            <img
              :src="heroPreviewUrl"
              alt="SwissReach morning reachability map preview"
              class="hero-figure__image"
              loading="eager"
              fetchpriority="high"
            />
          </div>

          <div class="hero-figure__footer">
            <div class="hero-note">
              <strong>Nationwide rail backbone</strong>
              <span>Swiss GTFS is filtered and collapsed into 1,938 logical rail stations.</span>
            </div>
            <div class="hero-note">
              <strong>Accessibility plus amenities</strong>
              <span>Connecting timetable reachability with supermarkets, schools, hospitals, and IKEA.</span>
            </div>
          </div>
        </figure>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero-shell {
  height: 100svh;
  min-height: 100svh;
  box-sizing: border-box;
  padding-top: var(--section-top-padding);
  padding-bottom: var(--section-bottom-padding);
  display: grid;
  align-items: center;
}

.hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.04fr) minmax(0, 0.96fr);
  gap: clamp(2rem, 4vw, 4rem);
  align-items: center;
}

.hero-copy {
  padding: clamp(1rem, 2vw, 1.5rem) 0;
}

.hero-title {
  margin: 1.15rem 0 0;
  max-width: 40ch;
  color: var(--ink-strong);
  font-size: clamp(2.4rem, 4.2vw, 3.8rem);
  line-height: 1.05;
  letter-spacing: -0.02em;
  font-weight: 700;
}

.hero-actions {
  margin-top: 1.9rem;
}

.hero-summary {
  margin: 1.2rem 0 0;
  max-width: 38rem;
  color: var(--ink-soft);
  font-size: 1.03rem;
  line-height: 1.7;
}

.text-brand {
  color: var(--brand);
}

.hero-guidance {
  display: inline-flex;
  align-items: center;
  gap: 0.9rem;
  margin-top: 2.75rem;
  color: var(--ink-soft);
  font-size: 0.85rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero-guidance__line {
  width: 3.8rem;
  height: 1px;
  background: linear-gradient(90deg, rgba(189, 45, 45, 0), rgba(189, 45, 45, 0.42));
}

.hero-visual {
  position: relative;
  border-radius: var(--radius-shell);
  padding: 1rem;
}

.hero-figure {
  margin: 0;
  display: grid;
  gap: 1rem;
}

.hero-figure__head,
.hero-figure__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.hero-figure__head {
  color: var(--ink-soft);
  font-size: 0.84rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero-figure__image-wrap {
  overflow: hidden;
  border-radius: calc(var(--radius-shell) - 8px);
  border: 1px solid rgba(33, 28, 26, 0.08);
  background: #ebe8e4;
}

.hero-figure__image {
  width: 100%;
  height: auto;
}

.hero-figure__footer {
  align-items: stretch;
}

.hero-note {
  flex: 1;
  display: grid;
  gap: 0.35rem;
  padding: 1rem 1.05rem;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(33, 28, 26, 0.07);
}

.hero-note strong {
  color: var(--ink-strong);
  font-size: 0.92rem;
}

.hero-note span {
  color: var(--ink-soft);
  font-size: 0.85rem;
  line-height: 1.55;
}

@media (max-width: 960px) {
  .hero-grid {
    grid-template-columns: 1fr;
  }

  .hero-title {
    max-width: 14ch;
  }
}

@media (max-width: 720px) {
  .hero-shell {
    height: 100dvh;
    min-height: 100dvh;
    align-items: start;
  }

  .hero-title {
    font-size: clamp(2.1rem, 10vw, 3.1rem);
  }

  .hero-figure__head,
  .hero-figure__footer {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
