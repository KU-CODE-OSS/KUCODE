// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from '@/views/Dashboard.vue';
import Information from '@/views/Information.vue';
import Statistics from '@/views/Statistics.vue';

const StatisticsCourse = () => import('@/views/StatisticsComponents/StatisticsCourse.vue');
const StatisticsStudent = () => import('@/views/StatisticsComponents/StatisticsStudent.vue');
const StatisticsDepartment = () => import('@/views/StatisticsComponents/StatisticsDepartment.vue');

const InformationCourse = () => import('@/views/InformationComponents/InformationCourse.vue')
const InformationRepos   = () => import('@/views/InformationComponents/InformationRepos.vue')
const InformationStudent = () => import('@/views/InformationComponents/InformationStudent.vue')
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
    component: Information,
    children: [
      { // default path
        path: '',
        redirect: '/info/course',
      },
      {
        path: 'course',
        name: 'InformationCourse',
        component: InformationCourse,
        props: true,
      },
      {
        path: 'students',
        name: 'InformationStudent',
        component: InformationStudent,
        props: true,
      },
      {
        path: 'repos',
        name: 'InformationRepos',
        component: InformationRepos,
      },
    ]
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: Statistics,
    children: [
      { // default path
        path: '',
        redirect: '/statistics/students',
      },
      {
        path: 'course',
        name: 'StatisticsCourse',
        component: StatisticsCourse,
        props: true,
      },
      {
        path: 'students',
        name: 'StatisticsStudent',
        component: StatisticsStudent,
      },
      {
        path: 'department',
        name: 'StatisticsDepartment',
        component: StatisticsDepartment,
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

router.beforeEach((to, from, next) => {

  const defaultQueryforInformation = { page: '1', type: 'summary' };
  const defaultQueryforStatistics = { type: 'all' };
  

  if (to.name === "InformationStudent") {
    const query = { ...to.query };
    if (!query.page) {
      query.page = defaultQueryforInformation.page;
    }
    if (!query.type) {
      query.type = defaultQueryforInformation.type;
    }
    if (query.page !== to.query.page || query.type !== to.query.type) {
      next({ name: to.name, params: to.params, query: query });
    } else {
      next();
    }
  } else if (to.name === "StatisticsStudent") {
    const query = { ...to.query };
    if (!query.type) {
      query.type = defaultQueryforStatistics.type;
    }
    if (query.type !== to.query.type) {
      next({ name: to.name, params: to.params, query: query });
    } else {
      next();
    }
  } else if (to.name === "StatisticsDepartment") {
    const query = { ...to.query };
    if (!query.type) {
      query.type = defaultQueryforStatistics.type;
    }
    if (query.type !== to.query.type) {
      next({ name: to.name, params: to.params, query: query });
    } else {
      next();
    }
  }
  else {
    next();
  }
});


export default router;