/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Trading platform dark theme colors
        dark: {
          bg: '#0a0e1a',
          card: '#0f1419',
          border: '#1f2937',
          hover: '#1a1f2e',
        },
        accent: {
          blue: '#3b82f6',
          green: '#10b981',
          red: '#ef4444',
          yellow: '#f59e0b',
        },
      },
    },
  },
  plugins: [],
}
