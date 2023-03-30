import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import '@material-design-icons/font/outlined.scss';
import 'keen-slider/keen-slider.scss';

import '@/assets/scss/base.scss';

const app = createApp(App)

app.use(router)

app.config.globalProperties.$filters = {
  truncate: function (text: string, stop: number, clamp: number) {
    return text.slice(0, stop) + (stop < text.length ? clamp || '&hellip;' : '')
  }
}

app.mount('#app')
