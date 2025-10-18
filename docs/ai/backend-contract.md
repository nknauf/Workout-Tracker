
## `/docs/ai/backend-contract.md`
```md
# Backend Contracts (authoritative)

## Models (Django)

### Social
- UserProfile(user OneToOne, avatar ImageField, bio TextField)
- Follow(follower FK->User, following FK->User) UNIQUE(follower, following), created_at
- Post(author FK->User, content TextField, created_at, visibility CharField{public,private})
- PostImage(post FK->Post, image ImageField, alt_text, order SmallInt; index (post, order))
- PostLike(user FK->User, post FK->Post) UNIQUE(user, post)
- Comment(post FK->Post, user FK->User, content TextField, created_at)

### Fitness
- MainMuscle(name unique)
- MuscleGroup(name unique, main FK->MainMuscle)
- Equipment(name unique)
- BaseExercise(name unique)
- Exercise(base_exercise FK, equipment FK nullable, name, UNIQUE(base_exercise, equipment, name))
- Workout(name)
- WorkoutSession(user FK, date, notes)
- ExerciseSet(session FK, exercise FK, sets SmallInt, reps CharField, weight Decimal, volume Integer)
- Meal(name, notes)
- Macro(meal FK, protein Integer, carbs Integer, fats Integer, calories Integer nullable)
- Recipe(title, steps Text)

### Daily Log (summary or computed)
- DailyLog(user FK, date, total_calories, protein, carbs, fats)
- Connects to workouts, meals, pump images by date.

## APIs

### Social
- `GET /api/posts/?page=<int>` →
  `{ results: PostDTO[], next?: string, prev?: string }`
  - Each PostDTO includes: author, createdAt (ISO), type, mediaUrl (first image), **images[]**, content, optional meal/workout, `liked`, `likeCount`, `comments[]`.

- `POST /social/post/<int:pk>/like/` → `{ liked: boolean, count: number }`
- `POST /social/post/<int:pk>/comment/` (json `{text}`) → `{ ok: true, comment: { user, text, when } }`
- `GET /api/profile/<username>/` → profile + posts (paginated; enforce visibility if viewer != owner)

### Home / Progress / Agent
- `GET /api/daily/today/` → today’s workouts, meals, totals, pump images
- `GET /api/daily/?start=YYYY-MM-DD&end=YYYY-MM-DD` → DailyLog summaries
- `POST /api/chat/add-workout` → creates WorkoutSession + ExerciseSet (returns ids)
- `POST /api/chat/add-meal` → creates Meal + Macro
- `GET /api/user/history/summary` → last N workouts/meals for Agent context

## Permissions
- All endpoints require login; social visibility enforced.
- CSRF on POST (`credentials: "same-origin"` client-side).

## Serialization
- Build explicit JSON; timestamps ISO 8601.
