<script setup>
const props = defineProps({
  title: { type: String, default: '' },
  youtubeUrl: { type: String, default: '' },
  metadata: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['add-card'])
</script>

<template>
  <section class="rounded-2xl border border-slate-800 bg-[#121722] p-6">
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <p class="text-xs uppercase tracking-[0.2em] text-slate-500">Active set</p>
        <h2 class="mt-1 text-xl font-semibold text-slate-100">{{ props.title }}</h2>
        <p v-if="props.youtubeUrl" class="mt-2 text-xs text-slate-400">{{ props.youtubeUrl }}</p>
        <p class="mt-2 text-sm text-slate-400">
          {{ props.metadata.total_cards || 0 }} cards · {{ props.metadata.chunks_processed || 0 }} chunks ·
          {{ props.metadata.processing_time || 0 }}s
        </p>
      </div>
      <div class="flex items-center gap-3">
        <button
          class="rounded-full border border-emerald-400/40 px-4 py-2 text-sm text-emerald-200 transition hover:border-emerald-300 hover:text-emerald-100"
          @click="emit('add-card')"
        >
          Add card
        </button>
        <span
          class="rounded-full border border-slate-800 px-3 py-1 text-xs"
          :class="props.metadata.classification_skipped ? 'text-amber-300' : 'text-emerald-300'"
        >
          {{ props.metadata.classification_skipped ? 'Classifier skipped' : 'Classifier ok' }}
        </span>
      </div>
    </div>
  </section>
</template>
