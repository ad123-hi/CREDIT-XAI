/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: "#0b0f19",
          slate: "#151d30",
          card: "#1e2942",
          accent: "#4f46e5",
          highlight: "#8b5cf6",
          text: "#f3f4f6"
        }
      }
    },
  },
  plugins: [],
}
