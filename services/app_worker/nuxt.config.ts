export default defineNuxtConfig({
  // (optional) Enable the Nuxt devtools
  devtools: { enabled: true },
  css: ['~/assets/css/main.css'],
  postcss: {
    plugins: {
      tailwindcss: {},
      autoprefixer: {},
    },
  },

  // Enable SSG
  ssr: false,

  // Enables the development server to be discoverable by other devices when running on iOS physical devices
  devServer: { 
    host: process.env.TAURI_DEV_HOST || 
    // '172.20.10.7'
    'localhost'
  },

  vite: {
    // Better support for Tauri CLI output
    clearScreen: false,
    // Enable environment variables
    // Additional environment variables can be found at
    // https://v2.tauri.app/reference/environment-variables/
    envPrefix: ['VITE_', 'TAURI_'],
    server: {
      // Tauri requires a consistent port
      strictPort: true,
    },
  },

  app: {
    head: {
      title: 'My Nuxt App', // Optional: set a title for your application
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { hid: 'description', name: 'description', content: 'My Nuxt.js project' },
      ],
      script: [
        { src: 'https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@latest', async: true }, // Add your CDN link here
      ],
    },
  },

  compatibilityDate: '2024-10-19',
  modules: ['@nuxtjs/tailwindcss']
});