import Albums from '/src/pages/Albums.vue'
import Album from '/src/pages/Album.vue'
import { createRouter, createWebHistory } from 'vue-router'

export default createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Albums',
      component: Albums,
      alias: '/albums',
    },
    {
      path: '/albums/:albumId',
      name: 'Album',
      component: Album,
      meta: {
        cacheKey: 'albumId',
      }
    },
    {
      path: '/albums/:albumId/items/:albumItemId',
      name: 'AlbumItem',
      component: Album,
      meta: {
        cacheKey: 'albumId',
      }
    },
  ],
})
