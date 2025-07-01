/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './main/renderer/index.html',
    './main/renderer/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        'deploybot': {
          primary: '#3B82F6',
          secondary: '#10B981',
          accent: '#F59E0B',
          dark: '#1F2937',
          light: '#F9FAFB',
        }
      },
      fontFamily: {
        'mono': ['SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', 'monospace'],
      },
    },
  },
  plugins: [],
} 