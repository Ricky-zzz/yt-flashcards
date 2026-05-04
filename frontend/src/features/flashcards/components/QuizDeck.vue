<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  cards: { type: Array, default: () => [] },
  sessionId: { type: [Number, String, null], default: null },
  isGuest: { type: Boolean, default: false }
})
const emit = defineEmits(['close', 'finished', 'attempt'])

const idx = ref(0)
const userAnswer = ref('')
const results = ref([])

const total = computed(() => props.cards.length)
const currentCard = computed(() => props.cards[idx.value] || null)
const correctCount = computed(() => results.value.filter((record) => record.isCorrect).length)
const percent = computed(() => (total.value ? Math.round((correctCount.value / total.value) * 100) : 0))

function normalize(value = '') {
  return String(value || '')
    .toLowerCase()
    .replace(/[^\w\s]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
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
  emit('attempt', record)

  userAnswer.value = ''
  idx.value += 1
  if (idx.value >= total.value) {
    finishQuiz()
  }
}

function finishQuiz() {
  emit('finished', {
    results: results.value,
    score: correctCount.value,
    percent: percent.value
  })
}
</script>

<template>
  <section class="rounded-2xl border border-slate-200 bg-white p-6">
    <div v-if="idx < total">
      <div class="mb-4">
        <div class="text-xs text-slate-500">Test mode - Question {{ idx + 1 }} / {{ total }}</div>
        <h3 class="mt-2 text-lg font-semibold">{{ currentCard?.question }}</h3>
      </div>

      <textarea v-model="userAnswer" rows="4" class="w-full rounded-md border p-2"></textarea>
      <div class="mt-3 flex gap-2">
        <button class="rounded bg-slate-900 px-3 py-1 text-white" @click="submitAnswer">Submit</button>
        <button class="rounded border px-3 py-1" @click="$emit('close')">Cancel</button>
      </div>
    </div>

    <div v-else>
      <h3 class="text-lg font-semibold">Results</h3>
      <p class="text-sm text-slate-600">{{ correctCount }} / {{ total }} correct - {{ percent }}%</p>
      <ul class="mt-3 space-y-2">
        <li v-for="record in results" :key="record.cardId" class="flex gap-3 items-start">
          <div :class="record.isCorrect ? 'text-emerald-600' : 'text-rose-600'">
            {{ record.isCorrect ? 'OK' : 'X' }}
          </div>
          <div>
            <div class="text-sm font-medium">
              Q: {{ props.cards.find((card) => card.id === record.cardId)?.question }}
            </div>
            <div class="text-sm text-slate-700">You: {{ record.userAnswer }}</div>
            <div class="text-sm text-slate-500">Answer: {{ record.correctAnswer }}</div>
          </div>
        </li>
      </ul>
      <div class="mt-4">
        <button class="rounded bg-slate-900 px-3 py-1 text-white" @click="$emit('close')">Back to deck</button>
      </div>
    </div>
  </section>
</template>
