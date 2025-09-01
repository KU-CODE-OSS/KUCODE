import { useAuthStore } from '../stores/auth'
import { onAuthStateChanged } from 'firebase/auth'
import { auth } from '../services/firebase'

export const authGuard = async (to, from, next) => {
  // Wait for Firebase auth to initialize
  await new Promise((resolve) => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      unsubscribe()
      resolve()
    })
  })
  
  const currentUser = auth.currentUser  // Current Firebase user
  
  if (currentUser && currentUser.emailVerified) {
    if (currentUser) {
      next()
    } else {
      next('/login')
    }
  }
}

export const guestGuard = async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Check session status
  await authStore.checkSession()
  
  if (!authStore.isAuthenticated) {
    next()
  } else {
    next('/login')
  }
}