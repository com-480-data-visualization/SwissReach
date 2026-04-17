<script setup lang="ts">
import { brandLogoUrl } from '@/content/productStory'
</script>

<template>
  <header class="page-section topbar-wrap">
    <div class="topbar section-frame">
      <a class="brand" href="#hero" aria-label="SwissReach homepage">
        <img :src="brandLogoUrl" alt="SwissReach" class="brand-logo" />
        <span class="brand-name">SwissReach</span>
      </a>

      <nav class="nav-links" aria-label="Primary">
        <a href="#hero">Home</a>
        <a href="#intro">Overview</a>
        <a href="#story">Experience</a>
        <a href="#outro">Closing</a>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.topbar-wrap {
  position: sticky;
  top: 0;
  z-index: 20;
  padding-top: 1rem;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 0.95rem 1.1rem;
  border-radius: 999px;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 0.85rem;
  min-width: 0;
}

.brand-logo {
  width: 2.3rem;
  height: 2.3rem;
  object-fit: contain;
}

.brand-name {
  color: var(--ink-strong);
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.nav-links {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.4rem;
}

.nav-links a {
  padding: 0.55rem 0.85rem;
  border-radius: 999px;
  color: var(--ink-soft);
  font-size: 0.92rem;
  transition:
    background-color 180ms ease,
    color 180ms ease;
}

.nav-links a:hover {
  color: var(--ink-strong);
  background: rgba(255, 255, 255, 0.7);
}

@media (max-width: 720px) {
  .topbar-wrap {
    padding-top: 0.75rem;
  }

  .topbar {
    border-radius: 24px;
    align-items: flex-start;
    flex-direction: column;
  }

  .nav-links {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
