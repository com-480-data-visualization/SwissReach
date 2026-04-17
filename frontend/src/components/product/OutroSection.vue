<template>
  <section id="outro" class="page-section outro-shell">
    <div class="outro-grid">
      <div class="outro-copy">
        <p class="section-label">Closing</p>
        <h2 class="section-title">
          Mobility explains connection. Retail explains opportunity. SwissReach is useful because it keeps both in the same frame.
        </h2>
        <p class="section-text">
          The transport network tells us where Switzerland is well linked; the retail layer tells us what that linkage means for everyday life. Reading those layers together makes it easier to spot where a strong backbone really expands choice and where it still leaves daily opportunity uneven.
        </p>

        <div class="button-row outro-actions">
          <a class="button-primary" href="#hero">Back to top</a>
          <a class="button-secondary" href="https://swissreach.online/docs/">Read the methodology</a>
        </div>
      </div>

      <div class="outro-cards">
        <article class="outro-card section-frame">
          <span class="outro-card__label">Argument</span>
          <strong>Transport alone is not the whole story</strong>
          <p>The page deliberately moves from rail geometry to reachable supermarkets so “coverage” never stays abstract for long.</p>
        </article>
        <article class="outro-card section-frame">
          <span class="outro-card__label">Method</span>
          <strong>Open GTFS and POI layers stay visible</strong>
          <p>
            The current demo combines national timetable structure, station-level POI counts, and a branded supermarket export without pretending to be a live router.
          </p>
        </article>
      </div>
    </div>
  </section>
</template>

<style scoped>
.outro-shell {
  height: 100svh;
  min-height: 100svh;
  box-sizing: border-box;
  padding-top: var(--section-top-padding);
  padding-bottom: var(--section-bottom-padding);
  display: grid;
  align-items: center;
}

.outro-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.9fr);
  gap: clamp(1.5rem, 4vw, 3rem);
  align-items: start;
}

.outro-copy {
  max-width: 42rem;
}

.outro-actions {
  margin-top: 1.8rem;
}

.outro-cards {
  display: grid;
  gap: 1rem;
}

.outro-card {
  display: grid;
  gap: 0.55rem;
  padding: 1.4rem;
  border-radius: var(--radius-card);
}

.outro-card__label {
  color: var(--brand);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.outro-card strong {
  color: var(--ink-strong);
  font-size: 1.05rem;
}

.outro-card p {
  margin: 0;
  color: var(--ink-soft);
  line-height: 1.65;
}

@media (max-width: 900px) {
  .outro-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .outro-shell {
    height: 100dvh;
    min-height: 100dvh;
    align-items: start;
  }
}
</style>
