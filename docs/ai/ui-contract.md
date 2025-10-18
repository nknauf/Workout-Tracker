# UI Contracts (authoritative)

> DO NOT BREAK THESE without updating backend-contracts + templates.

## Shared
- Tailwind v4 utilities only. If custom styles are needed, add Tailwind `@layer` in the app CSS.
- Accessibility: focus states; announce “Liked/Unliked” via `aria-live="polite"`.
- Keyboard: ArrowUp/Down (prev/next card), ArrowLeft/Right (prev/next panel), L (toggle like).

## Nav Header
- Exactly: **Home**, **Profile**, **Social**, **Agent**, **Progress** (Django base template).
- React pages mount inside content blocks.

## Social Feed (React — RepDeck)
**File:** `frontend/src/RepDeck.tsx`  
**Export:** `export default function RepDeck(props)`  
**Mount:** `<div id="repdeck-root"></div>`

```ts
type Media = { url: string; alt?: string };
type Macro = { protein: number; carbs: number; fats: number; calories?: number };
type WorkoutStat = { exercise: string; sets: number; reps: string; volume?: number };

export type PostDTO = {
  id: number | string;
  author: { username: string; avatarUrl?: string };
  createdAt: string;          // ISO
  type: "image" | "video" | "text";
  mediaUrl?: string;          // fallback to first image
  images?: Media[];           // multi-image support
  content?: string;
  meal?: { name: string; macros: Macro } | null;
  workout?: { name: string; stats: WorkoutStat[] } | null;
  liked: boolean;
  likeCount?: number;
  comments: Array<{ user: string; text: string; when: string }>;
}

export type RepDeckProps = {
  posts?: PostDTO[];
  onToggleLike?: (id: PostDTO["id"], liked: boolean) => void;
}
