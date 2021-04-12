<template>
    <div>
      <div class="row">
        <div class="col-12">
          <input
            v-model="username"
          />
        </div>
      </div>
      <div class="row">
        <div class="col-12">
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