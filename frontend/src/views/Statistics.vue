<template>
  <div class="default-container">
    <div class="left-split">
      <div class="empty-box"></div>
      <div class="filter-box">
        <div class="filter-title-box">
          <div class="title">필터</div>
          <v-btn class="init">Button</v-btn>
        </div>
      </div>
    </div>
    <div class="right-split" density="comfortable" rounded></div>
  </div> 
</template>

<script>
export default {
  name: 'Statistics',
}
</script>

<style scoped>
.default-container {
  display: flex;
  width: 100vw;
  height: calc(100rem - 100px);
  background: var(--White, #FCFCFC);
  overflow: hidden; /* Ensure no overflow issues */
}
.default-container {
  display: flex;
  width: 100vw;
  height: calc(100rem - 100px);
  background: var(--White, #FCFCFC);
  overflow: hidden; /* Ensure no overflow issues */
}

.left-split {
  margin-left: 220px;
  width: 400px !important;
  min-width: 400px;
  height: 100em;
  border-right: 2px solid;
  border-right-color: #DCE2ED;
  .empty-box {
    width: 100em;
    margin-bottom: 166px;
  }
  .filter-box {
    height: 100%;
    .filter-title-box {
      height: 40px;
      display: flex;
      flex-wrap: nowrap;
      .title {
        font-size: 22px;
        font-weight: 600;
        
      }
      .init {
        margin-left: auto;
        margin-right: 15px;
      }
    }
  }
}

.right-split {
  width: 100%;
  margin-right: 320px;
}


</style>
