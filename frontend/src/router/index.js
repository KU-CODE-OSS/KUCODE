// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from '@/views/Dashboard.vue';
import Information from '@/views/Information.vue';
import Statistics from '@/views/Statistics.vue';
import StatisticsCourse from '@/views/StatisticsComponents/StatisticsCourse.vue';
import StatisticsStudent from '@/views/StatisticsComponents/StatisticsStudent.vue'
import StatisticsRepos from '@/views/StatisticsComponents/StatisticsRepos.vue'
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
    component: Statistics,
    children: [
      { // default path
        path: '',
        name: 'default',
        redirect: '/statistics/course',
      },
      {
        path: 'course',
        name: 'StatisticsCourse',
        component: StatisticsCourse,
      },
      {
        path: 'students',
        name: 'StatisticsStudent',
        component: StatisticsStudent,
      },
      {
        path: 'repos',
        name: 'StatisticsRepos',
        component: StatisticsRepos,
      },
    ]
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