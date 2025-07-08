/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#3a86ff', // Protein Blue
        },
        secondary: {
          DEFAULT: '#43aa8b', // Leaf Green
        },
        background: {
          light: '#ffffff',
          dark: '#181818',
        },
        text: {
          DEFAULT: '#222222', // Charcoal
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      }
    },
  },
  plugins: [],
} 