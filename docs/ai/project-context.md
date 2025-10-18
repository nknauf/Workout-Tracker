# MoreSore — Project Context

Goal: Bodybuilding social + coaching app: daily logs (workouts, meals, macros, pump pics), TikTok-style feed, and a chat Agent that knows user history.

Stack: Django 5 + Postgres; React 18 + TS + Tailwind v4 (Vite).  
Build: `npm run build` → `static/repdeck/index.js` (Social) and `static/home/index.js` (Home).  
Mount IDs: `#repdeck-root`, `#home-root`.  
Media: MEDIA_URL/ROOT, dev via urls.py static().  
No Next.js; no extra client deps.

Pages: Home, Profile, Social, Agent, Progress (header shows exactly these).  
Contracts: RepDeck does **not** fetch; receives `posts` and handlers. All social APIs require login.
