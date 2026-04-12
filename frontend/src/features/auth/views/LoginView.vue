<script setup>
import { useRouter } from 'vue-router'
import AuthLogin from '../components/AuthLogin.vue'

const router = useRouter()

const handleLogin = () => {
  router.push('/dashboard')
}

const goRegister = () => {
  router.push('/register')
}
</script>

<template>
  <AuthLogin @login="handleLogin" @go-register="goRegister" />
</template>
