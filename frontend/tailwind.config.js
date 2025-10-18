/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx,js,jsx}",
    // include Django templates so classes used there aren't purged:
    "../templates/**/*.{html,htm}"
  ],
  theme: { extend: {} },
  plugins: [],
}