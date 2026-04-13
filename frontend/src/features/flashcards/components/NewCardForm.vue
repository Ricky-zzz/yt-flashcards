<script setup>
import { computed } from 'vue'

const props = defineProps({
  question: { type: String, default: '' },
  answer: { type: String, default: '' }
})

const emit = defineEmits(['update:question', 'update:answer', 'save', 'close'])

const modelQuestion = computed({
  get: () => props.question,
  set: (val) => emit('update:question', val)
})

const modelAnswer = computed({
  get: () => props.answer,
  set: (val) => emit('update:answer', val)
})
</script>

<template>
  <section class="rounded-2xl border border-slate-200 bg-white p-6">
    <div class="flex flex-col gap-3">
      <div class="flex items-center justify-between">
        <p class="text-sm font-semibold text-slate-900">New flashcard</p>
        <button class="text-xs text-slate-500 hover:text-slate-900" @click="emit('close')">Close</button>
      </div>
      <input
        v-model="modelQuestion"
        type="text"
        placeholder="Question"
        class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 focus:border-slate-400 focus:outline-none"
      />
      <textarea
        v-model="modelAnswer"
        rows="3"
        placeholder="Answer"
        class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 focus:border-slate-400 focus:outline-none"
      ></textarea>
      <button
        class="self-start rounded-full bg-slate-900 px-4 py-2 text-sm text-white hover:bg-slate-800"
        @click="emit('save')"
      >
        Save card
      </button>
    </div>
  </section>
</template>
