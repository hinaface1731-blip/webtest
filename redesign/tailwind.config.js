/** Сборка: npx tailwindcss@3.4.16 -c tailwind.config.js -i tailwind.input.css -o assets/styles.css --minify */
module.exports = {
  content: ['./*.html'],
  theme: {
    extend: {
      colors: {
        graphite: { 950: '#0B0D10', 900: '#0F1215', 800: '#161A1F', 700: '#1F252B', 600: '#2A3139' },
        steel: { 500: '#8A949E', 400: '#A9B2BA', 300: '#C9D0D6' },
        signal: { 500: '#FF6A13', 600: '#E85A07', 400: '#FF8A45' },
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'system-ui', 'sans-serif'],
        cond: ['"IBM Plex Sans Condensed"', '"IBM Plex Sans"', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
    },
  },
};
