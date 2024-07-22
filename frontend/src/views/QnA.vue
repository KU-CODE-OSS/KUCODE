<template>
  <div class="default-container">
    <div class="left-split"></div>
    <div class="right-split">
      <div class="title">
        QnA
      </div>
    </div>
  </div> 
</template>

<script>
export default {
  name: 'QnA',
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
  margin-left: 320px;
  width: 268px !important;
  min-width: 268px;
  height: 100em;
  border-right: 2px solid;
  border-right-color: #DCE2ED;
}


.right-split {
  width: 100%;
  margin-right: 320px;
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
