// src/main.js
import { createApp } from 'vue'
import App from './App.vue'

// global styles & SCSS
import './styles/styles.scss'

// loading overlay
import Loading from 'vue-loading-overlay'
import 'vue-loading-overlay/dist/css/index.css';

// toast notifications
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'

const app = createApp(App)

// register loading overlay (provides this.$loading)
app.use(Loading)

// register toast (provides this.$toast)
app.use(Toast, {
  position: 'bottom-right',
  timeout: 3000
})

app.mount('#app')
