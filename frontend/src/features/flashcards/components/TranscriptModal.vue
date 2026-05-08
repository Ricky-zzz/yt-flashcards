<script setup>
const props = defineProps({
  transcript: { type: String, default: '' },
  title: { type: String, default: 'Transcript' },
  pdfUrl: { type: String, default: '' }
})

const emit = defineEmits(['close'])
</script>

<template>
  <div
    v-if="props.transcript || props.pdfUrl"
    class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4"
    role="dialog"
    aria-modal="true"
    :aria-label="`${props.title} transcript`"
    @click.self="emit('close')"
  >
    <div class="w-full max-w-5xl rounded-2xl bg-white p-6 shadow-xl">
      <div class="flex flex-wrap items-start justify-between gap-3 mb-4">
        <div>
          <p class="text-xs uppercase tracking-[0.2em] text-slate-500">Transcript</p>
          <p class="text-lg font-semibold text-slate-900">{{ props.title }}</p>
        </div>
        <button
          class="rounded-full border border-slate-300 px-3 py-2 text-xs text-slate-700 hover:border-slate-400"
          @click="emit('close')"
        >
          Close
        </button>
      </div>

      <div class="grid gap-4 md:grid-cols-2">
        <div class="max-h-[70vh] overflow-y-auto rounded-xl border border-slate-200 bg-slate-50 p-6 pr-4">
          <p class="whitespace-pre-wrap text-sm leading-relaxed text-slate-800">
            {{ props.transcript || 'No transcript available.' }}
          </p>
        </div>
        <div v-if="props.pdfUrl" class="h-[70vh] overflow-hidden rounded-xl border border-slate-200 bg-slate-50">
          <iframe
            :src="props.pdfUrl"
            title="PDF preview"
            class="h-full w-full"
          ></iframe>
        </div>
      </div>
    </div>
  </div>
</template>
