import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          900: "#10182B", // sidebar / nav background
          700: "#2B3A55", // secondary headings on light surfaces
          500: "#4A5B7A",
        },
        surface: {
          DEFAULT: "#F5F6F8", // app background
          card: "#FFFFFF",
          border: "#E4E6EB",
        },
        brass: {
          DEFAULT: "#B08D57", // signature accent
          light: "#D9C29A",
          dark: "#8C6D3F",
        },
        priority: {
          critical: "#C1443D",
          high: "#C98A2C",
          medium: "#3E6FA8",
          low: "#6B7280",
        },
        state: {
          success: "#2F7D5D",
          warn: "#C98A2C",
          danger: "#C1443D",
        },
      },
      fontFamily: {
        display: ["var(--font-fraunces)", "Georgia", "serif"],
        body: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(16, 24, 43, 0.04), 0 1px 8px rgba(16, 24, 43, 0.04)",
      },
    },
  },
  plugins: [],
};

export default config;
