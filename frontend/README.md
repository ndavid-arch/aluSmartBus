# Frontend

React web app for ALU SmartBus: the student, driver and administrator screens, with a live map of the Rebero - ALU route.

## Run it locally

Needs Node.js 20 or newer.
The app talks to the backend through `/api`, which the dev server forwards to `http://localhost:8000`, so start the backend too (see `backend/README.md`).

```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173. The bare address goes to the student page.

## Before opening a pull request

```bash
npm run format   # consistent formatting (Prettier)
npm run lint     # no lint errors (ESLint)
npm run build    # type check and production build
```

## Layout

```
frontend/
├── src/
│   ├── main.tsx          # starts the app and switches on routing
│   ├── App.tsx           # the list of pages and their addresses
│   ├── index.css         # styles and the ALU colours
│   ├── components/       # pieces used on several pages (NavBar, RouteMap)
│   └── pages/            # one screen per role: student, driver, admin
├── public/               # files served as they are (favicon)
├── package.json          # packages and scripts (like requirements.txt)
└── package-lock.json     # exact versions of every package
```

## Tools

- React with TypeScript, built with Vite
- React Router for the /student, /driver and /admin pages
- Leaflet for the map; its tile provider is a setting (`VITE_TILE_URL`, `VITE_TILE_ATTRIBUTION` in `.env`, see `.env.example`), OpenStreetMap by default
- ESLint and Prettier for code quality
