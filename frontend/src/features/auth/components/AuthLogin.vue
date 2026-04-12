<script setup>
import { ref } from 'vue'

const emit = defineEmits(['login', 'go-register'])

const email = ref('')
const password = ref('')
const remember = ref(true)
</script>

<template>
  <div class="min-h-screen bg-[#0b0e13] text-slate-100">
    <div class="relative mx-auto flex min-h-screen max-w-6xl flex-col items-center justify-center gap-10 px-6 py-12 lg:flex-row">
      <div class="max-w-lg">
        <p class="text-xs uppercase tracking-[0.35em] text-emerald-300">Welcome back</p>
        <h1 class="mt-4 text-4xl font-semibold leading-tight">Log in to your flashcard studio.</h1>
        <p class="mt-3 text-sm text-slate-400">
          Your study sets, history, and shared decks live here. Sign in to keep everything in one place.
        </p>
        <div class="mt-8 grid gap-3 text-sm text-slate-300">
          <div class="flex items-center gap-3 rounded-full border border-slate-800/60 bg-slate-950/60 px-4 py-2">
            <span class="h-2 w-2 rounded-full bg-emerald-400"></span>
            <span>Keep your generated sets organized by course.</span>
          </div>
          <div class="flex items-center gap-3 rounded-full border border-slate-800/60 bg-slate-950/60 px-4 py-2">
            <span class="h-2 w-2 rounded-full bg-amber-400"></span>
            <span>Resume from where you left off in seconds.</span>
          </div>
          <div class="flex items-center gap-3 rounded-full border border-slate-800/60 bg-slate-950/60 px-4 py-2">
            <span class="h-2 w-2 rounded-full bg-sky-400"></span>
            <span>Share decks when teamwork matters.</span>
          </div>
        </div>
      </div>

      <div class="w-full max-w-md rounded-2xl border border-slate-800/60 bg-slate-950/70 p-6 shadow-2xl shadow-black/40">
        <div class="mb-6">
          <h2 class="text-2xl font-semibold">Login</h2>
          <p class="mt-1 text-sm text-slate-400">Use any email for the demo.</p>
        </div>

        <form class="flex flex-col gap-4" @submit.prevent="emit('login')">
          <label class="flex flex-col gap-2 text-sm">
            Email
            <input
              v-model="email"
              type="email"
              autocomplete="email"
              placeholder="you@school.edu"
              class="rounded-lg border border-slate-800 bg-slate-900/70 px-4 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-emerald-400 focus:outline-none"
            />
          </label>

          <label class="flex flex-col gap-2 text-sm">
            Password
            <input
              v-model="password"
              type="password"
              autocomplete="current-password"
              placeholder="********"
              class="rounded-lg border border-slate-800 bg-slate-900/70 px-4 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-emerald-400 focus:outline-none"
            />
          </label>

          <div class="flex items-center justify-between text-xs text-slate-400">
            <label class="flex items-center gap-2">
              <input v-model="remember" type="checkbox" class="h-4 w-4 rounded border-slate-700 bg-slate-900" />
              Remember me
            </label>
            <button type="button" class="text-emerald-300 hover:text-emerald-200">Forgot password?</button>
          </div>

          <button
            type="submit"
            class="mt-2 rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-emerald-400"
          >
            Log in
          </button>

          <button
            type="button"
            class="rounded-lg border border-slate-800 px-4 py-2 text-sm text-slate-200 transition hover:border-emerald-400"
            @click="emit('go-register')"
          >
            Create an account
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
