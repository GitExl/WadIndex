// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  css: ['@/assets/scss/base.scss'],
  vite: {
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: '@use "@/assets/scss/defs.scss" as *;',
        },
      },
    },
  },
  runtimeConfig: {
    public: {
      apiBase: process.env.API_BASE_URL,
      otherUrl: process.env.STORAGE_BASE_URL
    }
  }
})
