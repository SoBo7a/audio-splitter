// src/main.js
import { createApp } from 'vue'
import App from './App.vue'

// global styles & SCSS
import './styles/styles.scss'

// loading overlay
import 'vue-loading-overlay/dist/css/index.css';

// toast notifications
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'

const app = createApp(App)

// register toast (provides this.$toast)
app.use(Toast, {
  position: 'bottom-right',
  timeout: 3000
})

app.config.globalProperties.$backend = process.env.VUE_APP_BACKEND_URL

app.mount('#app')
