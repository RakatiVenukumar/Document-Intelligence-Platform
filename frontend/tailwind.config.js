/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['"Inter"', 'sans-serif'],
      },
      colors: {
        canvas: '#f8f4ec',
        ink: '#10212e',
        accent: '#d94f30',
        moss: '#2f6f68',
        sand: '#e7dccb',
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(217, 79, 48, 0.16), 0 24px 80px rgba(16, 33, 46, 0.16)',
      },
      backgroundImage: {
        'hero-grid':
          'radial-gradient(circle at top left, rgba(217, 79, 48, 0.18), transparent 28%), radial-gradient(circle at right 25%, rgba(47, 111, 104, 0.18), transparent 24%), linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(248, 244, 236, 1))',
      },
    },
  },
  plugins: [],
}
