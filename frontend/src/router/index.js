// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from '@/views/Dashboard.vue';
import Information from '@/views/Information.vue';
import Statistics from '@/views/Statistics.vue';
import StatisticsTotal from '@/views/StatisticsComponents/StatisticsTotal.vue';
import StatisticsCourse from '@/views/StatisticsComponents/StatisticsCourse.vue';
import StatisticsDepartment from '@/views/StatisticsComponents/StatisticsDepartment.vue';
import InformationCourse from '@/views/InformationComponents/InformationCourse.vue'
import InformationRepos from '@/views/InformationComponents/InformationRepos.vue'
import InformationStudent from '@/views/InformationComponents/InformationStudent.vue'
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
        redirect: '/statistics/total',
      },
      {
        path: 'total',
        name: 'StatisticsTotal',
        component: StatisticsTotal,
        props: true,
      },
      {
        path: 'course',
        name: 'StatisticsCourse',
        component: StatisticsCourse,
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

  const defaultQuery = { page: '1', type: 'summary' };

  if (to.name === "InformationStudent") {
    const query = { ...to.query };
    if (!query.page) {
      query.page = defaultQuery.page;
    }
    if (!query.type) {
      query.type = defaultQuery.type;
    }
    if (query.page !== to.query.page || query.type !== to.query.type) {
      next({ name: to.name, params: to.params, query: query });
    } else {
      next();
    }
  } else {
    next();
  }
});


export default router;