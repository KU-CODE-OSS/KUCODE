// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from '../views/Dashboard.vue';
import Information from '../views/Information.vue';
import Statistics from '../views/Statistics.vue';
import QnA from '../views/QnA.vue'

const routes = [
  {
    path: '/board',
    name: 'board',
    component: Dashboard
  },
  {
    path: '/info',
    name: 'Information',
    component: Information
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: Statistics
  },
  {
    path: '/qna',
    name: 'QnA',
    component: QnA
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;