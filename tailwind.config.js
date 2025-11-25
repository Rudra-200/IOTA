/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                bg: 'rgb(var(--bg) / <alpha-value>)',
                secondary: 'rgb(var(--bg-secondary) / <alpha-value>)',
                card: 'rgb(var(--card) / <alpha-value>)',
                stroke: 'rgb(var(--stroke) / <alpha-value>)',
                ink: 'rgb(var(--ink) / <alpha-value>)',
                muted: 'rgb(var(--muted) / <alpha-value>)',
                ember: 'rgb(var(--ember) / <alpha-value>)',
                royal: 'rgb(var(--royal) / <alpha-value>)',
                mint: 'rgb(var(--mint) / <alpha-value>)',
                gold: 'rgb(var(--gold) / <alpha-value>)',
                // Mapping 'surface' to card as it's used in some files but not in tokens
                surface: 'rgb(var(--card) / <alpha-value>)',
            },
            borderRadius: {
                card: 'var(--radius-card)',
                chip: 'var(--radius-chip)',
            },
            fontFamily: {
                display: ['var(--font-display)', 'sans-serif'],
                body: ['var(--font-body)', 'sans-serif'],
            }
        },
    },
    plugins: [
        require('@tailwindcss/typography'),
    ],
}
