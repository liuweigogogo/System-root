/**
 * 用户认证状态管理
 * 
 * 使用Pinia进行状态管理
 * 
 * 职责：
 * - 管理用户登录状态
 * - 存储用户信息
 * - 提供登录、登出、注册等方法
 * - 会话验证
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api/auth'
import type { UserInfo, LoginParams, RegisterParams } from '@/types/auth'

/**
 * 定义认证状态管理store
 * 
 * 使用Composition API风格（推荐）
 */
export const useAuthStore = defineStore('auth', () => {
  // ==================== 状态定义 ====================
  
  /**
   * 用户信息
   * 包含用户ID、用户名、邮箱等信息
   */
  const userInfo = ref<UserInfo | null>(null)
  
  /**
   * 认证令牌（会话令牌）
   * 存储在localStorage中，用于API请求认证
   */
  const token = ref<string>(localStorage.getItem('auth_token') || '')
  
  /**
   * 加载状态
   * 用于显示加载动画
   */
  const loading = ref<boolean>(false)
  
  // ==================== 计算属性 ====================
  
  /**
   * 是否已认证
   * 根据token和userInfo判断用户是否已登录
   */
  const isAuthenticated = computed(() => {
    return !!token.value && !!userInfo.value
  })
  
  /**
   * 用户ID
   * 快捷访问用户ID
   */
  const userId = computed(() => {
    return userInfo.value?.user_id || null
  })
  
  /**
   * 用户名
   * 快捷访问用户名
   */
  const username = computed(() => {
    return userInfo.value?.username || ''
  })
  
  // ==================== 方法定义 ====================
  
  /**
   * 用户登录
   * 
   * 流程：
   * 1. 调用登录API
   * 2. 存储token和用户信息
   * 3. 更新localStorage
   * 
   * @param params - 登录参数（用户名、密码、验证码）
   * @returns Promise<boolean> - 登录是否成功
   */
  const login = async (params: LoginParams): Promise<boolean> => {
    loading.value = true
    
    try {
      // 调用登录API
      const response = await authAPI.login(params)
      
      if (response.success) {
        // 登录成功，存储token（实际项目中应该从响应中获取）
        const sessionToken = response.session_token || 'dummy_token'
        token.value = sessionToken
        
        // 存储到localStorage，实现持久化
        localStorage.setItem('auth_token', sessionToken)
        
        // 获取用户信息
        await getUserInfo()
        
        return true
      } else {
        return false
      }
    } catch (error) {
      console.error('登录失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 用户注册
   * 
   * @param params - 注册参数（用户名、密码、邮箱）
   * @returns Promise<{ success: boolean, message: string }>
   */
  const register = async (params: RegisterParams): Promise<{ success: boolean, message: string }> => {
    loading.value = true
    
    try {
      // 调用注册API
      const response = await authAPI.register(params)
      
      return {
        success: response.success,
        message: response.message
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.message || '注册失败'
      }
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 用户登出
   * 
   * 流程：
   * 1. 调用登出API
   * 2. 清除本地存储的token和用户信息
   * 3. 清除localStorage
   */
  const logout = async (): Promise<void> => {
    try {
      // 调用登出API
      await authAPI.logout()
    } catch (error) {
      console.error('登出API调用失败:', error)
    } finally {
      // 无论API调用是否成功，都清除本地状态
      token.value = ''
      userInfo.value = null
      localStorage.removeItem('auth_token')
    }
  }
  
  /**
   * 检查认证状态
   * 
   * 用于页面刷新或应用启动时验证会话是否有效
   * 
   * @returns Promise<boolean> - 会话是否有效
   */
  const checkAuth = async (): Promise<boolean> => {
    // 如果没有token，直接返回false
    if (!token.value) {
      return false
    }
    
    try {
      // 调用认证检查API
      const response = await authAPI.checkAuth()
      
      if (response.authenticated) {
        // 会话有效，获取用户信息
        await getUserInfo()
        return true
      } else {
        // 会话无效，清除本地状态
        token.value = ''
        userInfo.value = null
        localStorage.removeItem('auth_token')
        return false
      }
    } catch (error) {
      console.error('认证检查失败:', error)
      // 出错时清除状态
      token.value = ''
      userInfo.value = null
      localStorage.removeItem('auth_token')
      return false
    }
  }
  
  /**
   * 获取用户信息
   * 
   * 登录成功后调用，获取用户详细信息
   */
  const getUserInfo = async (): Promise<void> => {
    try {
      // 这里应该调用获取用户信息的API
      // 暂时使用模拟数据
      userInfo.value = {
        user_id: 1,
        username: 'test_user',
        email: 'test@example.com'
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }
  
  /**
   * 更新用户信息
   * 
   * @param info - 新的用户信息
   */
  const updateUserInfo = (info: Partial<UserInfo>): void => {
    if (userInfo.value) {
      userInfo.value = {
        ...userInfo.value,
        ...info
      }
    }
  }
  
  // ==================== 返回暴露的状态和方法 ====================
  
  return {
    // 状态
    userInfo,
    token,
    loading,
    
    // 计算属性
    isAuthenticated,
    userId,
    username,
    
    // 方法
    login,
    register,
    logout,
    checkAuth,
    getUserInfo,
    updateUserInfo
  }
})
