import { createApp } from 'vue'
import App from './App.vue'
import LoadingAnimation from './components/LoadingAnimation.vue'
import Button from './components/Button.vue'
import router from './router'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'
import { createState, stateSymbol } from './store';


const app = createApp(App)
app.use(router)
app.component('LoadingAnimation', LoadingAnimation)
app.component('Button', Button)
app.provide(stateSymbol, createState());
router.isReady().then(() => app.mount('#app'))