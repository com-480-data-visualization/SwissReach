<template>
  <section id="outro" class="page-section outro-shell">
    <div class="outro-grid">
      <div class="outro-copy">
        <p class="section-label">Outro</p>
        <h2 class="section-title">
          The page closes the way the product reads: calm, direct and ready for the next layer of
          depth.
        </h2>
        <p class="section-text">
          Once the horizontal story ends, vertical scrolling returns naturally. The takeaway is
          concise: clearer reachability, stronger comparison and a more trustworthy sense of what
          daily movement really looks like across the network.
        </p>

        <div class="button-row outro-actions">
          <a class="button-primary" href="#hero">Back to top</a>
          <a class="button-secondary" href="#story">Replay the core story</a>
        </div>
      </div>

      <div class="outro-cards">
        <article class="outro-card section-frame">
          <span class="outro-card__label">Why it works</span>
          <strong>Story first, controls second</strong>
          <p>The experience leads with clarity and only then opens into richer comparison.</p>
        </article>
        <article class="outro-card section-frame">
          <span class="outro-card__label">What stays ready</span>
          <strong>Built for steady iteration</strong>
          <p>
            Each section is modular, restrained and prepared for future content without visual
            drift.
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
