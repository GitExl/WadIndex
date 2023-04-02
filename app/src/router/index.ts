import Entry from '@/views/Entry.vue'
import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const router = createRouter({
  history: createWebHistory(),

  scrollBehavior(to, from, savedPosition) {
    if (to.path === from.path && to.hash !== from.hash) {
      return { selector: to.hash };
    }

    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
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
      path: '/entries/:path(.*)',
      name: 'entry',
      component: Entry,
    },
    {
      path: '/author/:alias',
      name: 'author',
      component: Entry
    },
    {
      path: '/music/:hash',
      name: 'music',
      component: Entry
    },
    {
      path: '/map/:path(.*)',
      name: 'map',
      component: Entry
    }
  ]
})

export default router
