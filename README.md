# RetainIQ

Predict churn. Understand why. Take action.

A frontend-only, beginner-friendly SaaS-style React app for checking churn risk, explaining results, and viewing revenue impact.

## What it does

- Explains churn in plain language.
- Shows whether a customer is low, medium, or high risk.
- Suggests simple actions to reduce churn.
- Includes a what-if simulator to test changes instantly.

## Stack

- React + TypeScript + Vite
- Tailwind CSS
- Recharts
- Framer Motion

## Setup

### Run locally

```powershell
cd frontend
npm install
npm run dev
```

Open app: http://127.0.0.1:5173

### Build for production

```powershell
cd frontend
npm run build
```

### Run tests

```powershell
pytest -q
```

## Pages

- Dashboard
- Check Customer
- Insights
- Revenue Impact
- Help

## Deploy

- Frontend: Vercel (root = `frontend/`, build command `npm run build`, output = `dist`)
- Backend is optional and not required for deployment.

## Notes

- Frontend production build: passed.

