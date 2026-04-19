<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import Sidebar from '../components/Sidebar.vue'
import GeneratePanel from '../components/GeneratePanel.vue'
import SetHeader from '../components/SetHeader.vue'
import CardGrid from '../components/CardGrid.vue'
import NewCardForm from '../components/NewCardForm.vue'
import EmptyState from '../components/EmptyState.vue'
import ReviewDeck from '../components/ReviewDeck.vue'
import { getStoredUser, clearStoredUser } from '../../auth/services/authService'
import {
  listDecks,
  createDeck,
  updateDeck,
  deleteDeck,
  listCards,
  createCard,
  updateCard as updateCardApi,
  deleteCard as deleteCardApi
} from '../services/deckService'

const API_BASE = 'http://127.0.0.1:8001/api/v1'

const router = useRouter()

const youtubeUrl = ref('')
const transcriptText = ref('')
const inputMode = ref('url')

const user = ref(null)
const sets = ref([])
const activeSetId = ref(null)

const isLoading = ref(false)
const errorMessage = ref('')

const showNewCard = ref(false)
const newQuestion = ref('')
const newAnswer = ref('')
const reviewMode = ref(false)

const activeSet = computed(() => sets.value.find((set) => set.id === activeSetId.value) || null)
const activeMeta = computed(() => activeSet.value?.metadata || {})
const canGenerate = computed(() => {
  if (isLoading.value) return false
  if (inputMode.value === 'transcript') {
    return transcriptText.value.trim().length > 0
  }
  return youtubeUrl.value.trim().length > 0
})

const mapDeck = (deck) => ({
  id: deck.id,
  title: deck.title,
  createdAt: deck.created_at,
  youtubeUrl: deck.source_url,
  cardCount: deck.card_count ?? 0,
  flashcards: [],
  metadata: {
    total_cards: deck.card_count ?? 0,
    chunks_processed: 0,
    processing_time: 0,
    classification_skipped: false
  }
})

const mapCard = (card, meta = {}) => ({
  id: card.id,
  question: card.front,
  answer: card.back,
  topic: card.topic || meta.topic || 'general',
  question_type: card.question_type || meta.question_type || 'definition',
  difficulty: card.difficulty || meta.difficulty || 'medium',
  chunk_index: meta.chunk_index ?? -1
})

const loadDecks = async () => {
  if (!user.value) return
  try {
    const decks = await listDecks(user.value.id)
    sets.value = decks.map(mapDeck)
    activeSetId.value = sets.value[0]?.id || null
    if (activeSetId.value) {
      await loadCardsForDeck(activeSetId.value)
    }
  } catch (err) {
    errorMessage.value = err?.message || 'Failed to load decks.'
  }
}

const loadCardsForDeck = async (deckId) => {
  const target = sets.value.find((set) => set.id === deckId)
  if (!target) return
  if (target.flashcards.length > 0) return

  try {
    const cards = await listCards(deckId)
    target.flashcards = cards.map((card) => mapCard(card))
    target.cardCount = cards.length
    target.metadata.total_cards = cards.length
  } catch (err) {
    errorMessage.value = err?.message || 'Failed to load cards.'
  }
}

onMounted(async () => {
  user.value = getStoredUser()
  if (!user.value) {
    router.push('/login')
    return
  }
  await loadDecks()
})

const handleGenerate = async () => {
  if (!canGenerate.value || !user.value) return
  errorMessage.value = ''
  isLoading.value = true

  try {
    const payload = {
      youtube_url: inputMode.value === 'url' ? youtubeUrl.value.trim() : null,
      transcript_text: inputMode.value === 'transcript' ? transcriptText.value.trim() : null,
      num_pairs: null,
      max_chunks: null
    }

    const response = await fetch(`${API_BASE}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    const data = await response.json()

    if (!response.ok || !data.success) {
      throw new Error(data?.message || 'Generation failed. Try again.')
    }

    const deck = await createDeck({
      title: data.data.metadata.video_title || 'Untitled Video',
      userId: user.value.id,
      sourceUrl: payload.youtube_url
    })

    const flashcards = data.data.flashcards || []
    const createdCards = await Promise.all(
      flashcards.map((card) =>
        createCard(deck.id, {
          front: card.question,
          back: card.answer,
          difficulty: card.difficulty,
          question_type: card.question_type,
          topic: card.topic
        })
      )
    )

    const newSet = mapDeck(deck)
    newSet.metadata = data.data.metadata
    newSet.flashcards = createdCards.map((card, idx) => mapCard(card, flashcards[idx]))
    newSet.cardCount = newSet.flashcards.length
    newSet.metadata.total_cards = newSet.flashcards.length

    sets.value = [newSet, ...sets.value]
    activeSetId.value = newSet.id
    showNewCard.value = false
  } catch (err) {
    const rawMessage = err?.message || ''
    const hintTriggers = ['transcript', 'caption', 'youtube url', 'fetch transcript', 'no transcript']
    const lower = rawMessage.toLowerCase()
    if (hintTriggers.some((hint) => lower.includes(hint))) {
      errorMessage.value = 'Having trouble fetching captions. Paste a transcript instead.'
    } else {
      errorMessage.value = rawMessage || 'Something went wrong.'
    }
  } finally {
    isLoading.value = false
  }
}

const selectSet = async (id) => {
  activeSetId.value = id
  showNewCard.value = false
  reviewMode.value = false
  await loadCardsForDeck(id)
}

const startNewSet = () => {
  activeSetId.value = null
  showNewCard.value = false
  reviewMode.value = false
}

const deleteSet = async (id) => {
  if (!confirm('Delete this set?')) return
  try {
    await deleteDeck(id)
    sets.value = sets.value.filter((set) => set.id !== id)
    if (activeSetId.value === id) {
      activeSetId.value = sets.value[0]?.id || null
    }
  } catch (err) {
    errorMessage.value = err?.message || 'Failed to delete set.'
  }
}

const renameSet = async (id) => {
  const target = sets.value.find((set) => set.id === id)
  if (!target) return
  const nextTitle = prompt('Rename set', target.title)
  if (!nextTitle) return
  try {
    const updated = await updateDeck(id, { title: nextTitle })
    target.title = updated.title
  } catch (err) {
    errorMessage.value = err?.message || 'Failed to rename set.'
  }
}

const addManualCard = async () => {
  if (!activeSet.value) return
  if (!newQuestion.value.trim() || !newAnswer.value.trim()) return

  try {
    const created = await createCard(activeSet.value.id, {
      front: newQuestion.value.trim(),
      back: newAnswer.value.trim(),
      difficulty: 'custom',
      question_type: 'manual',
      topic: 'custom'
    })

    activeSet.value.flashcards.unshift(
      mapCard(created, {
        topic: 'custom',
        question_type: 'manual',
        difficulty: 'custom',
        chunk_index: -1
      })
    )
    activeSet.value.cardCount = activeSet.value.flashcards.length
    activeSet.value.metadata.total_cards = activeSet.value.flashcards.length
    newQuestion.value = ''
    newAnswer.value = ''
    showNewCard.value = false
  } catch (err) {
    errorMessage.value = err?.message || 'Failed to add card.'
  }
}

const toggleNewCard = () => {
  reviewMode.value = false
  showNewCard.value = !showNewCard.value
}

const startReview = () => {
  if (!activeSet.value) return
  showNewCard.value = false
  reviewMode.value = true
}

const stopReview = () => {
  reviewMode.value = false
}

const updateCard = async (idx, question, answer) => {
  if (!activeSet.value) return
  const card = activeSet.value.flashcards[idx]
  if (!card) return
  try {
    const updated = await updateCardApi(card.id, { front: question, back: answer })
    card.question = updated.front
    card.answer = updated.back
  } catch (err) {
    errorMessage.value = err?.message || 'Failed to update card.'
  }
}

const deleteCard = async (idx) => {
  if (!activeSet.value) return
  const card = activeSet.value.flashcards[idx]
  if (!card) return
  try {
    await deleteCardApi(card.id)
    activeSet.value.flashcards.splice(idx, 1)
    activeSet.value.cardCount = activeSet.value.flashcards.length
    activeSet.value.metadata.total_cards = activeSet.value.flashcards.length
  } catch (err) {
    errorMessage.value = err?.message || 'Failed to delete card.'
  }
}

const handleSignOut = () => {
  clearStoredUser()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen bg-[#f8fafc] text-slate-900">
    <div class="flex min-h-screen flex-col md:flex-row">
      <Sidebar
        :sets="sets"
        :active-set-id="activeSetId"
        @select="selectSet"
        @create="startNewSet"
        @rename="renameSet"
        @delete="deleteSet"
      />

      <main class="relative flex-1">
        <div class="pointer-events-none absolute right-0 top-0 h-72 w-72 rounded-full bg-[radial-gradient(circle,_rgba(15,23,42,0.06),_transparent_65%)] blur-3xl"></div>
        <div class="pointer-events-none absolute left-10 top-20 h-80 w-80 rounded-full bg-[radial-gradient(circle,_rgba(148,163,184,0.12),_transparent_70%)] blur-3xl"></div>

        <div class="mx-auto flex max-w-5xl flex-col gap-8 px-6 py-10">
          <header class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div class="animate-fade">
              <p class="text-xs uppercase tracking-[0.35em] text-slate-500">Studio</p>
              <h1 class="text-3xl font-semibold text-slate-900 md:text-4xl">
                Make study cards from any video in minutes.
              </h1>
              <p class="mt-2 text-sm text-slate-600">
                Paste a YouTube link, generate clean Q&A cards, and manage them like a workspace.
              </p>
            </div>
            <button
              type="button"
              class="rounded-full border border-slate-300 px-4 py-2 text-xs uppercase tracking-[0.2em] text-slate-700 transition hover:border-slate-400"
              @click="handleSignOut"
            >
              Sign out
            </button>
          </header>

          <p v-if="errorMessage && activeSet" class="text-sm text-rose-600">
            {{ errorMessage }}
          </p>

          <GeneratePanel
            v-if="!activeSet"
            v-model:input-mode="inputMode"
            v-model:youtube-url="youtubeUrl"
            v-model:transcript-text="transcriptText"
            :is-loading="isLoading"
            :can-generate="canGenerate"
            :error-message="errorMessage"
            @generate="handleGenerate"
          />

          <SetHeader
            v-if="activeSet"
            :title="activeSet.title"
            :youtube-url="activeSet.youtubeUrl"
            :metadata="activeMeta"
            @add-card="toggleNewCard"
            @review="startReview"
          />

          <NewCardForm
            v-if="showNewCard && activeSet && !reviewMode"
            v-model:question="newQuestion"
            v-model:answer="newAnswer"
            @close="showNewCard = false"
            @save="addManualCard"
          />

          <ReviewDeck
            v-if="activeSet && reviewMode"
            :cards="activeSet.flashcards"
            @close="stopReview"
          />

          <CardGrid
            v-else-if="activeSet"
            :cards="activeSet.flashcards"
            @update-card="updateCard"
            @delete-card="deleteCard"
          />

          <EmptyState v-else />
        </div>
      </main>
    </div>
  </div>
</template>
