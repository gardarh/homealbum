<template>
    <div class="container login-container mb-3">
      <div class="row mb-1">
        <div class="col-4">
          Username:
        </div>
        <div class="col-8">
          <input
            v-model="username"
          />
        </div>
      </div>
      <div class="row mb-1">
        <div class="col-4">
          Password:
        </div>
        <div class="col-8">
          <input
            v-model="password"
            type="password"
          />
        </div>
      </div>
      <button @click.prevent="login">Login</button>
    </div>
</template>
<script lang="ts">
import { defineComponent, ref } from 'vue'
import { useState } from '../store'
import { loginPost, systemInfoGet, userGet } from '../utils/api'
export default defineComponent({
  name: 'Login',
  components: {
  },
  setup() {
    const username = ref('')
    const password = ref('')
    const state = useState()

    const login = async () => {
      return loginPost({
        username: username.value,
        password: password.value
      }).then(() => {
        Promise.all([systemInfoGet(), userGet()]).then((response) => {
          const [systemInfo, userInfo] = response
          state.user = userInfo
          state.systemInfo = systemInfo
          return
        })
      })
    }

    return {
        username,
        password,
        login
    }
  }
})
</script>

<style scoped>
.login-container {
  width: 300px;
}
</style>