<script setup>
import { ref } from 'vue'
import { registerUser } from '../services/authService'

const emit = defineEmits(['register', 'go-login'])

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const isLoading = ref(false)
const errorMessage = ref('')

const handleSubmit = async () => {
  if (!email.value || !password.value) return
  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'Passwords do not match'
    return
  }

  errorMessage.value = ''
  isLoading.value = true

  try {
    await registerUser({
      email: email.value,
      password: password.value,
      fullName: name.value
    })
    emit('register')
  } catch (err) {
    errorMessage.value = err?.message || 'Registration failed'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#f8fafc] text-slate-900">
    <div class="relative mx-auto flex min-h-screen max-w-6xl flex-col items-center justify-center gap-10 px-6 py-12 lg:flex-row">
      <div class="max-w-lg">
        <p class="text-xs uppercase tracking-[0.35em] text-slate-500">Start fresh</p>
        <h1 class="mt-4 text-4xl font-semibold leading-tight text-slate-900">Create your study workspace.</h1>
        <p class="mt-3 text-sm text-slate-600">
          Build sets, track learning progress, and keep everything tied to your account.
        </p>
        <div class="mt-8 grid gap-3 text-sm text-slate-600">
          <div class="flex items-center gap-3 rounded-full border border-slate-200 bg-white px-4 py-2">
            <span class="h-2 w-2 rounded-full bg-slate-900"></span>
            <span>Save every video-generated deck automatically.</span>
          </div>
          <div class="flex items-center gap-3 rounded-full border border-slate-200 bg-white px-4 py-2">
            <span class="h-2 w-2 rounded-full bg-slate-900"></span>
            <span>Sync study plans across devices.</span>
          </div>
          <div class="flex items-center gap-3 rounded-full border border-slate-200 bg-white px-4 py-2">
            <span class="h-2 w-2 rounded-full bg-slate-900"></span>
            <span>Invite teammates to co-build flashcards.</span>
          </div>
        </div>
      </div>

      <div class="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-6 shadow-xl shadow-slate-200/50">
        <div class="mb-6">
          <h2 class="text-2xl font-semibold text-slate-900">Register</h2>
          <p class="mt-1 text-sm text-slate-500">Creates a local demo account.</p>
        </div>

        <form class="flex flex-col gap-4" @submit.prevent="handleSubmit">
          <label class="flex flex-col gap-2 text-sm">
            Full name
            <input
              v-model="name"
              type="text"
              autocomplete="name"
              placeholder="Alex Carter"
              class="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-slate-400 focus:outline-none"
            />
          </label>

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
              autocomplete="new-password"
              placeholder="Create a password"
              class="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-slate-400 focus:outline-none"
            />
          </label>

          <label class="flex flex-col gap-2 text-sm">
            Confirm password
            <input
              v-model="confirmPassword"
              type="password"
              autocomplete="new-password"
              placeholder="Confirm password"
              class="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-slate-400 focus:outline-none"
            />
          </label>

          <button
            type="submit"
            class="mt-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-70"
            :disabled="isLoading"
          >
            {{ isLoading ? 'Creating...' : 'Create account' }}
          </button>

          <p v-if="errorMessage" class="text-sm text-rose-600">{{ errorMessage }}</p>

          <button
            type="button"
            class="rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-700 transition hover:border-slate-400"
            @click="emit('go-login')"
          >
            I already have an account
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
