import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'

// import { useAuth } from '@/composables/useAuth'

// import PulseLoader from 'vue-spinner/src/PulseLoader.vue'


const app = createApp(App)
// app.component('pulse-loader', PulseLoader)

// const { initializeAuth } = useAuth()
// initializeAuth()

app.use(vuetify)
app.use(createPinia())
app.use(router)

app.mount('#app')
