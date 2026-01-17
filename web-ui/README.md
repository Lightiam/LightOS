# LightOS Web UI

Modern React + TypeScript web interface for LightOS DCIM (Data Center Infrastructure Management).

This UI is integrated from LightRail_AI_Aurora and provides comprehensive datacenter management capabilities.

## Features

- **Dashboard** - Real-time overview of infrastructure and workloads
- **Fleet Explorer** - Node-level monitoring and capacity planning
- **DCIM Control** - Power, thermal, and fabric management
- **HCI Orchestrator** - Hyper-converged infrastructure management
- **Workloads** - AI/ML job orchestration
- **Cost Control** - Cost analytics and optimization
- **Settings & Documentation** - Configuration and help

## Technology Stack

- **Frontend Framework**: React 18
- **Language**: TypeScript
- **Build Tool**: Vite
- **Routing**: React Router v6
- **UI Components**: Lucide Icons
- **Styling**: Tailwind CSS (inline classes)

## Development

### Prerequisites

- Node.js 18+ and npm
- LightOS DCIM API running on port 8001

### Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The dev server will start on http://localhost:3000 with API proxy to localhost:8001.

### Available Scripts

```bash
# Development server with hot reload
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check

# Linting
npm run lint
```

## Project Structure

```
web-ui/
├── components/          # Reusable React components
│   ├── AIAssistant.tsx
│   ├── AuroraBackground.tsx
│   ├── Header.tsx
│   ├── Sidebar.tsx
│   └── StatsCard.tsx
├── pages/              # Page components
│   ├── Dashboard.tsx
│   ├── FleetExplorer.tsx
│   ├── DCIMControl.tsx
│   ├── HCIOrchestrator.tsx
│   ├── Workloads.tsx
│   ├── CostControl.tsx
│   ├── Settings.tsx
│   └── Documentation.tsx
├── services/           # Data services and API
│   └── mockData.ts
├── types.ts           # TypeScript type definitions
├── App.tsx            # Main application component
├── index.tsx          # Application entry point
├── index.html         # HTML template
├── vite.config.ts     # Vite configuration
├── tsconfig.json      # TypeScript configuration
└── package.json       # Dependencies and scripts
```

## Building for Production

```bash
npm run build
```

This creates an optimized production build in the `dist/` directory:

```
dist/
├── index.html
└── assets/
    ├── index-[hash].js
    ├── index-[hash].css
    └── [other assets]
```

## API Integration

The UI communicates with the LightOS DCIM API:

- **Base URL**: `/api` (proxied in dev, direct in production)
- **WebSocket**: `/ws/dcim` for real-time telemetry

### API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/providers` | GET | Infrastructure providers |
| `/api/jobs` | GET | Workload jobs |
| `/api/sites` | GET | Datacenter sites |
| `/api/racks` | GET | Rack information |
| `/api/nodes` | GET | Node metrics |
| `/api/hci-nodes` | GET | HCI nodes |
| `/api/tenant-isolation` | GET | Tenant isolation data |
| `/api/dcim/kpi` | GET | KPI summary |
| `/api/dcim/power` | GET | Power metrics |
| `/api/dcim/peak-shaving` | GET | Peak shaving status |
| `/ws/dcim` | WebSocket | Real-time telemetry |

## Environment Variables

Create a `.env.local` file for local development:

```env
VITE_API_BASE_URL=http://localhost:8001
GEMINI_API_KEY=your-gemini-api-key  # Optional, for AI features
```

## Deployment

The web UI is served by the FastAPI backend in production:

1. Build the frontend: `npm run build`
2. The backend serves static files from `dist/`
3. API requests go to `/api/*`
4. WebSocket connections to `/ws/*`

See `../deployment/vps/README.md` for full deployment instructions.

## Development Tips

### Hot Module Replacement

Vite provides instant HMR. Changes to components are reflected immediately without full page reload.

### API Proxy

During development, API calls to `/api` are automatically proxied to `http://localhost:8001`. Make sure the DCIM API is running:

```bash
cd ../dcim-api
python main.py
```

### Type Safety

The project uses TypeScript for type safety. All types are defined in `types.ts`. Run type checking:

```bash
npm run type-check
```

### Component Development

Components follow React functional component patterns with hooks:

```tsx
import React, { useState } from 'react';

const MyComponent: React.FC = () => {
  const [state, setState] = useState(initialValue);

  return <div>...</div>;
};

export default MyComponent;
```

## Styling

The UI uses Tailwind-style utility classes for styling. Common patterns:

- Glass morphism: `glass-panel` class
- Aurora gradient: `aurora-gradient` class
- Dark theme: Base colors use slate-900, slate-800, etc.
- Accent colors: Green (`#00FF41`) and Blue (`#0ea5e9`)

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Performance

- Code splitting by route
- Lazy loading of components
- Optimized production builds
- Asset caching with versioned filenames

## Troubleshooting

### Build Fails

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### API Connection Issues

Check that the backend is running:

```bash
curl http://localhost:8001/health
```

### Type Errors

Run type checking to see all errors:

```bash
npm run type-check
```

## Contributing

When adding new features:

1. Add types to `types.ts`
2. Create components in `components/` or pages in `pages/`
3. Update API endpoints in backend if needed
4. Test in development mode
5. Build and verify production build

## License

See LICENSE in the root repository.
