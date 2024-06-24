import { createApp } from 'vue'
import axios from 'axios'
import App from './App.vue'
import router from './router'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css' // icon


// 개발 서버의 주소를 설정합니다.
axios.defaults.baseURL = 'http://localhost'

const app = createApp(App)

// axios를 전역으로 설정합니다.
app.config.globalProperties.$axios = axios

// vuetify를 사용합니다.
const vuetify = createVuetify({
  components,
  directives,
  icons: { // icon
    defaultSet: 'mdi',
  },
})

// Vue 앱에 router와 vuetify를 적용하고 마운트합니다.
app.use(router).use(vuetify).mount('#app')



















/*import { createApp } from 'vue'
import axios from 'axios'
import App from './App.vue'
import router from './router'

// 개발 서버의 주소를 설정합니다.
axios.defaults.baseURL = 'http://43.155.173.127:8000'

const app = createApp(App)
app.config.globalProperties.$axios = axios
app.use(router)
app.mount('#app')


// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

const vuetify = createVuetify({
  components,
  directives,
})
// createApp(App).use(router).mount('#app')
// createApp(App).use(vuetify).mount('#app')

app.use(router).use(vuetify).mount('#app')
*/