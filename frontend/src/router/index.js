// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from '@/views/Dashboard.vue';
import Information from '@/views/Information.vue';
import Statistics from '@/views/Statistics.vue';
import Login from '@/views/Login.vue';
import Register from '@/views/Register.vue';
import EmailVerification from '@/views/EmailVerification.vue';
import EProfile from '@/views/EProfile.vue';
import { authGuard, guestGuard } from './guards'

const StatisticsCourse = () => import('@/views/StatisticsComponents/StatisticsCourse.vue');
const StatisticsStudent = () => import('@/views/StatisticsComponents/StatisticsStudent.vue');
const StatisticsDepartment = () => import('@/views/StatisticsComponents/StatisticsDepartment.vue');

const InformationCourse = () => import('@/views/InformationComponents/InformationCourse.vue')
const InformationRepos   = () => import('@/views/InformationComponents/InformationRepos.vue')
const InformationStudent = () => import('@/views/InformationComponents/InformationStudent.vue')
import QnA from '../views/QnA.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'login',
    component: Login,
    // beforeEnter: guestGuard
  },
  {
    path: '/register',
    name: 'register',
    component: Register,
    // beforeEnter: guestGuard
  },
  {
    path: '/emailVerification',
    name: 'emailVerification',
    component: EmailVerification,
    // beforeEnter: guestGuard
  },
  {
    path: '/board',
    name: 'board',
    component: Dashboard,
    beforeEnter: authGuard
  },
  {
    path: '/info',
    name: 'Information',
    component: Information,
    beforeEnter: authGuard,
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
  },
  {
    path: '/eprofile',
    name: 'EProfile',
    component: EProfile,
    //beforeEnter: guestGuard,
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