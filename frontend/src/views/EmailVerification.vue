<template>
  <div class="email-verification-container">
    <!-- Background School Image -->
    <div class="background-image"></div>
    
    <!-- Header Frame (Logo + Platform Info) -->
    <div class="header-frame">
      <!-- Logo Frame -->
      <div class="logo-frame">
        <div class="logo-layer">
          <!-- University Logo placeholder -->
          <div class="logo-placeholder"></div>
        </div>
      </div>
      
      <!-- Divider -->
      <div class="divider"></div>
      
      <!-- Platform Info Frame -->
      <div class="platform-frame">
        <div class="platform-text">
          <div class="korean-title">오픈 소스 소프트웨어 플랫폼</div>
          <div class="english-title">Open Source Software Platform</div>
        </div>
      </div>
    </div>
    
    <!-- Main Content Frame -->
    <div class="main-frame">
      <!-- Email Verification Content -->
      <div class="verification-content">
        <!-- Email Icon -->
        <div class="email-icon-frame">
          <div class="email-icon">
            <svg width="58" height="45" viewBox="0 0 58 45" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M5 5H53V40H5V5Z" stroke="#910024" stroke-width="2.5" fill="none"/>
              <path d="M5 5L29 25L53 5" stroke="#910024" stroke-width="2.5" fill="none"/>
              <circle cx="41" cy="33" r="4" fill="#F7BEC7"/>
            </svg>
          </div>
        </div>
        
        <!-- Verification Text -->
        <div class="verification-text-frame">
          <h1 class="verification-title">인증 메일이 발송되었습니다</h1>
          <p class="verification-description">
            입력하신 이메일의 메일함에서 인증 메일을 확인해주세요<br>
            이메일 인증이 확인되면 회원가입이 완료됩니다
          </p>
        </div>
      </div>
      
      <!-- Resend Email Button -->
      <button 
        @click="handleResendEmail"
        :disabled="resending || cooldown > 0"
        class="resend-button"
      >
        {{ getResendButtonText() }}
      </button>
      
      <!-- Back to Registration Link -->
      <div class="back-link-text">
        <router-link to="/register" class="back-link">
          이전 페이지로 돌아가서 이메일 재입력 (Re-enter Email)
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { sendEmailVerification } from 'firebase/auth'
import { auth } from '../services/firebase'
import { useAuthStore } from '../stores/auth'

// Router and store
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// State management
const resending = ref(false)
const cooldown = ref(0)
const email = ref('')

// Timer for cooldown
let cooldownTimer = null

// Get resend button text based on state
const getResendButtonText = () => {
  if (resending.value) {
    return '발송 중...'
  } else if (cooldown.value > 0) {
    return `재발송 가능 (${cooldown.value}초)`
  } else {
    return '인증 메일 재발송 (Resend)'
  }
}

// Handle resend email
const handleResendEmail = async () => {
  try {
    resending.value = true
    
    const user = auth.currentUser
    if (!user) {
      // If no current user, redirect to registration
      router.push('/register')
      return
    }
    
    // Send verification email
    await sendEmailVerification(user)
    
    // Start cooldown timer (60 seconds)
    cooldown.value = 60
    cooldownTimer = setInterval(() => {
      cooldown.value--
      if (cooldown.value <= 0) {
        clearInterval(cooldownTimer)
        cooldownTimer = null
      }
    }, 1000)
    
    console.log('Verification email resent successfully')
    
  } catch (error) {
    console.error('Error resending verification email:', error)
    // Handle specific errors if needed
    if (error.code === 'auth/too-many-requests') {
      alert('너무 많은 요청이 발생했습니다. 잠시 후 다시 시도해주세요.')
    } else {
      alert('인증 메일 재발송 중 오류가 발생했습니다.')
    }
  } finally {
    resending.value = false
  }
}

// Check authentication state on mount
onMounted(async () => {
  await authStore.checkSession()
  
  // Get email from current user
  email.value = auth.currentUser.email
  
  // If user is already verified, redirect to board
  if (authStore.isAuthenticated && auth.currentUser?.emailVerified) {
    router.push('/board')
  }
  
  // If no current user, redirect to registration
  if (!auth.currentUser) {
    router.push('/register')
  }
})

// Clean up timer on unmount
onUnmounted(() => {
  if (cooldownTimer) {
    clearInterval(cooldownTimer)
  }
})
</script>

<style scoped>
/* Import Pretendard font */
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.8/dist/web/static/pretendard.css');

/* Main Container */
.email-verification-container {
  position: relative;
  width: 100%;
  height: 100vh;
  margin-top: 120px; /* Account for navigation bar */
  background: #FFFFFF;
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
  overflow: hidden;
}

/* Background School Image - exact Figma positioning */
.background-image {
  position: absolute;
  width: 845px;
  height: 1268px;
  left: 0px;
  top: 0px;
  background: url('/login_school.jpg') no-repeat center center;
  background-size: cover;
}

/* Header Frame - exact Figma positioning */
.header-frame {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0px;
  gap: 6px;
  position: absolute;
  width: 471.96px;
  height: 73.21px;
  left: 864px;
  top: 38px;
}

/* Logo Frame - exact Figma specs */
.logo-frame {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 10px;
  gap: 10px;
  width: 216.96px;
  height: 73.21px;
  flex: none;
  order: 0;
  flex-grow: 0;
}

.logo-layer {
  width: 196.96px;
  height: 53.21px;
  flex: none;
  order: 0;
  flex-grow: 0;
  position: relative;
}

.logo-placeholder {
  width: 100%;
  height: 100%;
  background: #7C0019;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: url('/login_logo.png') no-repeat center center;
}

/* Divider - exact Figma specs */
.divider {
  width: 0px;
  height: 46px;
  border: 2px solid #910024;
  flex: none;
  order: 1;
  flex-grow: 0;
}

/* Platform Frame - exact Figma specs */
.platform-frame {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 10px 10px 14px;
  gap: 10px;
  width: 243px;
  height: 73px;
  flex: none;
  order: 2;
  flex-grow: 0;
}

.platform-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 0px;
  width: 223px;
  height: 44px;
  flex: none;
  order: 0;
  align-self: stretch;
  flex-grow: 0;
}

.korean-title {
  width: 223px;
  height: 27px;
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 500;
  font-size: 20px;
  line-height: 24px;
  text-align: center;
  color: #262626;
  flex: none;
  order: 0;
  align-self: stretch;
  flex-grow: 0;
}

.english-title {
  width: 223px;
  height: 17px;
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 400;
  font-size: 14px;
  line-height: 17px;
  text-align: center;
  color: #616161;
  flex: none;
  order: 1;
  align-self: stretch;
  flex-grow: 0;
}

/* Main Frame - exact Figma positioning */
.main-frame {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 0px;
  gap: 40px;
  position: absolute;
  width: 416px;
  height: 327px;
  left: 1189px;
  top: 377px;
}

/* Verification Content */
.verification-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0px;
  gap: 30px;
  width: 416px;
  height: 176px;
  flex: none;
  order: 0;
  align-self: stretch;
  flex-grow: 0;
}

/* Email Icon Frame */
.email-icon-frame {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 7.29167px;
  width: 70px;
  height: 58px;
  flex: none;
  order: 0;
  flex-grow: 0;
}

.email-icon {
  width: 58.17px;
  height: 44.85px;
  flex: none;
  order: 0;
  flex-grow: 0;
}

/* Verification Text Frame */
.verification-text-frame {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 0px;
  gap: 20px;
  width: 416px;
  height: 88px;
  flex: none;
  order: 1;
  align-self: stretch;
  flex-grow: 0;
}

.verification-title {
  width: 416px;
  height: 26px;
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 600;
  font-size: 22px;
  line-height: 26px;
  text-align: center;
  letter-spacing: -0.004em;
  color: #262626;
  flex: none;
  order: 0;
  align-self: stretch;
  flex-grow: 0;
  margin: 0;
}

.verification-description {
  width: 416px;
  height: 42px;
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 400;
  font-size: 18px;
  line-height: 21px;
  text-align: center;
  color: #616161;
  flex: none;
  order: 1;
  align-self: stretch;
  flex-grow: 0;
  margin: 0;
}

/* Resend Button */
.resend-button {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  padding: 14px 0px;
  gap: 10px;
  width: 416px;
  height: 50px;
  background: #910024;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  flex: none;
  order: 1;
  align-self: stretch;
  flex-grow: 0;
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 600;
  font-size: 18px;
  line-height: 21px;
  text-align: center;
  color: #FCFCFC;
  transition: background-color 0.2s ease;
}

.resend-button:hover:not(:disabled) {
  background: #7C0019;
}

.resend-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Back Link Text */
.back-link-text {
  width: 416px;
  height: 21px;
  flex: none;
  order: 2;
  align-self: stretch;
  flex-grow: 0;
}

.back-link {
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 400;
  font-size: 18px;
  line-height: 21px;
  text-align: center;
  color: #949494;
  text-decoration: none;
  display: block;
  width: 100%;
}

.back-link:hover {
  text-decoration: underline;
  color: #616161;
}

/* Responsive adjustments that maintain Figma proportions */
@media (max-width: 1600px) {
  .email-verification-container {
    transform: scale(0.8);
    transform-origin: top left;
  }
}

@media (max-width: 1400px) {
  .email-verification-container {
    transform: scale(0.7);
    transform-origin: top left;
  }
}

@media (max-width: 1200px) {
  .email-verification-container {
    transform: none;
    height: auto;
    padding: 20px;
  }
  
  .background-image {
    position: relative;
    width: 100%;
    height: 300px;
    left: 0;
    top: 0;
  }
  
  .header-frame {
    position: relative;
    left: 0;
    top: 20px;
    width: 100%;
    justify-content: center;
    margin: 20px 0;
  }
  
  .main-frame {
    position: relative;
    left: 0;
    top: 0;
    width: 100%;
    max-width: 416px;
    margin: 20px auto 0;
  }
}
</style>