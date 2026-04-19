<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  cards: { type: Array, default: () => [] }
})

const emit = defineEmits(['close'])

const currentIndex = ref(0)
const isFlipped = ref(false)

const totalCards = computed(() => props.cards.length)
const currentCard = computed(() => props.cards[currentIndex.value] || null)

const flipCard = () => {
  if (!currentCard.value) return
  isFlipped.value = !isFlipped.value
}

const goNext = () => {
  if (totalCards.value === 0) return
  currentIndex.value = (currentIndex.value + 1) % totalCards.value
  isFlipped.value = false
}

const goPrev = () => {
  if (totalCards.value === 0) return
  currentIndex.value = (currentIndex.value - 1 + totalCards.value) % totalCards.value
  isFlipped.value = false
}

watch(
  () => props.cards.length,
  () => {
    currentIndex.value = 0
    isFlipped.value = false
  }
)
</script>

<template>
  <section class="rounded-2xl border border-slate-200 bg-white p-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <p class="text-xs uppercase tracking-[0.2em] text-slate-500">Review mode</p>
        <p class="text-sm text-slate-600">Flip to see the answer, then go next or previous.</p>
      </div>
      <div class="flex items-center gap-2">
        <button
          class="rounded-full border border-slate-300 px-3 py-2 text-xs text-slate-700 hover:border-slate-400"
          @click="goPrev"
        >
          Previous
        </button>
        <button
          class="rounded-full border border-slate-300 px-3 py-2 text-xs text-slate-700 hover:border-slate-400"
          @click="goNext"
        >
          Next
        </button>
        <button
          class="rounded-full bg-slate-900 px-3 py-2 text-xs text-white hover:bg-slate-800"
          @click="emit('close')"
        >
          Back to deck
        </button>
      </div>
    </div>

    <div v-if="currentCard" class="mt-6">
      <div class="mb-3 flex items-center justify-between text-xs text-slate-500">
        <span>Card {{ currentIndex + 1 }} of {{ totalCards }}</span>
        <span>Endless loop enabled</span>
      </div>

      <button
        type="button"
        class="flip-card group relative h-64 w-full rounded-2xl border border-slate-200 bg-white p-0 text-left"
        @click="flipCard"
      >
        <div class="flip-inner" :class="{ 'is-flipped': isFlipped }">
          <div class="flip-face flip-front rounded-2xl border border-transparent p-6">
            <div class="flex items-start justify-between gap-3">
              <span class="rounded-full bg-slate-900/10 px-2 py-1 text-xs text-slate-700">
                #{{ currentIndex + 1 }}
              </span>
              <span class="text-[10px] uppercase tracking-[0.2em] text-slate-400">Question</span>
            </div>
            <h3 class="mt-6 text-lg font-semibold text-slate-900">{{ currentCard.question }}</h3>
            <p class="mt-4 text-xs uppercase tracking-[0.2em] text-slate-400">Tap to reveal answer</p>
          </div>
          <div class="flip-face flip-back rounded-2xl border border-transparent bg-slate-900 text-white p-6">
            <div class="flex items-start justify-between gap-3">
              <span class="rounded-full bg-white/15 px-2 py-1 text-xs text-white">Answer</span>
              <span class="text-[10px] uppercase tracking-[0.2em] text-white/70">Tap to flip</span>
            </div>
            <p class="mt-6 text-base text-white/90">{{ currentCard.answer }}</p>
          </div>
        </div>
      </button>
    </div>

    <div v-else class="mt-6 rounded-2xl border border-dashed border-slate-200 px-6 py-8 text-sm text-slate-500">
      No cards in this deck yet.
    </div>
  </section>
</template>

<style scoped>
.flip-card {
  perspective: 1000px;
}

.flip-inner {
  position: relative;
  height: 100%;
  width: 100%;
  transform-style: preserve-3d;
  transition: transform 0.4s ease;
}

.flip-inner.is-flipped {
  transform: rotateY(180deg);
}

.flip-face {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
}

.flip-back {
  transform: rotateY(180deg);
}
</style>
