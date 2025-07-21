// src/stores/auth.js
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { 
  signInWithEmailAndPassword, 
  signOut, 
  onAuthStateChanged 
} from 'firebase/auth'
import { auth } from '../services/firebase'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)
  const error = ref('')

  const isAuthenticated = computed(() => !!user.value)

  const login = async (email, password) => {
    try {
      loading.value = true
      error.value = ''

      // Sign in with Firebase
      const userCredential = await signInWithEmailAndPassword(auth, email, password)
      const firebaseUser = userCredential.user

      // TODO: Implement email verification first to activate
      // Check if email is verified
      // if (!firebaseUser.emailVerified) {
      //   error.value = '이메일 인증을 완료해주세요'
      //   await signOut(auth)
      //   return { success: false, error: error.value }
      // }

      // Set user data from Firebase
      user.value = {
        id: firebaseUser.uid,
        email: firebaseUser.email,
        username: firebaseUser.email.split('@')[0],
        isVerified: firebaseUser.emailVerified
      }
      
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.error || err.message
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      loading.value = true
      
      // Sign out from Firebase
      await signOut(auth)
      
      user.value = null
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      loading.value = false
    }
  }

  const checkSession = async () => {
    return new Promise((resolve) => {
      // Listen to Firebase auth state changes
      const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
        if (firebaseUser && firebaseUser.emailVerified) {
          user.value = {
            id: firebaseUser.uid,
            email: firebaseUser.email,
            username: firebaseUser.email.split('@')[0],
            isVerified: firebaseUser.emailVerified
          }
        } else {
          user.value = null
        }
        unsubscribe() // Unsubscribe after first check
        resolve()
      })
    })
  }

  return {
    user,
    loading,
    error,
    isAuthenticated,
    login,
    logout,
    checkSession
  }
})