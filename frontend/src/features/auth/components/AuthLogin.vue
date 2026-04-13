<script setup>
import { ref } from 'vue'
import { loginUser } from '../services/authService'

const emit = defineEmits(['login', 'go-register'])

const email = ref('')
const password = ref('')
const remember = ref(true)
const isLoading = ref(false)
const errorMessage = ref('')

const handleSubmit = async () => {
  if (!email.value || !password.value) return
  errorMessage.value = ''
  isLoading.value = true

  try {
    await loginUser({ email: email.value, password: password.value })
    emit('login')
  } catch (err) {
    errorMessage.value = err?.message || 'Login failed'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#f8fafc] text-slate-900">
    <div class="relative mx-auto flex min-h-screen max-w-6xl flex-col items-center justify-center gap-10 px-6 py-12 lg:flex-row">
      <div class="max-w-lg">
        <p class="text-xs uppercase tracking-[0.35em] text-slate-500">Welcome back</p>
        <h1 class="mt-4 text-4xl font-semibold leading-tight text-slate-900">Log in to your flashcard studio.</h1>
        <p class="mt-3 text-sm text-slate-600">
          Your study sets, history, and shared decks live here. Sign in to keep everything in one place.
        </p>
        <div class="mt-8 grid gap-3 text-sm text-slate-600">
          <div class="flex items-center gap-3 rounded-full border border-slate-200 bg-white px-4 py-2">
            <span class="h-2 w-2 rounded-full bg-slate-900"></span>
            <span>Keep your generated sets organized by course.</span>
          </div>
          <div class="flex items-center gap-3 rounded-full border border-slate-200 bg-white px-4 py-2">
            <span class="h-2 w-2 rounded-full bg-slate-900"></span>
            <span>Resume from where you left off in seconds.</span>
          </div>
          <div class="flex items-center gap-3 rounded-full border border-slate-200 bg-white px-4 py-2">
            <span class="h-2 w-2 rounded-full bg-slate-900"></span>
            <span>Share decks when teamwork matters.</span>
          </div>
        </div>
      </div>

      <div class="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-6 shadow-xl shadow-slate-200/50">
        <div class="mb-6">
          <h2 class="text-2xl font-semibold text-slate-900">Login</h2>
          <p class="mt-1 text-sm text-slate-500">Use any email for the demo.</p>
        </div>

        <form class="flex flex-col gap-4" @submit.prevent="handleSubmit">
          <label class="flex flex-col gap-2 text-sm">
            Email
            <input
              v-model="email"
              type="email"
              autocomplete="email"
              placeholder="you@school.edu"
              class="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-slate-400 focus:outline-none"
            />
          </label>

          <label class="flex flex-col gap-2 text-sm">
            Password
            <input
              v-model="password"
              type="password"
              autocomplete="current-password"
              placeholder="********"
              class="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-slate-400 focus:outline-none"
            />
          </label>

          <div class="flex items-center justify-between text-xs text-slate-500">
            <label class="flex items-center gap-2">
              <input v-model="remember" type="checkbox" class="h-4 w-4 rounded border-slate-300 bg-white" />
              Remember me
            </label>
            <button type="button" class="text-slate-600 hover:text-slate-900">Forgot password?</button>
          </div>

          <button
            type="submit"
            class="mt-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-70"
            :disabled="isLoading"
          >
            {{ isLoading ? 'Signing in...' : 'Log in' }}
          </button>

          <p v-if="errorMessage" class="text-sm text-rose-600">{{ errorMessage }}</p>

          <button
            type="button"
            class="rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-700 transition hover:border-slate-400"
            @click="emit('go-register')"
          >
            Create an account
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
