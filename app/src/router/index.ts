import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    // {
    //   path: '/search',
    //   name: 'search',
    //   component: Search
    // },
    // {
    //   path: '/browse',
    //   name: 'browse',
    //   component: Browse
    // },
    // {
    //   path: '/queue',
    //   name: 'queue',
    //   component: Queue
    // },
    // {
    //   path: '/about',
    //   name: 'about',
    //   component: About
    // }
  ]
})

export default router
