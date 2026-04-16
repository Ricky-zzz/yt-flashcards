# Dev Plan

## Goals
- Guest mode: generate flashcards without login; data disappears on refresh.
- Auth mode: create decks from URL, view decks and cards, CRUD cards.
- Review flow: shuffle and answer cards, show score at end.
- Progress tracking: store attempts to show improvement.
- Generation quality: avoid multi-part questions; tune output by video length.
- Classifier: train a simple model for question type/topic; show dataset + model file in presentation.

## Step-by-step
1. **Product decisions**
   - Guest mode uses local storage only (no DB writes).
   - Review scoring is correct/incorrect.
   - Review attempts persist in DB for progress history.
   - Answer checking: start with simple normalization + exact match; add fuzzy match later if needed.

2. **Data model (DB)**
   - Create tables:
     - `decks`: id, user_id (nullable for guest), title, source_url, created_at, updated_at
     - `cards`: id, deck_id, front, back, created_at, updated_at
     - `review_sessions`: id, deck_id, user_id (nullable), started_at, finished_at, score
     - `review_attempts`: id, session_id, card_id, user_answer, is_correct, answered_at
   - Add indexes for deck_id and user_id.

3. **Backend API (FastAPI)**
   - Deck endpoints: create from URL, list user decks, get deck details.
   - Card endpoints: list cards, add, edit, delete.
   - Review endpoints: start session (shuffle), submit answer, finish session.
   - Guest mode: local storage only (no DB writes).

4. **Frontend UX (Vue)**
   - Guest toggle on login/register screen or a "Continue as guest" button.
   - Deck list view with create form (URL paste).
   - Deck detail view with cards list + CRUD actions.
   - Review view: shuffled cards, one-by-one answering, final score screen.
   - Local storage for guest decks/cards + guest review sessions.

5. **Generation pipeline improvements**
   - Add max-length and single-question constraints in prompt.
   - Split long questions with heuristics or re-prompt.
   - Tie number of cards to video length (e.g., minutes * rate).
   - Add answer normalization rules for review checks (trim, lower, collapse whitespace).

6. **Classifier training**
   - Prepare dataset CSV: question, answer, difficulty, question_type, topic.
   - Train a simple baseline (e.g., TF-IDF + Logistic Regression).
   - Save model file (e.g., .pkl) and show metrics.
   - Add a small demo script to load model and classify a sample.

7. **Presentation artifacts**
   - Dataset file (CSV).
   - Model file (.pkl).
   - Short doc explaining training and evaluation.

8. **Polish + demo readiness**
   - Error handling for URL parsing/generation.
   - Loading states, empty states.
   - Seed demo data for guest mode.

## Suggested order of implementation
1. Guest mode + local storage.
2. Deck list + deck detail views.
3. Card CRUD.
4. Review flow (shuffle, answer, score).
5. DB tables + API wiring for logged-in mode.
6. Generation pipeline improvements.
7. Classifier training + artifacts.

## Open questions
- Do we want fuzzy matching (e.g., token overlap) if exact match feels too strict?
