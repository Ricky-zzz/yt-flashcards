<script setup>
import { useRouter } from 'vue-router'
import AuthRegister from '../components/AuthRegister.vue'

const router = useRouter()

const handleRegister = () => {
  router.push('/dashboard')
}

const goLogin = () => {
  router.push('/login')
}
</script>

<template>
  <AuthRegister @register="handleRegister" @go-login="goLogin" />
</template>
