<template>
  <section id="outro" class="page-section outro-shell">
    <div class="outro-grid">
      <div class="outro-copy">
        <p class="section-label">Methodology</p>
        <h2 class="section-title">
          Built on open data from Swiss GTFS and structured POI datasets.
        </h2>
        <p class="section-text">
          By processing national timetables and combining them with geospatial amenity data, SwissReach provides a trustworthy sense of what daily movement really looks like and how infrastructure caters to public needs.
        </p>

        <div class="button-row outro-actions">
          <a class="button-primary" href="#hero">Back to top</a>
          <a class="button-secondary" href="https://swissreach.online/docs/">Read the methodology</a>
        </div>
      </div>

      <div class="outro-cards">
        <article class="outro-card section-frame">
          <span class="outro-card__label">Data Layer</span>
          <strong>Retail competition stories</strong>
          <p>A dedicated supermarket dataset supports Migros vs Coop density analysis and broader food-retail mapping.</p>
        </article>
        <article class="outro-card section-frame">
          <span class="outro-card__label">Data Layer</span>
          <strong>Consistent POI mappings</strong>
          <p>
            30-minute access counts for supermarkets, schools, and hospitals, alongside a 60-minute IKEA access coverage.
          </p>
        </article>
      </div>
    </div>
  </section>
</template>

<style scoped>
.outro-shell {
  min-height: 100svh;
  padding-top: clamp(5rem, 8vw, 7rem);
  padding-bottom: clamp(5rem, 8vw, 7rem);
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
    min-height: 100dvh;
    align-items: start;
    padding-top: 6.5rem;
    padding-bottom: 3rem;
  }
}
</style>
