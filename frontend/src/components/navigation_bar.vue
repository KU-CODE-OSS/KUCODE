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
  </div>
</template>

<script>
  export default {
    data() {
      return {
        isBold: false,
      };
    },
  };
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
  justify-content: flex-start; /* Center the logo and navigation */
  align-items: center;
  width: 1920px;
  height: 120px;
  /* padding-left: 320px; */
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
  width: 100%;
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
</style>
