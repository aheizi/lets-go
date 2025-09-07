/** @type {import('tailwindcss').Config} */

export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    container: {
      center: true,
    },
    extend: {
      colors: {
        // Let'sGo Brand Colors
        brand: {
          orange: '#FF6B35',
          blue: '#4ECDC4',
          yellow: '#FFE66D',
          pink: '#FF8B94',
        },
        // Extended color palette
        primary: {
          50: '#FFF4F1',
          100: '#FFE8E1',
          200: '#FFD1C3',
          300: '#FFB5A0',
          400: '#FF8B6B',
          500: '#FF6B35', // Main brand orange
          600: '#E55A2B',
          700: '#CC4A21',
          800: '#B33A17',
          900: '#992A0D',
        },
        secondary: {
          50: '#F0FFFE',
          100: '#E1FFFC',
          200: '#C3FFF9',
          300: '#A0FFF5',
          400: '#6BFFEE',
          500: '#4ECDC4', // Main brand blue
          600: '#3BB8B0',
          700: '#2A9B94',
          800: '#1A7E78',
          900: '#0A615C',
        },
        accent: {
          yellow: '#FFE66D',
          pink: '#FF8B94',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Poppins', 'system-ui', 'sans-serif'],
      },
      animation: {
        'bounce-slow': 'bounce 2s infinite',
        'pulse-slow': 'pulse 3s infinite',
        'float': 'float 3s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
      boxShadow: {
        'brand': '0 4px 14px 0 rgba(255, 107, 53, 0.15)',
        'brand-lg': '0 10px 25px 0 rgba(255, 107, 53, 0.2)',
        'secondary': '0 4px 14px 0 rgba(78, 205, 196, 0.15)',
        'secondary-lg': '0 10px 25px 0 rgba(78, 205, 196, 0.2)',
      },
      backgroundImage: {
        'gradient-brand': 'linear-gradient(135deg, #FF6B35 0%, #FF8B94 100%)',
        'gradient-secondary': 'linear-gradient(135deg, #4ECDC4 0%, #FFE66D 100%)',
        'gradient-hero': 'linear-gradient(135deg, #FF6B35 0%, #4ECDC4 50%, #FFE66D 100%)',
      },
    },
  },
  plugins: [],
};
