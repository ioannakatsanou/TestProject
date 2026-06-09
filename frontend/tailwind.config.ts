import type { Config } from "tailwindcss";

export default {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#0d3b66",   // deep Greek-blue
          dark: "#08294a",
          light: "#1c5a99",
        },
        accent: "#f4a259",
      },
    },
  },
  plugins: [],
} satisfies Config;
