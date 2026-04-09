<script setup>
import { computed } from 'vue'

const props = defineProps({
  youtubeUrl: { type: String, default: '' },
  numPairs: { type: Number, default: 3 },
  maxChunks: { type: Number, default: 2 },
  showAdvanced: { type: Boolean, default: false },
  isLoading: { type: Boolean, default: false },
  canGenerate: { type: Boolean, default: false },
  errorMessage: { type: String, default: '' }
})

const emit = defineEmits([
  'update:youtubeUrl',
  'update:numPairs',
  'update:maxChunks',
  'toggle-advanced',
  'generate'
])

const modelUrl = computed({
  get: () => props.youtubeUrl,
  set: (val) => emit('update:youtubeUrl', val)
})

const modelPairs = computed({
  get: () => props.numPairs,
  set: (val) => emit('update:numPairs', val)
})

const modelChunks = computed({
  get: () => props.maxChunks,
  set: (val) => emit('update:maxChunks', val)
})
</script>

<template>
  <section class="rounded-2xl border border-slate-800 bg-[#121722] p-6 shadow-[0_30px_80px_rgba(0,0,0,0.35)]">
    <div class="flex flex-col gap-4">
      <div>
        <label class="text-xs uppercase tracking-[0.2em] text-slate-500">YouTube URL</label>
        <input
          v-model="modelUrl"
          type="url"
          placeholder="https://www.youtube.com/watch?v=..."
          class="mt-2 w-full rounded-xl border border-slate-800 bg-[#0b0e13] px-4 py-3 text-sm text-slate-100 focus:border-emerald-300 focus:outline-none"
        />
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <button
          class="rounded-full bg-gradient-to-r from-emerald-400 to-amber-300 px-5 py-2 text-sm font-semibold text-[#0b0e13] transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
          :disabled="!props.canGenerate"
          @click="emit('generate')"
        >
          {{ props.isLoading ? 'Generating...' : 'Generate flashcards' }}
        </button>
        <button
          class="rounded-full border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:border-slate-500"
          @click="emit('toggle-advanced')"
        >
          {{ props.showAdvanced ? 'Hide' : 'Show' }} advanced
        </button>
        <span v-if="props.isLoading" class="text-xs text-slate-400">This may take ~20s.</span>
      </div>

      <div v-if="props.showAdvanced" class="grid gap-4 md:grid-cols-2">
        <div>
          <label class="text-xs uppercase tracking-[0.2em] text-slate-500">Pairs per chunk</label>
          <input
            v-model.number="modelPairs"
            type="number"
            min="1"
            max="10"
            class="mt-2 w-full rounded-xl border border-slate-800 bg-[#0b0e13] px-4 py-3 text-sm text-slate-100 focus:border-emerald-300 focus:outline-none"
          />
        </div>
        <div>
          <label class="text-xs uppercase tracking-[0.2em] text-slate-500">Max chunks</label>
          <input
            v-model.number="modelChunks"
            type="number"
            min="1"
            max="10"
            class="mt-2 w-full rounded-xl border border-slate-800 bg-[#0b0e13] px-4 py-3 text-sm text-slate-100 focus:border-emerald-300 focus:outline-none"
          />
        </div>
      </div>

      <p v-if="props.errorMessage" class="text-sm text-rose-300">{{ props.errorMessage }}</p>
    </div>
  </section>
</template>
