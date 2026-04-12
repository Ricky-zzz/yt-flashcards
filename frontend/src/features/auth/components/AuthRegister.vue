<script setup>
import { ref } from 'vue'

const emit = defineEmits(['register', 'go-login'])

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
</script>

<template>
  <div class="min-h-screen bg-[#0b0e13] text-slate-100">
    <div class="relative mx-auto flex min-h-screen max-w-6xl flex-col items-center justify-center gap-10 px-6 py-12 lg:flex-row">
      <div class="max-w-lg">
        <p class="text-xs uppercase tracking-[0.35em] text-amber-300">Start fresh</p>
        <h1 class="mt-4 text-4xl font-semibold leading-tight">Create your study workspace.</h1>
        <p class="mt-3 text-sm text-slate-400">
          Build sets, track learning progress, and keep everything tied to your account.
        </p>
        <div class="mt-8 grid gap-3 text-sm text-slate-300">
          <div class="flex items-center gap-3 rounded-full border border-slate-800/60 bg-slate-950/60 px-4 py-2">
            <span class="h-2 w-2 rounded-full bg-amber-400"></span>
            <span>Save every video-generated deck automatically.</span>
          </div>
          <div class="flex items-center gap-3 rounded-full border border-slate-800/60 bg-slate-950/60 px-4 py-2">
            <span class="h-2 w-2 rounded-full bg-emerald-400"></span>
            <span>Sync study plans across devices.</span>
          </div>
          <div class="flex items-center gap-3 rounded-full border border-slate-800/60 bg-slate-950/60 px-4 py-2">
            <span class="h-2 w-2 rounded-full bg-indigo-400"></span>
            <span>Invite teammates to co-build flashcards.</span>
          </div>
        </div>
      </div>

      <div class="w-full max-w-md rounded-2xl border border-slate-800/60 bg-slate-950/70 p-6 shadow-2xl shadow-black/40">
        <div class="mb-6">
          <h2 class="text-2xl font-semibold">Register</h2>
          <p class="mt-1 text-sm text-slate-400">Demo form only, no data is saved.</p>
        </div>

        <form class="flex flex-col gap-4" @submit.prevent="emit('register')">
          <label class="flex flex-col gap-2 text-sm">
            Full name
            <input
              v-model="name"
              type="text"
              autocomplete="name"
              placeholder="Alex Carter"
              class="rounded-lg border border-slate-800 bg-slate-900/70 px-4 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-amber-400 focus:outline-none"
            />
          </label>

          <label class="flex flex-col gap-2 text-sm">
            Email
            <input
              v-model="email"
              type="email"
              autocomplete="email"
              placeholder="you@school.edu"
              class="rounded-lg border border-slate-800 bg-slate-900/70 px-4 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-amber-400 focus:outline-none"
            />
          </label>

          <label class="flex flex-col gap-2 text-sm">
            Password
            <input
              v-model="password"
              type="password"
              autocomplete="new-password"
              placeholder="Create a password"
              class="rounded-lg border border-slate-800 bg-slate-900/70 px-4 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-amber-400 focus:outline-none"
            />
          </label>

          <label class="flex flex-col gap-2 text-sm">
            Confirm password
            <input
              v-model="confirmPassword"
              type="password"
              autocomplete="new-password"
              placeholder="Confirm password"
              class="rounded-lg border border-slate-800 bg-slate-900/70 px-4 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-amber-400 focus:outline-none"
            />
          </label>

          <button
            type="submit"
            class="mt-2 rounded-lg bg-amber-400 px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-amber-300"
          >
            Create account
          </button>

          <button
            type="button"
            class="rounded-lg border border-slate-800 px-4 py-2 text-sm text-slate-200 transition hover:border-amber-300"
            @click="emit('go-login')"
          >
            I already have an account
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
