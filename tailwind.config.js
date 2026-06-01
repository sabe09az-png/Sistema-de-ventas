/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./juegos/templates/**/*.html",
    "./**/templates/**/*.html", 
    "./**/*.py",
  ],
  theme: {
    extend: {
      colors: {
        'gamezher-bg': '#000000',      // Negro puro
        'gamezher-header': '#1a1a1a',  // Negro oscuro para header
        'gamezher-accent': '#3b82f6',  // Azul para acentos
      },
    },
  },
  plugins: [],
}