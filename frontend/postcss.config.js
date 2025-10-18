/** @type {import('postcss-load-config').Config} */
export default {
  plugins: {
    '@tailwindcss/postcss': {},   // ← new in Tailwind v4
    autoprefixer: {},
  },
};
