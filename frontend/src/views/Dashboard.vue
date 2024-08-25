<template>
  <div class="default-container">
    <div class="left-split"></div>
    <div class="right-split">
      <div class="title">
        게시판
      </div>
    </div>
  </div> 
</template>

<script>
export default {
  name: 'Dashboard',
}
</script>

<style scoped>
.default-container {
  /* position: relative; */
  display: flex;
  justify-content: flex-start;
  align-items: center;
  width: 100%;
  margin-top: 120px;
  height: 100vh;
  background: #FFF;
  overflow: hidden; /* Ensure no overflow issues */
}

.left-split {
  margin-left: 320px;
  width: 268px !important;
  min-width: 268px;
  height: 100vh;
  border-right: 2px solid;
  border-right-color: #DCE2ED;
}

.right-split {
  width: 100%;
  margin-right: 320px;
  height: 100vh;
  .title {
    font-size: 28px;
    font-weight: 700;
    margin-top: 57px;
    margin-left: 57px;
    min-height: 45px;
    margin-bottom: 64px;
  }
}
</style>
