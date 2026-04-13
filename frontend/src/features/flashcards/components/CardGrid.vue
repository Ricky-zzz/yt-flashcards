<script setup>
import { ref } from 'vue'

const props = defineProps({
  cards: { type: Array, default: () => [] }
})

const emit = defineEmits(['update-card', 'delete-card'])

const editingIndex = ref(null)
const editQuestion = ref('')
const editAnswer = ref('')

const startEdit = (idx, card) => {
  editingIndex.value = idx
  editQuestion.value = card.question
  editAnswer.value = card.answer
}

const saveEdit = (idx) => {
  emit('update-card', idx, editQuestion.value.trim(), editAnswer.value.trim())
  editingIndex.value = null
}

const cancelEdit = () => {
  editingIndex.value = null
}
</script>

<template>
  <section class="animate-rise">
    <div class="mt-6 grid gap-4 md:grid-cols-2">
      <article
        v-for="(card, idx) in props.cards"
        :key="idx"
        class="group relative rounded-2xl border border-slate-200 bg-white p-5 transition hover:border-slate-400"
        :style="{ animationDelay: `${idx * 60}ms` }"
      >
        <div class="flex items-start justify-between gap-3">
          <span class="rounded-full bg-slate-900/10 px-2 py-1 text-xs text-slate-700">#{{ idx + 1 }}</span>
          <div class="flex gap-2 text-xs text-slate-500 opacity-0 transition group-hover:opacity-100">
            <button class="hover:text-slate-900" @click="startEdit(idx, card)">Edit</button>
            <button class="hover:text-rose-600" @click="emit('delete-card', idx)">Delete</button>
          </div>
        </div>

        <div v-if="editingIndex === idx" class="mt-3 flex flex-col gap-3">
          <input
            v-model="editQuestion"
            type="text"
            class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 focus:border-slate-400 focus:outline-none"
          />
          <textarea
            v-model="editAnswer"
            rows="3"
            class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 focus:border-slate-400 focus:outline-none"
          ></textarea>
          <div class="flex gap-2">
            <button class="rounded-full bg-slate-900 px-3 py-1 text-xs text-white" @click="saveEdit(idx)">
              Save
            </button>
            <button class="rounded-full border border-slate-300 px-3 py-1 text-xs text-slate-600" @click="cancelEdit">
              Cancel
            </button>
          </div>
        </div>
        <div v-else class="mt-3 space-y-3">
          <h3 class="text-base font-semibold text-slate-900">{{ card.question }}</h3>
          <p class="text-sm text-slate-600">{{ card.answer }}</p>
          <div class="flex flex-wrap gap-2 text-xs text-slate-500">
            <span class="rounded-full border border-slate-200 px-2 py-1">{{ card.topic }}</span>
            <span class="rounded-full border border-slate-200 px-2 py-1">{{ card.question_type }}</span>
            <span class="rounded-full border border-slate-200 px-2 py-1">{{ card.difficulty }}</span>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>
