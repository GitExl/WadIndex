import '@/assets/scss/base.scss';

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(router)

app.config.globalProperties.$filters = {
  truncate: function (text: string, stop: number, clamp: number) {
    return text.slice(0, stop) + (stop < text.length ? clamp || '&hellip;' : '')
  }
}

app.mount('#app')
