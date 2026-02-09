import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles/global.scss'

// Element Plus 组件和样式由 unplugin-vue-components / unplugin-auto-import 自动按需引入
// 无需手动 import ElementPlus 或全量注册图标

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
