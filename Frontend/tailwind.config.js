/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      colors: {
        forest: {
          50:  '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
          950: '#052e16',
        },
        amber: {
          50:  '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
          950: '#451a03',
        },
        parchment: {
          50:  '#fefef9',
          100: '#fafaf0',
          200: '#f5f5e8',
          300: '#ededd5',
          400: '#e0dfca',
          500: '#cccbb5',
        },
        // Dark mode surfaces
        dark: {
          base:    '#0b1a10',
          surface: '#0f2318',
          card:    '#152d1e',
          elevated:'#1a3826',
          border:  '#1f4530',
          muted:   '#2a5940',
        },
      },
      animation: {
        'fade-in':  'fadeIn 0.35s ease-out',
        'slide-up': 'slideUp 0.35s ease-out',
        'leaf':     'leaf 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn:  { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
        slideUp: { '0%': { opacity: '0', transform: 'translateY(10px)' }, '100%': { opacity: '1', transform: 'translateY(0)' } },
        leaf:    { '0%,100%': { transform: 'rotate(-3deg)' }, '50%': { transform: 'rotate(3deg)' } },
      },
      boxShadow: {
        card:      '0 1px 3px rgba(0,0,0,0.06), 0 4px 14px rgba(0,0,0,0.05)',
        'card-hover': '0 4px 20px rgba(0,0,0,0.10), 0 8px 30px rgba(0,0,0,0.07)',
        glow:      '0 0 20px rgba(34,197,94,0.20)',
        'amber-glow': '0 0 20px rgba(251,191,36,0.25)',
      },
    },
  },
  plugins: [],
};
