<template>
  <div>
    <div v-if="!state.systemInfo?.is_authenticated">
      <Login />
    </div>
    <div v-else>
      Authenticated
      <router-view class="mb-3"></router-view>
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
import Login from '/src/pages/Login.vue'

export default defineComponent({
  name: 'App',
  components: {
    Login,
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
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

.version-info {
  color: #AAA;
  font-size: 11px;
}
</style>