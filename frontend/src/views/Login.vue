<template>
  <div class="container">
    <div class="left-pane"></div>
    <div class="right-pane">
      <div class="header">
        <h1>고려대학교</h1>
        <h2>SW 오픈소스 플랫폼</h2>
      </div>
      <div class="login-container">
        <div class="login-box">
          <p>로그인 및 회원가입을 진행해주세요</p>
          <p>고려대학교 포털 계정을 통해 로그인하기</p>
          <button class="login-button">로그인하기</button>
          <a href="#" class="register-link">회원가입 진행하기</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login'
}
</script>

<style scoped>
.container {
  display: flex;
  height: 100vh;
}

.left-pane {
  flex: 4;
  background-color: #d3d3d3; /* Gray background */
}

.right-pane {
  flex: 6;
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: #f5f5f5;
  position: relative;
}

.header {
  position: absolute;
  top: 20px;
  left: 20px;
  text-align: left;
}

.header h1 {
  margin: 0;
  font-size: 2rem;
  color: #8b0000;
}

.header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #8b0000;
}

.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  width: 100%;
}

.login-box {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.login-box p {
  margin: 10px 0;
  font-size: 1rem;
  color: #333;
}

.login-button {
  background-color: #8b0000;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  margin-top: 20px;
}

.login-button:hover {
  background-color: #a10000;
}

.register-link {
  display: block;
  margin-top: 20px;
  color: #333;
  text-decoration: none;
}

.register-link:hover {
  text-decoration: underline;
}
</style>
