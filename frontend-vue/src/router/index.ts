/**
 * Vue Router路由配置
 * 
 * 职责：
 * - 定义应用的所有路由规则
 * - 配置路由守卫（认证检查）
 * - 管理页面导航
 */

import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/store/auth'

/**
 * 路由配置列表
 * 
 * 每个路由对象包含：
 * - path: URL路径
 * - name: 路由名称（用于编程式导航）
 * - component: 对应的Vue组件
 * - meta: 元信息（如是否需要认证）
 */
const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/login'  // 根路径重定向到登录页
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),  // 懒加载组件
    meta: { 
      requiresAuth: false,  // 不需要认证
      title: '用户登录' 
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),  // 懒加载组件
    meta: { 
      requiresAuth: false,
      title: '用户注册' 
    }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),  // 懒加载组件
    meta: { 
      requiresAuth: true,  // 需要登录后才能访问
      title: '仪表板' 
    }
  },
  {
    path: '/converter',
    name: 'FileConverter',
    component: () => import('@/views/FileConverter.vue'),  // 懒加载组件
    meta: { 
      requiresAuth: true,
      title: '文件转换' 
    }
  },
  {
    path: '/logs',
    name: 'Logs',
    component: () => import('@/views/Logs.vue'),  // 懒加载组件
    meta: { 
      requiresAuth: true,
      title: '日志管理' 
    }
  },
  {
    // 404页面
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { 
      requiresAuth: false,
      title: '页面不存在' 
    }
  }
]

/**
 * 创建路由实例
 * 
 * - history模式：使用HTML5 History API，URL没有#号
 * - routes：路由配置列表
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

/**
 * 全局前置守卫
 * 
 * 在每次路由跳转之前执行
 * 主要用途：
 * 1. 检查用户认证状态
 * 2. 根据路由元信息决定是否允许访问
 * 3. 更新页面标题
 */
router.beforeEach(async (to, from, next) => {
  // 获取认证状态管理器
  const authStore = useAuthStore()
  
  // 更新页面标题
  document.title = `${to.meta.title || '文件转换系统'} - 文件转换系统`
  
  // 检查路由是否需要认证
  if (to.meta.requiresAuth) {
    // 如果需要认证但用户未登录
    if (!authStore.isAuthenticated) {
      // 尝试验证现有会话
      await authStore.checkAuth()
      
      // 验证后仍未登录，重定向到登录页
      if (!authStore.isAuthenticated) {
        next({
          name: 'Login',
          query: { redirect: to.fullPath }  // 保存目标路径，登录后跳转
        })
        return
      }
    }
  } else {
    // 如果已登录用户访问登录/注册页，重定向到仪表板
    if (authStore.isAuthenticated && (to.name === 'Login' || to.name === 'Register')) {
      next({ name: 'Dashboard' })
      return
    }
  }
  
  // 允许导航
  next()
})

/**
 * 全局后置钩子
 * 
 * 在路由跳转完成后执行
 * 可以用于页面浏览记录、埋点统计等
 */
router.afterEach((to, from) => {
  // 这里可以添加页面访问统计等逻辑
  console.log(`导航完成: ${from.path} -> ${to.path}`)
})

export default router
