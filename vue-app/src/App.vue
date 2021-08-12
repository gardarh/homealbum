<template>
  <div>
    <LoadingAnimation v-if="!state.systemInfo" />
    <div v-else-if="!state.systemInfo?.is_authenticated">
      <Login />
    </div>
    <div v-else class="mb-3">
      <router-view v-slot="{ Component, route }">
        <keep-alive include="album">
          <component
            :is="Component"
            :key="route.meta.cacheKey ? route.params[route.meta.cacheKey] : undefined"
          />
        </keep-alive>
      </router-view>
    </div>
    <div v-if="state.systemInfo" class="version-info">
      Version: {{ state.systemInfo.version }}
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useState } from './store'
import { systemInfoGet, userGet } from './utils/api'
import Album from '/src/pages/Album.vue'
import Login from '/src/pages/Login.vue'

export default defineComponent({
  name: 'App',
  components: {
    Login,
    Album,
  },
  setup() {
    const state = useState()
    systemInfoGet().then(result => {
      state.systemInfo = result
      if(result.is_authenticated) {
        userGet().then(result => {
          state.user = result
        })
      }
    })
    return {
      state
    }
  },
})
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin-top: 20px;
  padding-left: 5px;
  padding-right: 5px;
}

html {
  scroll-behavior: auto !important;
}

.version-info {
  text-align: center;
  color: #AAA;
  font-size: 11px;
}
</style>