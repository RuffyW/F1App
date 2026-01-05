import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui"],
      },
      colors: {
        background: "#f8fafc",
        surface: "#ffffff",
        accent: "#2563eb",
        muted: "#e2e8f0",
      },
      boxShadow: {
        soft: "0 20px 50px -24px rgba(15, 23, 42, 0.25)",
      },
      transitionTimingFunction: {
        gentle: "cubic-bezier(0.4, 0, 0.2, 1)",
      },
    },
  },
  plugins: [],
};

export default config;
