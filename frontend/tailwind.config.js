/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        slate: {
          850: '#151f32',
          950: '#0b1120',
        },
        theme: {
          bg: 'var(--color-bg-page)',
          card: 'var(--color-bg-card)',
          'card-hover': 'var(--color-bg-card-hover)',
          subtle: 'var(--color-bg-subtle)',
          'subtle-2': 'var(--color-bg-subtle-2)',
          border: 'var(--color-border)',
          'border-subtle': 'var(--color-border-subtle)',
          text: 'var(--color-text-main)',
          'text-sub': 'var(--color-text-sub)',
          'text-muted': 'var(--color-text-muted)',
          backdrop: 'var(--color-backdrop)',

          // Semantic
          primary: 'var(--color-primary)',
          'primary-bg': 'var(--color-primary-bg)',
          'primary-border': 'var(--color-primary-border)',

          success: 'var(--color-success)',
          'success-bg': 'var(--color-success-bg)',
          'success-border': 'var(--color-success-border)',

          warning: 'var(--color-warning)',
          'warning-bg': 'var(--color-warning-bg)',
          'warning-border': 'var(--color-warning-border)',

          danger: 'var(--color-danger)',
          'danger-bg': 'var(--color-danger-bg)',
          'danger-border': 'var(--color-danger-border)',
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      }
    },
  },
  plugins: [],
}
