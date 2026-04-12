<script setup>
const props = defineProps({
  sets: { type: Array, default: () => [] },
  activeSetId: { type: String, default: null }
})

const emit = defineEmits(['select', 'create', 'rename', 'delete'])
</script>

<template>
  <aside class="w-full border-b border-slate-800/60 bg-[#0f131b] md:w-72 md:border-b-0 md:border-r">
    <div class="flex items-center gap-3 px-6 py-6">
      <div class="h-10 w-10 rounded-2xl bg-gradient-to-br from-emerald-400 to-amber-300"></div>
      <div>
        <p class="text-xs uppercase tracking-[0.35em] text-emerald-300">YouTube</p>
        <p class="text-lg font-semibold">Flashcards</p>
      </div>
    </div>

    <div class="px-4 pb-6">
      <div class="mb-4 flex items-center justify-between">
        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
          Flashcard Sets
        </p>
        <button
          class="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300 hover:border-emerald-300 hover:text-emerald-200"
          @click="emit('create')"
        >
          New set
        </button>
      </div>

      <div
        v-if="props.sets.length === 0"
        class="rounded-xl border border-dashed border-slate-800 px-4 py-6 text-sm text-slate-500"
      >
        Generate a set to see it here.
      </div>

      <div class="space-y-3">
        <button
          v-for="set in props.sets"
          :key="set.id"
          type="button"
          @click="emit('select', set.id)"
          class="group w-full rounded-2xl border border-slate-800/70 bg-[#121722] px-4 py-3 text-left transition hover:border-emerald-400/40"
          :class="props.activeSetId === set.id ? 'ring-1 ring-emerald-400/40' : ''"
        >
          <div class="flex items-start justify-between gap-2">
            <div class="min-w-0">
              <p class="truncate text-sm font-semibold text-slate-100">{{ set.title }}</p>
              <p class="text-xs text-slate-500">
                {{ set.flashcards.length }} cards · {{ new Date(set.createdAt).toLocaleDateString() }}
              </p>
            </div>
            <div class="flex gap-2 opacity-0 transition group-hover:opacity-100">
              <button
                class="text-xs text-slate-400 hover:text-emerald-300"
                @click.stop="emit('rename', set.id)"
              >
                Rename
              </button>
              <button
                class="text-xs text-slate-400 hover:text-rose-400"
                @click.stop="emit('delete', set.id)"
              >
                Delete
              </button>
            </div>
          </div>
        </button>
      </div>
    </div>
  </aside>
</template>
