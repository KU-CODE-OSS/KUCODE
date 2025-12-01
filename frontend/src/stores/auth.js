// src/stores/auth.js
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import {
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged
} from 'firebase/auth'
import { auth } from '../services/firebase'
import { postLoginRole } from '../api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)
  const error = ref('')
  const role = ref(null)
  const memberId = ref(null)
  const memberName = ref(null)

  const isAuthenticated = computed(() => !!user.value)
  const canWriteBoard = computed(() => ['ADMIN', 'PROFESSOR'].includes(role.value))

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

      // Fetch role information from backend
      try {
        const roleResponse = await postLoginRole(firebaseUser.uid)
        if (roleResponse.data) {
          role.value = roleResponse.data.role
          memberId.value = roleResponse.data.member_id
          memberName.value = roleResponse.data.member_name

          // Cache role data in sessionStorage
          sessionStorage.setItem('userRole', role.value)
          sessionStorage.setItem('memberId', memberId.value)
          sessionStorage.setItem('memberName', memberName.value)
        }
      } catch (roleErr) {
        console.error('Failed to fetch role:', roleErr)
        // Continue with login even if role fetch fails
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
      role.value = null
      memberId.value = null
      memberName.value = null

      // Clear cached data
      sessionStorage.removeItem('userRole')
      sessionStorage.removeItem('memberId')
      sessionStorage.removeItem('memberName')
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      loading.value = false
    }
  }

  const checkSession = async () => {
    return new Promise((resolve) => {
      // Listen to Firebase auth state changes
      const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
        if (firebaseUser && firebaseUser.emailVerified) {
          user.value = {
            id: firebaseUser.uid,
            email: firebaseUser.email,
            username: firebaseUser.email.split('@')[0],
            isVerified: firebaseUser.emailVerified
          }

          // Try to restore role data from cache
          const cachedRole = sessionStorage.getItem('userRole')
          const cachedMemberId = sessionStorage.getItem('memberId')
          const cachedMemberName = sessionStorage.getItem('memberName')

          if (cachedRole && cachedMemberId && cachedMemberName) {
            role.value = cachedRole
            memberId.value = cachedMemberId
            memberName.value = cachedMemberName
          } else {
            // Cache miss - re-fetch from API
            try {
              const roleResponse = await postLoginRole(firebaseUser.uid)
              if (roleResponse.data) {
                role.value = roleResponse.data.role
                memberId.value = roleResponse.data.member_id
                memberName.value = roleResponse.data.member_name

                // Cache role data in sessionStorage
                sessionStorage.setItem('userRole', role.value)
                sessionStorage.setItem('memberId', memberId.value)
                sessionStorage.setItem('memberName', memberName.value)
              }
            } catch (roleErr) {
              console.error('Failed to fetch role during session check:', roleErr)
            }
          }
        } else {
          user.value = null
          role.value = null
          memberId.value = null
          memberName.value = null
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
    role,
    memberId,
    memberName,
    isAuthenticated,
    canWriteBoard,
    login,
    logout,
    checkSession
  }
})