import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
// import ECharts from 'vue-echarts'
import 'echarts-gl'
import PulseLoader from 'vue-spinner/src/PulseLoader.vue'
// import echarts from 'echarts'
// import { LineChart, BarChart, ScatterChart, EffectScatterChart } from 'echarts/charts'
// import { GridComponent, TitleComponent, TooltipComponent, LegendComponent, DataZoomComponent } from 'echarts/components'
// import { UniversalTransition } from 'echarts/features'
// import { CanvasRenderer } from 'echarts/renderers'
// echarts.use([
//     CanvasRenderer,
//     TitleComponent,
//     LineChart,
//     BarChart,
//     ScatterChart,
//     GridComponent,
//     TooltipComponent,
//     EffectScatterChart,
//     UniversalTransition,
//     LegendComponent,
//     DataZoomComponent
//   ])

const app = createApp(App)
// app.component('v-chart', VueECharts)
app.component('pulse-loader', PulseLoader)
app.use(vuetify)
app.use(createPinia())
app.use(router)

app.mount('#app')
