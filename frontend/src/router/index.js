import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../features/auth/views/LoginView.vue'
import RegisterView from '../features/auth/views/RegisterView.vue'
import DashboardView from '../features/flashcards/views/DashboardView.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/register', name: 'register', component: RegisterView },
  { path: '/dashboard', name: 'dashboard', component: DashboardView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
