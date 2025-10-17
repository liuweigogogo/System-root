/**
 * 认证相关API接口
 * 
 * 职责：
 * - 封装所有认证相关的HTTP请求
 * - 提供类型安全的API调用方法
 * - 统一管理API端点
 */

import { get, post } from '@/utils/request'
import type {
  LoginParams,
  RegisterParams,
  LoginResponse,
  RegisterResponse,
  CheckAuthResponse,
  CaptchaResponse
} from '@/types/auth'

/**
 * 认证API集合
 */
export const authAPI = {
  /**
   * 用户登录
   * 
   * 调用后端的/api/login接口
   * 
   * @param params - 登录参数（用户名、密码、验证码）
   * @returns Promise<LoginResponse> - 登录结果
   * 
   * 示例：
   * ```typescript
   * const result = await authAPI.login({
   *   username: 'test',
   *   password: '123456',
   *   captcha: 'abc123'
   * })
   * ```
   */
  login(params: LoginParams): Promise<LoginResponse> {
    return post<LoginResponse>('/login', params)
  },

  /**
   * 用户注册
   * 
   * 调用后端的/api/register接口
   * 
   * @param params - 注册参数（用户名、密码、邮箱）
   * @returns Promise<RegisterResponse> - 注册结果
   */
  register(params: RegisterParams): Promise<RegisterResponse> {
    return post<RegisterResponse>('/register', params)
  },

  /**
   * 用户登出
   * 
   * 调用后端的/api/logout接口
   * 清除服务器端的会话信息
   * 
   * @returns Promise<{ success: boolean, message: string }>
   */
  logout(): Promise<{ success: boolean, message: string }> {
    return post('/logout')
  },

  /**
   * 检查认证状态
   * 
   * 调用后端的/api/check-auth接口
   * 验证当前会话是否有效
   * 
   * @returns Promise<CheckAuthResponse> - 认证状态
   * 
   * 使用场景：
   * - 应用启动时检查用户是否已登录
   * - 页面刷新后恢复登录状态
   * - 定期验证会话是否过期
   */
  checkAuth(): Promise<CheckAuthResponse> {
    return get<CheckAuthResponse>('/check-auth')
  },

  /**
   * 获取验证码
   * 
   * 调用后端的/api/captcha接口
   * 获取登录所需的验证码
   * 
   * @returns Promise<CaptchaResponse> - 验证码数据
   */
  getCaptcha(): Promise<CaptchaResponse> {
    return get<CaptchaResponse>('/captcha')
  }
}
