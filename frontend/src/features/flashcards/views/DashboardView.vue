<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import Sidebar from '../components/Sidebar.vue'
import GeneratePanel from '../components/GeneratePanel.vue'
import SetHeader from '../components/SetHeader.vue'
import CardGrid from '../components/CardGrid.vue'
import NewCardForm from '../components/NewCardForm.vue'
import EmptyState from '../components/EmptyState.vue'

const API_BASE = 'http://127.0.0.1:8001/api/v1'
const STORAGE_KEY = 'yt_flashcard_sets_v1'

const router = useRouter()

const youtubeUrl = ref('')
const numPairs = ref(3)
const maxChunks = ref(2)
const showAdvanced = ref(false)

const sets = ref([])
const activeSetId = ref(null)

const isLoading = ref(false)
const errorMessage = ref('')

const showNewCard = ref(false)
const newQuestion = ref('')
const newAnswer = ref('')

const activeSet = computed(() => sets.value.find((set) => set.id === activeSetId.value) || null)
const activeMeta = computed(() => activeSet.value?.metadata || {})
const canGenerate = computed(() => youtubeUrl.value.trim().length > 0 && !isLoading.value)

const saveSets = () => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(sets.value))
}

watch(sets, saveSets, { deep: true })

const loadSets = () => {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return
  try {
    const parsed = JSON.parse(raw)
    if (Array.isArray(parsed)) {
      sets.value = parsed
      activeSetId.value = parsed[0]?.id || null
    }
  } catch {
    localStorage.removeItem(STORAGE_KEY)
  }
}

onMounted(loadSets)

const createId = () => {
  if (crypto?.randomUUID) return crypto.randomUUID()
  return `set-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

const handleGenerate = async () => {
  if (!canGenerate.value) return
  errorMessage.value = ''
  isLoading.value = true

  try {
    const payload = {
      youtube_url: youtubeUrl.value.trim(),
      num_pairs: Number(numPairs.value),
      max_chunks: Number(maxChunks.value)
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

    const newSet = {
      id: createId(),
      title: data.data.metadata.video_title || 'Untitled Video',
      createdAt: new Date().toISOString(),
      youtubeUrl: payload.youtube_url,
      flashcards: data.data.flashcards || [],
      metadata: data.data.metadata
    }

    sets.value = [newSet, ...sets.value]
    activeSetId.value = newSet.id
    showNewCard.value = false
  } catch (err) {
    errorMessage.value = err?.message || 'Something went wrong.'
  } finally {
    isLoading.value = false
  }
}

const selectSet = (id) => {
  activeSetId.value = id
  showNewCard.value = false
}

const startNewSet = () => {
  activeSetId.value = null
  showNewCard.value = false
}

const deleteSet = (id) => {
  if (!confirm('Delete this set?')) return
  sets.value = sets.value.filter((set) => set.id !== id)
  if (activeSetId.value === id) {
    activeSetId.value = sets.value[0]?.id || null
  }
}

const renameSet = (id) => {
  const target = sets.value.find((set) => set.id === id)
  if (!target) return
  const nextTitle = prompt('Rename set', target.title)
  if (nextTitle) target.title = nextTitle
}

const addManualCard = () => {
  if (!activeSet.value) return
  if (!newQuestion.value.trim() || !newAnswer.value.trim()) return

  activeSet.value.flashcards.unshift({
    question: newQuestion.value.trim(),
    answer: newAnswer.value.trim(),
    topic: 'custom',
    question_type: 'manual',
    difficulty: 'custom',
    chunk_index: -1
  })

  activeSet.value.metadata.total_cards = activeSet.value.flashcards.length
  newQuestion.value = ''
  newAnswer.value = ''
  showNewCard.value = false
}

const updateCard = (idx, question, answer) => {
  if (!activeSet.value) return
  const card = activeSet.value.flashcards[idx]
  if (!card) return
  card.question = question
  card.answer = answer
}

const deleteCard = (idx) => {
  if (!activeSet.value) return
  activeSet.value.flashcards.splice(idx, 1)
  activeSet.value.metadata.total_cards = activeSet.value.flashcards.length
}

const handleSignOut = () => {
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

          <GeneratePanel
            v-if="!activeSet"
            v-model:youtube-url="youtubeUrl"
            v-model:num-pairs="numPairs"
            v-model:max-chunks="maxChunks"
            :show-advanced="showAdvanced"
            :is-loading="isLoading"
            :can-generate="canGenerate"
            :error-message="errorMessage"
            @toggle-advanced="showAdvanced = !showAdvanced"
            @generate="handleGenerate"
          />

          <SetHeader
            v-if="activeSet"
            :title="activeSet.title"
            :youtube-url="activeSet.youtubeUrl"
            :metadata="activeMeta"
            @add-card="showNewCard = !showNewCard"
          />

          <NewCardForm
            v-if="showNewCard && activeSet"
            v-model:question="newQuestion"
            v-model:answer="newAnswer"
            @close="showNewCard = false"
            @save="addManualCard"
          />

          <CardGrid
            v-if="activeSet"
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
