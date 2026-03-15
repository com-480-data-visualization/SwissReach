<script setup lang="ts">
const docsUrl = 'https://swissreach.online/docs'
const githubUrl = 'https://github.com/com-480-data-visualization/SwissReach'
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
          <a :href="docsUrl" target="_blank" rel="noreferrer">Docs</a>
          <a :href="githubUrl" target="_blank" rel="noreferrer">GitHub</a>
        </div>
      </nav>

      <section class="hero-content">
        <div class="hero-copy">
          <p class="eyebrow">EPFL COM-480 Project</p>
          <h1>Nationwide rail accessibility in Switzerland.</h1>
          <p class="hero-text">
            SwissReach is an interactive visualization project built around Swiss public transport
            timetable data. The current website serves as the official landing page for the project,
            while the full interactive experience is still under development.
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
          <img
            alt="SwissReach reachability preview"
            class="preview-image"
            src="/preview/lausanne_reachability_0800_6h.png"
          >
        </div>
      </section>
    </header>

    <main class="content">
      <section class="panel">
        <h2>About the project</h2>
        <p>
          SwissReach explores accessibility through the Swiss rail network using timetable-based
          reachability analysis, station-level aggregation, and large-scale visual storytelling.
        </p>
      </section>

      <section class="panel panel-grid">
        <div>
          <h2>Current status</h2>
          <p>
            The interactive visualization website is in progress. At this stage, the project
            documentation, methodology, and milestone report are already available online.
          </p>
        </div>

        <div>
          <h2>Useful links</h2>
          <ul class="link-list">
            <li><a :href="docsUrl" target="_blank" rel="noreferrer">swissreach.online/docs</a></li>
            <li><a :href="githubUrl" target="_blank" rel="noreferrer">GitHub repository</a></li>
          </ul>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
:global(body) {
  margin: 0;
  font-family:
    Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background:
    radial-gradient(circle at top, rgba(200, 79, 86, 0.08), transparent 35%),
    linear-gradient(180deg, #fffaf9 0%, #fff 30%, #fff 100%);
  color: #271f20;
}

:global(a) {
  color: inherit;
  text-decoration: none;
}

:global(*) {
  box-sizing: border-box;
}

.page-shell {
  min-height: 100vh;
}

.hero {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 24px 40px;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 48px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-logo {
  width: 44px;
  height: 44px;
  object-fit: contain;
}

.brand-name {
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: 0.01em;
}

.topbar-links {
  display: flex;
  gap: 18px;
  font-size: 0.95rem;
  color: #7a4b4f;
}

.topbar-links a:hover,
.link-list a:hover {
  color: #b8444b;
}

.hero-content {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr);
  gap: 40px;
  align-items: center;
}

.eyebrow {
  margin: 0 0 10px;
  font-size: 0.9rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #b8444b;
}

.hero-copy h1 {
  margin: 0;
  max-width: 11ch;
  font-size: clamp(2.8rem, 6vw, 5.3rem);
  line-height: 0.98;
  letter-spacing: -0.04em;
}

.hero-text {
  max-width: 60ch;
  margin: 20px 0 0;
  font-size: 1.08rem;
  line-height: 1.7;
  color: #5b4b4d;
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
  min-height: 46px;
  padding: 0 18px;
  border-radius: 999px;
  font-weight: 600;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    background-color 0.2s ease;
}

.button:hover {
  transform: translateY(-1px);
}

.button-primary {
  background: #c84f56;
  color: white;
  box-shadow: 0 10px 24px rgba(200, 79, 86, 0.2);
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
  justify-content: center;
}

.preview-image {
  width: min(100%, 560px);
  border-radius: 22px;
  border: 1px solid rgba(184, 68, 75, 0.12);
  box-shadow: 0 18px 60px rgba(64, 24, 26, 0.12);
  background: white;
}

.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px 56px;
  display: grid;
  gap: 20px;
}

.panel {
  padding: 26px 28px;
  border: 1px solid rgba(184, 68, 75, 0.1);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 10px 40px rgba(44, 22, 24, 0.04);
}

.panel h2 {
  margin: 0 0 12px;
  font-size: 1.15rem;
}

.panel p,
.link-list {
  margin: 0;
  line-height: 1.7;
  color: #5b4b4d;
}

.panel-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 24px;
}

.link-list {
  padding-left: 20px;
}

.link-list li + li {
  margin-top: 8px;
}

@media (max-width: 900px) {
  .hero-content,
  .panel-grid {
    grid-template-columns: 1fr;
  }

  .hero-copy h1 {
    max-width: none;
  }

  .topbar {
    flex-direction: column;
    align-items: flex-start;
    margin-bottom: 32px;
  }
}

@media (max-width: 640px) {
  .hero,
  .content {
    padding-left: 18px;
    padding-right: 18px;
  }

  .hero-copy h1 {
    font-size: clamp(2.4rem, 12vw, 4rem);
  }
}
</style>
