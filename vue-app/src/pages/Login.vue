<template>
    <div class="container login-container mb-3">
      <LoadingAnimation v-if="isLoginPending" />
      <div v-else>
        <form @submit.prevent="login">
          <Message v-if="isLoginError" variant="error" class="mb-2">Login failed</Message>
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
        </form>
      </div>
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
    const isLoginError = ref(false)
    const isLoginPending = ref(false)
    const state = useState()

    const login = async () => {
      isLoginPending.value = true
      return loginPost({
        username: username.value,
        password: password.value
      }).then((response) => {
        if(response.ok === true) {
          Promise.all([systemInfoGet(), userGet()]).then((response) => {
            const [systemInfo, userInfo] = response
            state.user = userInfo
            state.systemInfo = systemInfo
          })
        } else {
          isLoginError.value = true
          isLoginPending.value = false
        }
      })
    }

    return {
        username,
        password,
        login,
        isLoginError,
        isLoginPending,
    }
  }
})
</script>

<style scoped>
.login-container {
  width: 300px;
}
</style>