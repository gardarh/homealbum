import Albums from '/src/pages/Albums.vue'
import { createRouter, createWebHistory } from 'vue-router'

export default createRouter({
  history: createWebHistory(),
  routes: [
    {
        path: '/',
        name: 'Albums',
        component: Albums,
        meta: {
          title: 'pagetitle_albums',
        },
      },
  ],
})
