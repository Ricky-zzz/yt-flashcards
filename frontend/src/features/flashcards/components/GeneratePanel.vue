<script setup>
import { computed } from 'vue'

const props = defineProps({
  inputMode: { type: String, default: 'url' },
  youtubeUrl: { type: String, default: '' },
  transcriptText: { type: String, default: '' },
  numPairs: { type: Number, default: 3 },
  maxChunks: { type: Number, default: 2 },
  showAdvanced: { type: Boolean, default: false },
  isLoading: { type: Boolean, default: false },
  canGenerate: { type: Boolean, default: false },
  errorMessage: { type: String, default: '' }
})

const emit = defineEmits([
  'update:inputMode',
  'update:youtubeUrl',
  'update:transcriptText',
  'update:numPairs',
  'update:maxChunks',
  'toggle-advanced',
  'generate'
])

const modelMode = computed({
  get: () => props.inputMode,
  set: (val) => emit('update:inputMode', val)
})

const modelUrl = computed({
  get: () => props.youtubeUrl,
  set: (val) => emit('update:youtubeUrl', val)
})

const modelTranscript = computed({
  get: () => props.transcriptText,
  set: (val) => emit('update:transcriptText', val)
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
  <section class="rounded-2xl border border-slate-200 bg-white p-6 shadow-[0_20px_60px_rgba(15,23,42,0.08)]">
    <div class="flex flex-col gap-4">
      <div class="flex flex-wrap items-center gap-2 text-xs uppercase tracking-[0.2em] text-slate-500">
        <label class="flex items-center gap-2 rounded-full border border-slate-200 px-3 py-2 text-[10px]">
          <input v-model="modelMode" type="radio" value="url" class="h-3 w-3" />
          YouTube URL
        </label>
        <label class="flex items-center gap-2 rounded-full border border-slate-200 px-3 py-2 text-[10px]">
          <input v-model="modelMode" type="radio" value="transcript" class="h-3 w-3" />
          Paste transcript
        </label>
      </div>

      <div v-if="props.inputMode === 'url'">
        <label class="text-xs uppercase tracking-[0.2em] text-slate-500">YouTube URL</label>
        <input
          v-model="modelUrl"
          type="url"
          placeholder="https://www.youtube.com/watch?v=..."
          class="mt-2 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 focus:border-slate-400 focus:outline-none"
        />
      </div>

      <div v-else>
        <label class="text-xs uppercase tracking-[0.2em] text-slate-500">Paste transcript</label>
        <textarea
          v-model="modelTranscript"
          rows="6"
          placeholder="Paste transcript text here..."
          class="mt-2 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 focus:border-slate-400 focus:outline-none"
        ></textarea>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <button
          class="rounded-full bg-slate-900 px-5 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
          :disabled="!props.canGenerate"
          @click="emit('generate')"
        >
          {{ props.isLoading ? 'Generating...' : 'Generate flashcards' }}
        </button>
        <button
          class="rounded-full border border-slate-300 px-4 py-2 text-sm text-slate-700 hover:border-slate-400"
          @click="emit('toggle-advanced')"
        >
          {{ props.showAdvanced ? 'Hide' : 'Show' }} advanced
        </button>
        <span v-if="props.isLoading" class="text-xs text-slate-500">This may take ~20s.</span>
      </div>

      <div v-if="props.showAdvanced" class="grid gap-4 md:grid-cols-2">
        <div>
          <label class="text-xs uppercase tracking-[0.2em] text-slate-500">Pairs per chunk</label>
          <input
            v-model.number="modelPairs"
            type="number"
            min="1"
            max="10"
            class="mt-2 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 focus:border-slate-400 focus:outline-none"
          />
        </div>
        <div>
          <label class="text-xs uppercase tracking-[0.2em] text-slate-500">Max chunks</label>
          <input
            v-model.number="modelChunks"
            type="number"
            min="1"
            max="10"
            class="mt-2 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 focus:border-slate-400 focus:outline-none"
          />
        </div>
      </div>

      <p v-if="props.errorMessage" class="text-sm text-rose-600">{{ props.errorMessage }}</p>
    </div>
  </section>
</template>
