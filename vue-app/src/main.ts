import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createState, stateSymbol } from './store';


const app = createApp(App)
app.use(router)
app.provide(stateSymbol, createState());
router.isReady().then(() => app.mount('#app'))