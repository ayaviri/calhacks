/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./app.vue",
    "./error.vue",
  ],
  theme: {
    extend: {
      colors: {
        "dark-green": "#1E201E",
        "grey-green": "#3C3D37",
        "gr": "#697565",
        "beige": "ECDFCC",
      },
      fontFamily: {
        'mono': ["Space Mono"]
      },
    },
  },
  plugins: [],
}

