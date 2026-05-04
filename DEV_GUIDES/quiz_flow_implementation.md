# Implementing Test (Quiz) Mode — Step by step

This guide walks you through implementing a full Test (quiz) mode: UI components in Vue, a small frontend service to call backend review endpoints, and backend saving using the existing review session/attempt endpoints. Follow the steps in order: UI first (learn Vue), service next (learn API integration), then backend saving (persist results).

TL;DR
1. Add `Test` button in the deck header to open Test mode.
2. Implement `QuizDeck.vue` (frontend-only) — local quiz state, grading, results summary.
3. Create `reviewService.js` to call backend endpoints.
4. Wire Dashboard to start a session (backend for logged-in, in-memory for guest), submit attempts as answers are given, and finish session to save the score.
5. Add a `QuizHistory` component to list past saved sessions for logged-in users.

Notes before you start
- Backend endpoints already exist in `app/routes/reviews.py` and `app/schemas/review.py`.
- Guest mode must remain ephemeral: do NOT call backend session/attempt endpoints for guest users.
- We'll use a simple normalized exact-match grader (lowercase, strip punctuation/extra whitespace). You can extend it later.

----

Step 1 — UI: add Test button to deck header
Files to edit:
- `frontend/src/features/flashcards/components/SetHeader.vue`

What to do:
- Add a new `Test` button next to `Review`.
- Emit a `test` event when clicked (similar to existing `review` and `add-card` emits).

Why:
- Keeps the UI explicit: user chooses Review (passive) or Test (active).

Small change example (inside template actions):

```html
<button class="rounded-full border ..." @click="$emit('test')">Test</button>
```

Step 2 — UI: create `QuizDeck.vue` (frontend-only first)
Files to add:
- `frontend/src/features/flashcards/components/QuizDeck.vue`

Responsibilities:
- Accept props: `cards`, `sessionId`, `isGuest`.
- Track: `currentIndex`, `userAnswer`, `results` (per-card records), `isFinished`.
- Provide: `submitAnswer()` to grade, advance index, and push result into `results`.
- Emit `finished` event with `{ results, score, percent }` when done.

Why:
- Keeping this component self-contained lets you learn Vue component props/state/emits without touching backend yet.

Starter implementation (copy this file exactly into `QuizDeck.vue`):

```vue
<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  cards: { type: Array, default: () => [] },
  sessionId: { type: [Number, String, null], default: null },
  isGuest: { type: Boolean, default: false }
})
const emit = defineEmits(['close','finished','attempt'])

const idx = ref(0)
const userAnswer = ref('')
const results = ref([])

const total = computed(() => props.cards.length)
const currentCard = computed(() => props.cards[idx.value] || null)

function normalize(s = '') {
  return String(s || '').toLowerCase().replace(/[^\w\s]/g, '').replace(/\s+/g, ' ').trim()
}

function gradeAnswer(user, correct) {
  return normalize(user) === normalize(correct)
}

async function submitAnswer() {
  if (!currentCard.value) return
  const isCorrect = gradeAnswer(userAnswer.value, currentCard.value.answer)
  const record = {
    cardId: currentCard.value.id,
    userAnswer: userAnswer.value,
    isCorrect,
    correctAnswer: currentCard.value.answer
  }
  results.value.push(record)
  // emit attempt so parent can save (parent decides whether to call backend or not)
  emit('attempt', record)

  userAnswer.value = ''
  idx.value++
  if (idx.value >= total.value) {
    finishQuiz()
  }
}

function finishQuiz() {
  const correct = results.value.filter(r => r.isCorrect).length
  const score = correct
  const percent = total.value ? Math.round((correct / total.value) * 100) : 0
  emit('finished', { results: results.value, score, percent })
}
</script>

<template>
  <section class="rounded-2xl border p-6 bg-white">
    <div v-if="idx < total">
      <div class="mb-4">
        <div class="text-xs text-slate-500">Test mode — Question {{ idx + 1 }} / {{ total }}</div>
        <h3 class="text-lg font-semibold mt-2">{{ currentCard?.question }}</h3>
      </div>

      <textarea v-model="userAnswer" rows="4" class="w-full rounded-md border p-2"></textarea>
      <div class="mt-3 flex gap-2">
        <button class="rounded bg-slate-900 text-white px-3 py-1" @click="submitAnswer">Submit</button>
        <button class="rounded border px-3 py-1" @click="$emit('close')">Cancel</button>
      </div>
    </div>

    <div v-else>
      <h3 class="text-lg font-semibold">Results</h3>
      <p class="text-sm text-slate-600">{{ results.filter(r=>r.isCorrect).length }} / {{ total }} correct — {{ Math.round((results.filter(r=>r.isCorrect).length/total)*100) }}%</p>
      <ul class="mt-3 space-y-2">
        <li v-for="r in results" :key="r.cardId" class="flex gap-3 items-start">
          <div :class="r.isCorrect ? 'text-green-600' : 'text-rose-600'">{{ r.isCorrect ? '✓' : '✗' }}</div>
          <div>
            <div class="text-sm font-medium">Q: {{ props.cards.find(c=>c.id===r.cardId)?.question }}</div>
            <div class="text-sm text-slate-700">You: {{ r.userAnswer }}</div>
            <div class="text-sm text-slate-500">Answer: {{ r.correctAnswer }}</div>
          </div>
        </li>
      </ul>
      <div class="mt-4">
        <button class="rounded bg-slate-900 text-white px-3 py-1" @click="$emit('close')">Back to deck</button>
      </div>
    </div>
  </section>
</template>
```

Implementation tips
- Test this with sample `cards` data inside the Dashboard (pass `:cards="activeSet.flashcards"` and `:isGuest="isGuest"`).
- For now do not call backend; simply handle `attempt` and `finished` events in parent and log to console.

Step 3 — Frontend service: `reviewService.js`
Files to add:
- `frontend/src/features/flashcards/services/reviewService.js`

What to implement (simple helpers):
- `startSession(deckId, userId)`
- `submitAttempt(sessionId, cardId, userAnswer, isCorrect)`
- `finishSession(sessionId, score)`
- `listSessions(userId, deckId)`

Example (copy into `reviewService.js`):

```js
const API_BASE = 'http://127.0.0.1:8001/api/v1'
const parseResponse = async (res) => {
  const data = await res.json()
  if (!res.ok || !data.success) throw new Error(data?.message || 'API error')
  return data
}

export const startSession = async (deckId, userId) => {
  const res = await fetch(`${API_BASE}/reviews/sessions`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ deck_id: deckId, user_id: userId })
  })
  return (await parseResponse(res)).data
}

export const submitAttempt = async (sessionId, cardId, userAnswer, isCorrect) => {
  const res = await fetch(`${API_BASE}/reviews/attempts`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, card_id: cardId, user_answer: userAnswer, is_correct: isCorrect })
  })
  return (await parseResponse(res)).data
}

export const finishSession = async (sessionId, score) => {
  const res = await fetch(`${API_BASE}/reviews/sessions/${sessionId}/finish?score=${score}`, { method: 'POST' })
  return (await parseResponse(res)).data
}

export const listSessions = async (userId, deckId) => {
  const url = new URL(`${API_BASE}/reviews/sessions`)
  if (userId != null) url.searchParams.set('user_id', String(userId))
  if (deckId != null) url.searchParams.set('deck_id', String(deckId))
  const res = await fetch(url.toString())
  return (await parseResponse(res)).data
}
```

Why:
- Keeping API calls in a small module makes components focused and testable.

Step 4 — Dashboard wiring: start session and handle attempts
Files to edit:
- `frontend/src/features/flashcards/views/DashboardView.vue`

What to do:
1. Add a `testMode` boolean state and `activeSessionId` state.
2. When user clicks Test (handle `test` emitted from `SetHeader`):
   - If logged-in: call `startSession(deckId, user.value.id)` and store the returned session id.
   - If guest: set `activeSessionId` to a generated string (e.g., `guest-${Date.now()}`) and mark `isGuest=true`.
3. Render `<QuizDeck>` when `testMode` is true and pass `:session-id="activeSessionId"` and `:is-guest="isGuest"`.
4. Listen for `attempt` events from `QuizDeck` and if not guest, call `submitAttempt(activeSessionId, cardId, userAnswer, isCorrect)`.
5. Listen for `finished` event: if logged-in call `finishSession(activeSessionId, score)`, then show saved confirmation.

Why:
- This pattern separates UI from side effects. Managing session ID and isGuest in parent makes it easy to switch back and forth.

Step 5 — Backend saving (what's already available and how to call it)
Files referenced:
- `app/routes/reviews.py` — contains endpoints:
  - `POST /api/v1/reviews/sessions` — start session
  - `POST /api/v1/reviews/attempts` — submit attempt
  - `POST /api/v1/reviews/sessions/{session_id}/finish?score=<score>` — finish

How the flow should call them:
- At quiz start (logged-in): POST session -> returns `data.id` (session id).
- For each answer: POST attempt with `{ session_id, card_id, user_answer, is_correct }`.
- At finish: POST finish session with `score` as query param (the endpoint writes `finished_at` and `score`).

Example curl (for testing):

```bash
curl -X POST http://127.0.0.1:8001/api/v1/reviews/sessions \
  -H "Content-Type: application/json" \
  -d '{"deck_id": 1, "user_id": 2}'

curl -X POST http://127.0.0.1:8001/api/v1/reviews/attempts \
  -H "Content-Type: application/json" \
  -d '{"session_id": 1, "card_id": 4, "user_answer": "entropy", "is_correct": true}'

curl -X POST "http://127.0.0.1:8001/api/v1/reviews/sessions/1/finish?score=8"
```

Step 6 — Results history and UI
Files to add (optional but recommended):
- `frontend/src/features/flashcards/components/QuizHistory.vue`

What it does:
- Calls `listSessions(userId, deckId)` and lists session rows with timestamp and score.
- Optionally links to attempts via `GET /api/v1/reviews/sessions/{id}/attempts`.

Why:
- Gives users persistence and tracks learning over time.

Step 7 — Testing checklist
- Frontend-only test:
  - Create a temporary hard-coded `cards` array, open `QuizDeck.vue`, answer questions, confirm results summary shows correct/wrong.
- Logged-in flow:
  - Start app, log in, open a deck, click Test.
  - Confirm `startSession` is called and returns an id.
  - Answer one question and inspect database `review_attempts` table (or call the attempts endpoint) to see per-attempt rows.
  - Finish quiz and inspect `review_sessions` table for `score` and `finished_at`.
- Guest flow:
  - Try as Guest, open Test, run quiz. Confirm UI works and no backend calls are made (open network inspector or server logs).
  - Reload page and confirm quiz history is gone.

Step 8 — Incremental learning path (recommended)
A. Implement `QuizDeck.vue` and wire it in Dashboard as a front-end-only modal. Test locally until UI is solid.
B. Add `reviewService.js`. Start submitting attempts only if `!isGuest`.
C. Add `startSession` and `finishSession` calls. Test full persistence while logged-in.
D. Implement `QuizHistory.vue` and style results.

Extras & improvements (later)
- Replace exact-match grade with fuzzy similarity (Levenshtein or cosine over embeddings) if needed.
- Let the user choose per-quiz settings: show immediate feedback vs end-only; time limit per question; shuffle cards.
- Track time per question in `review_attempts` (would need schema changes).

----

If you want, I can now:
- Generate the exact `QuizDeck.vue` file in your repo and a `reviewService.js` file so you can implement Step A quickly, or
- Provide a very short course-style checklist you can follow to implement one file per day and practice Vue concepts.

Tell me which you prefer next and I will create those files for you.