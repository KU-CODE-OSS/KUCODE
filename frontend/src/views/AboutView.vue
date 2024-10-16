<template>
  <div class="about">
    <h1>This is an about page {{ response }}</h1>
  </div>
  <div>
    <h1>Welcome to the Home Page {{ response }}</h1>
    <p v-if="response">{{ response }}</p>
    <p v-if="error" style="color: red;">{{ error }}</p>
  </div> 
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getHealthCheck } from '@/api';  // api.js에서 함수를 import 합니다.

const response = ref(null);
const error = ref(null);

async function updateDraft() {
  try {
    const result = await getHealthCheck();
    console.log(result.data)
    response.value = 'Draft updated successfully: ' + JSON.stringify(result.data.status);
    error.value = null;
  } catch (err) {
    error.value = 'Failed to update draft: ' + err.message;
  }
}
// onMounted 훅에서 초기 데이터 로딩 함수 호출
onMounted(() => {
  updateDraft();
});
</script>

<style>
@media (min-width: 1024px) {
  .about {
    min-height: 100vh; 
    display: flex;
    align-items: center;
  }
}
</style>
