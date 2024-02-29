/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["../apps/**/templates/*.{html,js}"],
  theme: {
    extend: {},
  },
  plugins: [require("daisyui")],
  darkMode: 'selector',
}

