<template>
  <div class="registration-container">
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
      <!-- Basic Info Section -->
      <div class="basic-info-section">
        <div class="section-header">
          <h2 class="section-title">기본 정보</h2>
        </div>
        
        <div class="input-section-frame">
          <!-- Name Input -->
          <div class="input-field">
            <input 
              type="text" 
              v-model="studentName"
              placeholder="성명"
              class="input-control"
            />
          </div>
          
          <!-- Student ID with Verification -->
          <div class="name-verification-frame">
            <div class="input-field name-input">
              <input 
                type="text" 
                v-model="studentId"
                placeholder="학번"
                class="input-control"
              />
            </div>
            <button 
              @click="handleStudentIdVerification"
              :disabled="!studentId || studentIdVerifying"
              :class="[
                'verification-button',
                studentIdVerified ? 'verified' : ''
              ]"
            >
              {{ studentIdVerified ? '인증 완료' : (studentIdVerifying ? '인증 중...' : '인증하기') }}
            </button>
          </div>
          
          <!-- Name Input -->
          <!-- <div class="input-field">
            <input 
              type="text" 
              v-model="studentName"
              placeholder="성명"
              class="input-control"
            />
          </div> -->
        </div>
        
        <!-- Basic Info Error Message -->
        <div 
          v-if="basicInfoError" 
          class="error-message basic-error"
        >
          {{ basicInfoError }}
        </div>
      </div>
      
      <!-- Account Info Section -->
      <div class="account-info-section">
        <div class="section-header">
          <h2 class="section-title">계정 정보</h2>
        </div>
        
        <div class="input-section-frame">
          <!-- Email Input -->
          <div class="input-field">
            <input 
              type="email" 
              v-model="email"
              placeholder="이메일 (@korea.ac.kr)"
              class="input-control"
            />
          </div>
          
          <!-- Password Input -->
          <div class="input-field">
            <input 
              type="password" 
              v-model="password"
              placeholder="비밀번호"
              class="input-control"
            />
          </div>
          
          <!-- Confirm Password Input -->
          <div class="input-field">
            <input 
              type="password" 
              v-model="confirmPassword"
              placeholder="비밀번호 확인"
              class="input-control"
            />
          </div>
        </div>
        
        <!-- Account Info Error Message -->
        <div 
          v-if="accountInfoError" 
          class="error-message account-error"
        >
          {{ accountInfoError }}
        </div>
      </div>
      
      <!-- Sign Up Button -->
      <button 
        @click="handleSignUp"
        :disabled="loading || !isFormValid"
        class="signup-button-frame"
      >
        {{ loading ? '가입 중...' : '회원가입 (Sign up)' }}
      </button>
      
      <!-- Login Link -->
      <div class="login-text">
        이미 등록된 계정이 있다면 
        <router-link to="/login" class="login-link">
          로그인 (Login)
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createUserWithEmailAndPassword, sendEmailVerification } from 'firebase/auth'
import { auth } from '../services/firebase'
import { useAuthStore } from '../stores/auth'
import { checkStudentIdNumber } from '@/api.js'
import axios from 'axios'

// Form data
const studentId = ref('')
const studentName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')

// State management
const loading = ref(false)
const studentIdVerifying = ref(false)
const studentIdVerified = ref(false)
const basicInfoError = ref('')
const accountInfoError = ref('')

// Store and router
const authStore = useAuthStore()
const router = useRouter()

console.log(studentIdVerified.value)

// Computed properties
const isFormValid = computed(() => {
  return studentId.value && 
         studentName.value && 
         studentIdVerified.value &&
         email.value && 
         password.value && 
         confirmPassword.value &&
         email.value.endsWith('@korea.ac.kr') &&
         password.value === confirmPassword.value
})

// Handle student ID verification
const handleStudentIdVerification = async () => {
  try {
    studentIdVerifying.value = false
    basicInfoError.value = ''

    // TODO: Catch up on KU API status -> fix 학번 verification once caught up
    // const result = await checkStudentIdNumber(studentId)
    // console.log(result)

    // const undergraduate_url = "https://kuapi.korea.ac.kr/svc/academic-record/student/undergraduate-gra"
    // const CLIENT_ID = "openSourcePlat"
    // const ACCESS_TOKEN = "6dff0e00dfc84b1a81a7d6a1b3c66a0d"

    // // Make API call to verify student ID
    // const response = await axios.get(undergraduate_url, {
    //   headers: {'AUTH_KEY': ACCESS_TOKEN},
    //   params: {
    //     'client_id': CLIENT_ID,
    //     'std_id': studentId.value
    //   },
    // })

  // --------------------
  //   // Handle successful verification response
  //   if (response.data.success) {
  //     studentIdVerified.value = true
  //     // Optionally auto-fill verified student name from response
  //     if (response.data.studentName) {
  //       studentName.value = response.data.studentName
  //     }
  //   } else {
  //     basicInfoError.value = response.data.error || '학번 인증에 실패했습니다'
  //   }

  // } catch (error) {
  //   // Handle API error
  //   if (error.response) {
  //     // Server responded with error status
  //     basicInfoError.value = error.response.data?.message || '학번 인증에 실패했습니다'
  //   } else if (error.request) {
  //     // Network error
  //     basicInfoError.value = '네트워크 오류가 발생했습니다'
  //   } else {
  //     // Other error
  //     basicInfoError.value = '인증 중 오류가 발생했습니다'
  //   }
  //   console.error('Student ID verification error:', error)
  // } finally {
  //   studentIdVerifying.value = false
  }
  catch{
    studentIdVerifying.value = false
    studentIdVerified.value = true
  } finally {
    studentIdVerifying.value = false
    studentIdVerified.value = true
  }

}

// Handle sign up
const handleSignUp = async () => {
  try {
    loading.value = true
    basicInfoError.value = ''
    accountInfoError.value = ''
    
    // Validate email domain
    if (!email.value.endsWith('@korea.ac.kr')) {
      accountInfoError.value = '사용 가능한 @korea.ac.kr 이메일을 입력해주세요'
      return
    }
    
    // Validate password match
    if (password.value !== confirmPassword.value) {
      accountInfoError.value = '비밀번호가 일치하지 않습니다'
      return
    }
    
    // Validate student ID verification
    if (!studentIdVerified.value) {
      basicInfoError.value = '학번 인증을 완료해주세요'
      return
    }
    
    // Create Firebase user
    const userCredential = await createUserWithEmailAndPassword(
      auth, 
      email.value, 
      password.value
    )
    
    const firebaseUser = userCredential.user
    
    // Send email verification
    await sendEmailVerification(firebaseUser)

    router.push({
      name: 'emailVerification'
    })
    
  } catch (error) {
    if (error.code === 'auth/email-already-in-use') {
      accountInfoError.value = '이미 사용 중인 이메일입니다'
    } else if (error.code === 'auth/weak-password') {
      accountInfoError.value = '비밀번호가 너무 약합니다 (최소 6자)'
    } else if (error.code === 'auth/invalid-email') {
      accountInfoError.value = '유효하지 않은 이메일 형식입니다'
    } else {
      accountInfoError.value = error.message || '회원가입 중 오류가 발생했습니다'
    }
    console.error('Registration error:', error)
  } finally {
    loading.value = false
  }
}

// Reset student ID verification when student ID changes
const resetStudentIdVerification = () => {
  studentIdVerified.value = false
  basicInfoError.value = ''
}

// Watch for changes in student ID
import { watch } from 'vue'
watch(studentId, resetStudentIdVerification)

// Check if user is already logged in
onMounted(async () => {
  await authStore.checkSession()
  if (authStore.isAuthenticated) {
    router.push('/board')
  }
})
</script>

<style scoped>
/* Import Pretendard font */
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.8/dist/web/static/pretendard.css');

/* Main Container */
.registration-container {
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
  gap: 26px;
  position: absolute;
  width: 416px;
  height: 607px;
  left: 1184px;
  top: 260px;
}

/* Section Styles */
.basic-info-section, .account-info-section {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 0px;
  gap: 16px;
  width: 416px;
  flex: none;
  align-self: stretch;
  flex-grow: 0;
}

.basic-info-section {
  height: 197px;
  order: 0;
}

.account-info-section {
  height: 267px;
  order: 1;
}

.section-header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 0px;
  gap: 12px;
  width: 416px;
  flex: none;
  order: 0;
  align-self: stretch;
  flex-grow: 0;
}

.section-title {
  width: 416px;
  height: 24px;
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 600;
  font-size: 20px;
  line-height: 24px;
  letter-spacing: -0.004em;
  color: #262626;
  flex: none;
  order: 0;
  align-self: stretch;
  flex-grow: 0;
  margin: 0;
}

/* Input Section Frame */
.input-section-frame {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 0px;
  gap: 14px;
  width: 416px;
  flex: none;
  order: 1;
  align-self: stretch;
  flex-grow: 0;
}

.basic-info-section .input-section-frame {
  height: 126px;
}

.account-info-section .input-section-frame {
  height: 196px;
}

/* Input Field Styles */
.input-field {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 11px 18px;
  gap: 10px;
  width: 416px;
  height: 56px;
  background: #F8F8F8;
  border-radius: 10px;
  flex: none;
  align-self: stretch;
  flex-grow: 0;
  box-sizing: border-box;
}

.input-control {
  width: 100%;
  border: none;
  background: transparent;
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 400;
  font-size: 18px;
  line-height: 21px;
  color: #262626;
  outline: none;
}

.input-control::placeholder {
  color: #949494;
}

/* Name Verification Frame */
.name-verification-frame {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 0px;
  gap: 16px;
  width: 416px;
  height: 56px;
  flex: none;
  flex-grow: 0;
}

.name-input {
  width: 308px;
  flex: none;
  order: 0;
  flex-grow: 0;
}

/* Verification Button */
.verification-button {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  /* padding: 18px 32px; */
  gap: 10px;
  width: 92px;
  height: 56px;
  background: #FCFCFC;
  border: 1px solid #910024;
  border-radius: 10px;
  flex: none;
  order: 1;
  flex-grow: 0;
  cursor: pointer;
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 500;
  font-size: 16px;
  line-height: 19px;
  text-align: center;
  color: #910024;
  transition: all 0.2s ease;
}

.verification-button:hover:not(:disabled) {
  background: #F5F5F5;
}

.verification-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.verification-button.verified {
  background: #FFEAEC;
  border: 1px solid #910024;
  color: #910024;
}

/* Error Messages */
.error-message {
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 500;
  font-size: 16px;
  line-height: 19px;
  text-align: center;
  color: #CB385C;
  flex: none;
  flex-grow: 0;
}

.basic-error {
  width: 416px;
  height: 19px;
  order: 1;
  align-self: stretch;
}

.account-error {
  width: 416px;
  height: 19px;
  order: 1;
  align-self: stretch;
}

/* Sign Up Button */
.signup-button-frame {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  /* padding: 14px 184px; */
  padding: 14px 0px;
  gap: 10px;
  width: 416px;
  height: 50px;
  background: #910024;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  flex: none;
  order: 2;
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

.signup-button-frame:hover:not(:disabled) {
  background: #7C0019;
}

.signup-button-frame:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Login Link Text */
.login-text {
  width: 416px;
  height: 21px;
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 400;
  font-size: 18px;
  line-height: 21px;
  text-align: center;
  color: #949494;
  flex: none;
  order: 3;
  align-self: stretch;
  flex-grow: 0;
  margin: 0;
}

.login-link {
  color: #910024;
  text-decoration: none;
  font-weight: 500;
}

.login-link:hover {
  text-decoration: underline;
}

/* Responsive adjustments that maintain Figma proportions */
@media (max-width: 1600px) {
  .registration-container {
    transform: scale(0.8);
    transform-origin: top left;
  }
}

@media (max-width: 1400px) {
  .registration-container {
    transform: scale(0.7);
    transform-origin: top left;
  }
}

@media (max-width: 1200px) {
  .registration-container {
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