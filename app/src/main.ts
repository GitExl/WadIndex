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

app.mount('#app')
