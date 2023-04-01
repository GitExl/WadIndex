import '@/assets/scss/base.scss';

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { pageTitle } from 'vue-page-title';

const app = createApp(App)

app.use(router)

app.use(
  pageTitle({
    suffix: 'The Wad Index',
    separator: ' - ',
  })
);

app.config.globalProperties.$filters = {
  truncate: function (text: string, stop: number, clamp: number) {
    return text.slice(0, stop) + (stop < text.length ? clamp || '&hellip;' : '')
  }
}

app.mount('#app')
