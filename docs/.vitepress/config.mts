import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  base: '/docs/',
  title: "SwissReach Docs",
  description: "Documentation for SwissReach, a nationwide Swiss rail accessibility visualization project for EPFL COM480.",
  head: [
    ['link', { rel: 'icon', type: 'image/png', href: '/logo/SwissReach_vectorized.png' }],
  ],
  themeConfig: {
    logo: '/logo/SwissReach_vectorized.png',
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Milestone 1 Report', link: '/milestone1' },
      { text: 'Methodology', link: '/methodology' },
      { text: 'Related Work', link: '/related-work' },
    ],

    sidebar: [
      {
        text: 'SwissReach',
        items: [
          { text: 'Project Home', link: '/' },
          { text: 'Milestone 1 Report', link: '/milestone1' },
          { text: 'Methodology', link: '/methodology' },
          { text: 'Related Work', link: '/related-work' },
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/com-480-data-visualization/SwissReach' }
    ]
  }
})
