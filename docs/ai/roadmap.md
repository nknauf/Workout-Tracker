# Roadmap

## M1 — Social foundation (templates/APIs cleanup)
- Feed is mount-only React page (RepDeck).
- `/api/posts/`: add `images[]` (ordered) + `likeCount`.
- Keep `post_form.html` minimal; `post_detail.html` optional “share” view.
- Seed: ensure multi-image and alt_text variety.

## M2 — Home + Agent (dashboard bubbles + chat UI)
- `/api/daily/today/` stub + wire to Home props.
- Home “Chatbot” UI calls `/api/chat/add-*` stubs; show success banners.

## M3 — Profile & Progress
- Profile page (public/private filters, edit profile).
- Progress explorer (date range + per-day cards; filters).

## M4 — Feed polish
- Pagination for `/api/posts/`.
- RepDeck multi-image gallery; error toasts; a11y polish.

## M5 — Quality & Ops
- Tests (feed/like/comment + basic frontend smoke).
- Secrets to env, DEBUG=False-ready static, basic caching/whitenoise.
