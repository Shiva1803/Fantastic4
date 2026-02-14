/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // x402.org-inspired LIGHT MODE color palette
        'x402': {
          'white': '#ffffff',
          'light-gray': '#f8f8f8',
          'border': '#d0d0d0',
          'text-primary': '#1a1a1a',
          'text-secondary': '#666666',
          'code-bg': '#f5f5f5',
          'accent': '#000000',
          'amber': '#fbbf24',
        },
      },
      fontFamily: {
        sans: [
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Oxygen',
          'Ubuntu',
          'Cantarell',
          'Fira Sans',
          'Droid Sans',
          'Helvetica Neue',
          'Arial',
          'sans-serif',
        ],
        mono: [
          'Consolas',
          'Monaco',
          'Andale Mono',
          'Ubuntu Mono',
          'monospace',
        ],
      },
      fontSize: {
        'hero': ['3rem', { lineHeight: '1.1', fontWeight: '700' }],
        'display': ['2.5rem', { lineHeight: '1.2', fontWeight: '700' }],
      },
      lineHeight: {
        'relaxed': '1.7',
        'loose': '1.8',
      },
      borderRadius: {
        'minimal': '2px',
        'subtle': '4px',
      },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-in',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}

