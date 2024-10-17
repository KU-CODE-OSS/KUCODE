<script setup>
import navigation_bar from './components/navigation_bar.vue';

</script>

<template>
  <div class="app">
    <navigation_bar></navigation_bar>
    <RouterView />
  </div>
</template>
<style>
 .app {
  background: #FFF;
 }
html, 
body {
  background: #FFF;
}
</style>