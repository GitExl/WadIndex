// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  css: [
    '@/node_modules/@material-design-icons/font/index.css',
    '@/assets/scss/base.scss',
  ],

  vite: {
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: '@use "~/assets/scss/variables.scss" as *; @use "~/assets/scss/mixins.scss" as *;',
          api: 'modern'
        },
      },
    },
  },

  app: {
    head: {
      charset: 'utf-8',
      viewport: 'width=device-width, initial-scale=1',
    }
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.API_BASE_URL,
      otherUrl: process.env.STORAGE_BASE_URL
    }
  },

  compatibilityDate: '2024-11-17'
})
