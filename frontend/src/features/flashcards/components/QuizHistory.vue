<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { listSessions, listAttempts } from '../services/reviewService'

const props = defineProps({
  deckId: { type: [Number, String], default: null },
  userId: { type: [Number, String], default: null },
  cards: { type: Array, default: () => [] },
  refreshKey: { type: [Number, String], default: 0 },
  collapsed: { type: Boolean, default: false }
})

const emit = defineEmits(['toggle-collapse'])

const sessions = ref([])
const attemptsBySession = ref({})
const attemptErrors = ref({})
const activeSessionId = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')

const cardById = computed(() => {
  const map = new Map()
  for (const card of props.cards) {
    map.set(card.id, card)
  }
  return map
})

const scoreDeltas = computed(() => {
  const result = {}
  let prevScore = null
  const ordered = [...sessions.value].slice().reverse()
  for (const session of ordered) {
    if (session.score == null) continue
    if (prevScore != null) {
      result[session.id] = session.score - prevScore
    }
    prevScore = session.score
  }
  return result
})

const activeSession = computed(
  () => sessions.value.find((session) => session.id === activeSessionId.value) || null
)

const activeAttempts = computed(
  () => attemptsBySession.value[activeSessionId.value] || []
)

const activeAttemptError = computed(() =>
  activeSessionId.value ? attemptErrors.value[activeSessionId.value] : false
)

const formatDateTime = (value) => {
  if (!value) return 'N/A'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  return new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short'
  }).format(date)
}

const getAttemptSummary = (session) => {
  const attempts = attemptsBySession.value[session.id]
  if (attempts && attempts.length > 0) {
    const correct = attempts.filter((attempt) => attempt.is_correct).length
    const percent = Math.round((correct / attempts.length) * 100)
    return `${correct}/${attempts.length} (${percent}%)`
  }
  if (session.score != null) return `${session.score} correct`
  return 'In progress'
}

const getDeltaLabel = (sessionId) => {
  const delta = scoreDeltas.value[sessionId]
  if (delta == null) return null
  if (delta > 0) return `+${delta}`
  return `${delta}`
}

const getQuestionText = (cardId) => {
  const card = cardById.value.get(cardId)
  if (card?.question) return card.question
  return `Card #${cardId}`
}

const openAttempts = (sessionId) => {
  activeSessionId.value = sessionId
}

const closeAttempts = () => {
  activeSessionId.value = null
}

const refresh = async () => {
  if (props.userId == null || props.deckId == null) {
    sessions.value = []
    attemptsBySession.value = {}
    attemptErrors.value = {}
    activeSessionId.value = null
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    const loadedSessions = await listSessions(props.userId, props.deckId)
    sessions.value = loadedSessions
    activeSessionId.value = null

    const results = await Promise.all(
      loadedSessions.map(async (session) => {
        try {
          const attempts = await listAttempts(session.id)
          return { id: session.id, attempts, error: false }
        } catch (err) {
          return { id: session.id, attempts: [], error: true }
        }
      })
    )

    const attemptsMap = {}
    const errorMap = {}
    for (const result of results) {
      attemptsMap[result.id] = result.attempts
      if (result.error) {
        errorMap[result.id] = true
      }
    }

    attemptsBySession.value = attemptsMap
    attemptErrors.value = errorMap
  } catch (err) {
    errorMessage.value = err?.message || 'Failed to load quiz history.'
  } finally {
    isLoading.value = false
  }
}

onMounted(refresh)

watch(
  () => [props.deckId, props.userId, props.refreshKey],
  () => {
    refresh()
  }
)
</script>

<template>
  <section
    class="rounded-2xl border border-slate-200 bg-white"
    :class="props.collapsed ? 'p-3' : 'p-6'"
  >
    <div class="flex flex-wrap items-start justify-between gap-3">
      <div>
        <p class="text-xs uppercase tracking-[0.2em] text-slate-500">Quiz history</p>
        <p v-if="!props.collapsed" class="text-sm text-slate-600">
          Track past quiz sessions and compare scores.
        </p>
      </div>
      <div class="flex items-center gap-2">
        <button
          v-if="!props.collapsed"
          class="rounded-full border border-slate-300 px-3 py-2 text-xs text-slate-700 hover:border-slate-400"
          @click="refresh"
        >
          Refresh
        </button>
        <button
          class="flex h-9 w-9 items-center justify-center rounded-full border border-slate-300 text-slate-700 hover:border-slate-400"
          :aria-expanded="!props.collapsed"
          :aria-label="props.collapsed ? 'Expand history' : 'Collapse history'"
          @click="emit('toggle-collapse')"
        >
          <span class="text-lg leading-none">{{ props.collapsed ? '‹' : '›' }}</span>
        </button>
      </div>
    </div>

    <div v-if="!props.collapsed">
      <div v-if="isLoading" class="mt-4 text-sm text-slate-500">Loading history...</div>
      <div v-else-if="errorMessage" class="mt-4 text-sm text-rose-600">{{ errorMessage }}</div>
      <div v-else-if="sessions.length === 0" class="mt-4 text-sm text-slate-500">
        No quiz sessions saved yet.
      </div>

      <ul v-else class="mt-4 max-h-[50vh] space-y-3 overflow-y-auto pr-1">
        <li
          v-for="session in sessions"
          :key="session.id"
          class="rounded-xl border border-slate-200 px-4 py-3"
        >
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p class="text-sm font-semibold text-slate-900">Session #{{ session.id }}</p>
              <p class="text-xs text-slate-500">Started {{ formatDateTime(session.started_at) }}</p>
              <p v-if="session.finished_at" class="text-xs text-slate-500">
                Finished {{ formatDateTime(session.finished_at) }}
              </p>
            </div>
            <div class="flex flex-wrap items-center gap-3">
              <span class="text-sm font-semibold text-slate-900">{{ getAttemptSummary(session) }}</span>
              <span
                v-if="getDeltaLabel(session.id)"
                class="rounded-full border border-slate-200 px-2 py-1 text-xs text-slate-600"
              >
                Delta {{ getDeltaLabel(session.id) }}
              </span>
              <button class="text-xs text-slate-600 underline" @click="openAttempts(session.id)">
                Show attempts
              </button>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </section>

  <div
    v-if="activeSessionId !== null"
    class="fixed inset-0 z-50 flex items-start justify-center bg-slate-900/40 p-4"
    role="dialog"
    aria-modal="true"
    aria-label="Quiz attempts"
    @click.self="closeAttempts"
  >
    <div class="w-full max-w-2xl rounded-2xl bg-white p-6 shadow-xl">
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p class="text-xs uppercase tracking-[0.2em] text-slate-500">Attempts</p>
          <p class="text-lg font-semibold text-slate-900">
            Session #{{ activeSession?.id || activeSessionId }}
          </p>
          <p v-if="activeSession" class="text-xs text-slate-500">
            Started {{ formatDateTime(activeSession.started_at) }}
          </p>
        </div>
        <button
          class="rounded-full border border-slate-300 px-3 py-2 text-xs text-slate-700 hover:border-slate-400"
          @click="closeAttempts"
        >
          Close
        </button>
      </div>

      <div class="mt-4 max-h-[60vh] overflow-y-auto pr-1">
        <div v-if="activeAttemptError" class="text-sm text-rose-600">
          Attempts could not be loaded for this session.
        </div>
        <div v-else-if="activeAttempts.length === 0" class="text-sm text-slate-500">
          No attempts recorded.
        </div>
        <ul v-else class="space-y-2">
          <li
            v-for="attempt in activeAttempts"
            :key="attempt.id"
            class="flex gap-3 rounded-lg border border-slate-100 bg-slate-50 px-3 py-2"
          >
            <div
              class="text-xs font-semibold"
              :class="attempt.is_correct ? 'text-emerald-600' : 'text-rose-600'"
            >
              {{ attempt.is_correct ? 'OK' : 'X' }}
            </div>
            <div>
              <p class="text-xs text-slate-500">{{ formatDateTime(attempt.answered_at) }}</p>
              <p class="text-sm text-slate-900">Q: {{ getQuestionText(attempt.card_id) }}</p>
              <p class="text-xs text-slate-600">You: {{ attempt.user_answer || 'No answer' }}</p>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
