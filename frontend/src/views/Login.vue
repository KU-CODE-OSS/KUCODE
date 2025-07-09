<template>
  <div class="login-container">
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
      <!-- Welcome Section Frame -->
      <div class="welcome-frame">
        <h1 class="main-title">오픈소스 소프트웨어 플랫폼 방문을 환영합니다</h1>
        <p class="subtitle">고려대학교 포털 계정을 통해 로그인을 해주세요</p>
      </div>
      
      <!-- Login Form Container Frame -->
      <div class="form-container-frame">
        <!-- Form Wrapper Frame -->
        <div class="form-wrapper-frame">
          <!-- Input Section Frame -->
          <div class="input-section-frame">
            <div class="input-field">
              <input 
                type="text" 
                v-model="username"
                placeholder="아이디"
                class="input-control"
              />
            </div>
            <div class="input-field">
              <input 
                type="password" 
                v-model="password"
                placeholder="비밀번호"
                class="input-control"
              />
            </div>
          </div>
          
          <!-- Login Button Frame -->
          <button 
            @click="handleLogin"
            :disabled="loading"
            class="login-button-frame"
          >
            {{ loading ? '로그인 중...' : '로그인 (Login)' }}
          </button>
        </div>
        
        <!-- Error Message - positioned exactly as Figma -->
        <div 
          v-if="errorMessage" 
          class="error-message"
        >
          {{ errorMessage }}
        </div>
        
        <!-- Sign Up Text -->
        <div class="signup-text">
          등록된 계정이 없다면 
          <router-link to="/register" class="signup-link">
            계정 만들기 (Sign up)
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

// Form data
const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

// Router
const router = useRouter()

// Handle login
const handleLogin = async () => {
  try {
    loading.value = true
    errorMessage.value = ''
    
    // Check if email contains @korea.ac.kr
    if (username.value && !username.value.includes('@korea.ac.kr')) {
      errorMessage.value = '사용 가능한 @korea.ac.kr 이메일을 입력해주세요'
      return
    }
    
    // Simulate login API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Demo validation - you can replace with real authentication
    if (username.value === 'admin@korea.ac.kr' && password.value === 'password') {
      router.push('/dashboard')
    } else {
      errorMessage.value = '이메일/비밀번호가 일치하지 않습니다'
    }
  } catch (error) {
    errorMessage.value = '이메일/비밀번호가 일치하지 않습니다'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Import Pretendard font */
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.8/dist/web/static/pretendard.css');

/* Main Container - matches Figma dimensions but accounts for navigation */
.login-container {
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

/* Logo placeholder - simplified but maintains colors */
.logo-placeholder {
  width: 100%;
  height: 100%;
  background: #7C0019;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  /* color: #D7C9B1;
  font-weight: 600;
  font-size: 10px;
  text-align: center; */
  background: url('/login_logo.png') no-repeat center center;
}

/* .logo-placeholder::after {
  content: "KOREA UNIVERSITY";
} */

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
  height: 394px;
  left: 1184px;
  top: 308px;
}

/* Welcome Frame - exact Figma specs */
.welcome-frame {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 0px;
  gap: 10px;
  width: 416px;
  height: 57px;
  flex: none;
  order: 0;
  align-self: stretch;
  flex-grow: 0;
}

.main-title {
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

.subtitle {
  width: 416px;
  height: 21px;
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

/* Form Container Frame - exact Figma specs */
.form-container-frame {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 0px;
  gap: 80px;
  isolation: isolate;
  width: 416px;
  height: 297px;
  flex: none;
  order: 1;
  align-self: stretch;
  flex-grow: 0;
}

.form-wrapper-frame {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 0px;
  gap: 20px;
  width: 416px;
  height: 196px;
  flex: none;
  order: 0;
  align-self: stretch;
  flex-grow: 0;
  z-index: 0;
}

/* Input Section Frame - exact Figma specs */
.input-section-frame {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 0px;
  gap: 14px;
  width: 416px;
  height: 126px;
  flex: none;
  order: 0;
  align-self: stretch;
  flex-grow: 0;
}

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

/* Login Button Frame - exact Figma specs */
.login-button-frame {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  padding: 14px 184px;
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

.login-button-frame:hover:not(:disabled) {
  background: #7C0019;
}

.login-button-frame:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Error Message - exact Figma positioning */
.error-message {
  position: absolute;
  width: 235px;
  height: 19px;
  left: 91px;
  top: 214px;
  font-family: 'Pretendard';
  font-style: normal;
  font-weight: 500;
  font-size: 16px;
  line-height: 19px;
  text-align: center;
  color: #CB385C;
  flex: none;
  order: 1;
  flex-grow: 0;
  z-index: 1;
}

/* Sign Up Text - exact Figma specs */
.signup-text {
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
  order: 2;
  align-self: stretch;
  flex-grow: 0;
  z-index: 2;
  margin: 0;
}

.signup-link {
  color: #910024;
  text-decoration: none;
  font-weight: 500;
}

.signup-link:hover {
  text-decoration: underline;
}

/* Responsive adjustments that maintain Figma proportions */
@media (max-width: 1600px) {
  .login-container {
    transform: scale(0.8);
    transform-origin: top left;
  }
}

@media (max-width: 1400px) {
  .login-container {
    transform: scale(0.7);
    transform-origin: top left;
  }
}

@media (max-width: 1200px) {
  .login-container {
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