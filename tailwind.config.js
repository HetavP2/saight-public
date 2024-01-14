/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./saight/templates/*.html"],
  theme: {
    extend: {
      colors: {
        staple_teal: "#5CE1E6",
        staple_purple: "#9416B8",
        sdg_3: "#299b45",
        sdg_9: "#f36e1f",
        sdg_10: "#e01a83",
      },
    },
  },
  plugins: [],
};

