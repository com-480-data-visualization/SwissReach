import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  base: '/docs/',
  title: "SwissReach Docs",
  description: "Milestone 1 documentation for SwissReach, a nationwide Swiss rail accessibility visualization project for EPFL COM480.",
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Milestone 1', link: '/milestone1' },
      { text: 'Methodology', link: '/methodology' },
      { text: 'Related Work', link: '/related-work' },
    ],

    sidebar: [
      {
        text: 'SwissReach',
        items: [
          { text: 'Project Home', link: '/' },
          { text: 'Milestone 1', link: '/milestone1' },
          { text: 'Methodology', link: '/methodology' },
          { text: 'Related Work', link: '/related-work' },
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com' }
    ]
  }
})
