<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { listSessions, listAttempts } from '../services/reviewService'

const props = defineProps({
  deckId: { type: [Number, String], default: null },
  userId: { type: [Number, String], default: null },
  cards: { type: Array, default: () => [] },
  refreshKey: { type: [Number, String], default: 0 }
})

const sessions = ref([])
const attemptsBySession = ref({})
const attemptErrors = ref({})
const expandedSessionIds = ref([])
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

const toggleAttempts = (sessionId) => {
  const idx = expandedSessionIds.value.indexOf(sessionId)
  if (idx >= 0) {
    expandedSessionIds.value.splice(idx, 1)
    return
  }
  expandedSessionIds.value.push(sessionId)
}

const refresh = async () => {
  if (props.userId == null || props.deckId == null) {
    sessions.value = []
    attemptsBySession.value = {}
    attemptErrors.value = {}
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    const loadedSessions = await listSessions(props.userId, props.deckId)
    sessions.value = loadedSessions

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
  <section class="rounded-2xl border border-slate-200 bg-white p-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <p class="text-xs uppercase tracking-[0.2em] text-slate-500">Quiz history</p>
        <p class="text-sm text-slate-600">Track past quiz sessions and compare scores.</p>
      </div>
      <button
        class="rounded-full border border-slate-300 px-3 py-2 text-xs text-slate-700 hover:border-slate-400"
        @click="refresh"
      >
        Refresh
      </button>
    </div>

    <div v-if="isLoading" class="mt-4 text-sm text-slate-500">Loading history...</div>
    <div v-else-if="errorMessage" class="mt-4 text-sm text-rose-600">{{ errorMessage }}</div>
    <div v-else-if="sessions.length === 0" class="mt-4 text-sm text-slate-500">
      No quiz sessions saved yet.
    </div>

    <ul v-else class="mt-4 space-y-3">
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
            <button class="text-xs text-slate-600 underline" @click="toggleAttempts(session.id)">
              {{ expandedSessionIds.includes(session.id) ? 'Hide attempts' : 'Show attempts' }}
            </button>
          </div>
        </div>

        <div v-if="expandedSessionIds.includes(session.id)" class="mt-3">
          <div v-if="attemptErrors[session.id]" class="text-xs text-rose-600">
            Attempts could not be loaded for this session.
          </div>
          <div v-else-if="!attemptsBySession[session.id] || attemptsBySession[session.id].length === 0" class="text-xs text-slate-500">
            No attempts recorded.
          </div>
          <ul v-else class="space-y-2">
            <li
              v-for="attempt in attemptsBySession[session.id]"
              :key="attempt.id"
              class="flex gap-3 rounded-lg border border-slate-100 bg-slate-50 px-3 py-2"
            >
              <div class="text-xs font-semibold" :class="attempt.is_correct ? 'text-emerald-600' : 'text-rose-600'">
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
      </li>
    </ul>
  </section>
</template>
