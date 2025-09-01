<template>
  <div class="header">
    <!-- Logo and Navigation -->
    <div class="logo-nav">
      <!-- Logo -->
      <div class="logo">
        <img src="../assets/logo_kor.gif" alt="고려대학교 로고" class="logo-image">
      </div>
      <!-- Navigation_bar -->
      <div class="navigation_bar">
        <div class="menu-item">
          <router-link to="/info" class="default-router">정보관리</router-link>
        </div>
        <div class="menu-item">
          <router-link to="/statistics" class="default-router">통계</router-link>
        </div>
        <div class="menu-item">
          <router-link to="/board" class="default-router">게시판</router-link>
        </div>
        <div class="menu-item">
          <router-link to="/qna" class="default-router">QnA</router-link>
        </div>
        <div class="menu-item">
          <router-link to="/eprofile" class="default-router">e-Profile</router-link>
        </div>
      </div>
    </div>
    
    <!-- User Actions -->
    <div class="user-actions" v-if="isAuthenticated">
      <div class="user-info">
        <span class="username">{{ user?.username }}</span>
      </div>
      <button @click="handleLogout" class="logout-button" :disabled="loading">
        {{ loading ? '로그아웃 중...' : '로그아웃' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const user = computed(() => authStore.user)
const isAuthenticated = computed(() => authStore.isAuthenticated)
const loading = computed(() => authStore.loading)

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}

// Initialize auth state on mount
onMounted(async () => {
  await authStore.checkSession()
})
</script>

<style>
.navigation_bar {
  height: 100%;
  width: 1332px;
  display: flex;
  align-items: center;
  gap: 16px;
  padding-top: 16px;
  margin-left: 150px;
  font-size: larger;
}
.header {
  display: flex;
  justify-content: space-between; /* Space between logo-nav and user-actions */
  align-items: center;
  width: 1920px;
  height: 120px;
  border-bottom: 1px solid var(--Gray_stroke, #DCE2ED);
  background-color: var(--White, #FCFCFC);
  position: fixed;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000; /* Ensure it stays above other elements */
  flex-shrink: 0; /* Ensure header doesn't shrink */
}
.logo-nav {
  margin-left: 320px;
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 860px;
}

.logo {
  display: flex;
  flex-shrink: 0; /* Ensure logo doesn't shrink */
  margin-right: 20px; /* Add margin if needed */
}

.logo-image {
  width: 150px; /* Adjusted the width of the logo image */
  height: auto; /* Maintain aspect ratio */
}
/* Media query for very small screens */
.menu-item {
  margin: 0 32px;
  background:none;
  border:none;
  padding:0;
  cursor: pointer;
}

.default-router {
  color: black;
  transition-duration: 0.2s;
  font-weight: 600;
  font-size: 18px;
  color: var(--Gray100, #CDCDCD);
}

.default-router:hover {
  background-color: transparent;
  font-weight: 700;
  color: #862633;
}

.router-link-active,
.router-link-exact-active {
  font-weight: 700;
  color: #862633;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-right: 320px;
  flex-shrink: 0;
  color: var(--Gray100, #CDCDCD);
}

.user-info {
  display: flex;
  align-items: center;
}

.username {
  font-size: 16px;
  font-weight: 500;
  color: #262626;
}

.logout-button {
  background: #910024;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.logout-button:hover:not(:disabled) {
  background: #7C0019;
}

.logout-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
