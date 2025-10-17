/**
 * Vue应用入口文件
 * 
 * 职责：
 * - 创建Vue应用实例
 * - 注册全局插件（路由、状态管理、UI组件库）
 * - 挂载应用到DOM
 */

import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'

// 创建Vue应用实例
const app = createApp(App)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 注册插件
app.use(createPinia())  // 状态管理
app.use(router)  // 路由
app.use(ElementPlus)  // UI组件库

// 挂载应用
app.mount('#app')
