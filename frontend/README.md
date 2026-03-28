# PYME-Ledger Frontend

Modern accounting dashboard for Peruvian SMEs built with React + Vite.

## Features

- **Dashboard Financiero** - Key metrics and KPIs with currency toggle (PEN/USD)
- **Plan de Cuentas PCGE** - Interactive account visualization
- **Transacciones** - Transaction list with PCGE codes
- **Reportes** - Balance General, Estado de Resultados
- **Multi-moneda** - Full PEN/USD support

## Design Philosophy

See [DESIGN.md](./DESIGN.md) for the complete design system documentation.

## Quick Start

```bash
# Install dependencies
npm install

# Development server
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

## Tech Stack

- React 18
- Vite
- Lucide React (icons)
- CSS Variables (design system)

## Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/          # Page-level components
│   ├── styles/         # Global CSS + app styles
│   ├── utils/          # Helper functions
│   ├── data/           # Mock data
│   ├── App.jsx
│   └── main.jsx
├── public/
│   └── favicon.svg
├── index.html
└── package.json
```

## Design System

- **Colors**: Deep emerald (#0D5C4A), warm cream (#F5F0E8), amber accent (#D4A853)
- **Typography**: Syne (display), Plus Jakarta Sans (body)
- **Style**: Neo-Editorial Brutalism - bold typography, geometric precision, professional fintech aesthetic

## Future Enhancements

- [ ] Backend API integration with Beancount
- [ ] Plan de Cuentas interactive tree view
- [ ] Transaction entry forms
- [ ] Report generation (Balance, Income Statement)
- [ ] Dark mode
- [ ] Responsive mobile navigation
