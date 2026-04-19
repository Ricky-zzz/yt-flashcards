<script setup>
const props = defineProps({
  title: { type: String, default: '' },
  youtubeUrl: { type: String, default: '' },
  metadata: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['add-card', 'review'])
</script>

<template>
  <section class="rounded-2xl border border-slate-200 bg-white p-6">
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <p class="text-xs uppercase tracking-[0.2em] text-slate-500">Active set</p>
        <h2 class="mt-1 text-xl font-semibold text-slate-900">{{ props.title }}</h2>
        <p v-if="props.youtubeUrl" class="mt-2 text-xs text-slate-500">{{ props.youtubeUrl }}</p>
        <p class="mt-2 text-sm text-slate-600">
          {{ props.metadata.total_cards || 0 }} cards · {{ props.metadata.chunks_processed || 0 }} chunks ·
          {{ props.metadata.processing_time || 0 }}s
        </p>
      </div>
      <div class="flex items-center gap-3">
        <button
          class="rounded-full border border-slate-300 px-4 py-2 text-sm text-slate-700 transition hover:border-slate-400"
          @click="emit('review')"
        >
          Review
        </button>
        <button
          class="rounded-full bg-slate-900 px-4 py-2 text-sm text-white transition hover:bg-slate-800"
          @click="emit('add-card')"
        >
          Add card
        </button>
      </div>
    </div>
  </section>
</template>
