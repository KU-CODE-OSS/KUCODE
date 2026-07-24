import { useAuthStore } from '../stores/auth'

export const authGuard = async (to, from, next) => {
  const authStore = useAuthStore()
  await authStore.checkSession()

  if (authStore.isAuthenticated) {
    next()
  } else {
    next('/login')
  }
}

export const guestGuard = async (to, from, next) => {
  const authStore = useAuthStore()
  await authStore.checkSession()

  if (authStore.isAuthenticated) {
    next('/info/course')
  } else {
    next()
  }
}
