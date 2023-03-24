import Entry from '@/views/Entry.vue'
import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),

  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },

  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/search',
      name: 'search',
      component: Entry
    },
    {
      path: '/browse',
      name: 'browse',
      component: Entry
    },
    {
      path: '/queue',
      name: 'queue',
      component: Entry
    },
    {
      path: '/about',
      name: 'about',
      component: Entry
    },
    {
      path: '/entries/:path+',
      name: 'entry',
      component: Entry
    },
    {
      path: '/author/:alias',
      name: 'author',
      component: Entry
    }
  ]
})

export default router
