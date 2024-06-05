import { createWebHistory, createRouter } from "vue-router"
// import AppView from './App.vue'
import MainView from './main.vue'
import DashBoard from './dashboard.vue'
import Login from './login.vue';
import dash_stats from './dash_stats.vue';


const routes = [
  {    path: "/",    component: MainView  },
  {    path: "/dashboard",    component: DashBoard  },
  {    path: "/login",    component: Login  },
  {    path: "/dashboard/stats",    component: dash_stats  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router; 