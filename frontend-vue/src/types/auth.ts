/**
 * 认证相关的TypeScript类型定义
 * 
 * 职责：
 * - 定义用户信息接口
 * - 定义登录/注册参数接口
 * - 定义API响应接口
 * 
 * 使用TypeScript类型系统提供编译时类型检查和IDE智能提示
 */

/**
 * 用户信息接口
 * 
 * 描述用户的基本信息
 */
export interface UserInfo {
  user_id: number          // 用户ID
  username: string         // 用户名
  email?: string          // 邮箱（可选）
  created_at?: string     // 创建时间（可选）
  last_login?: string     // 最后登录时间（可选）
}

/**
 * 登录参数接口
 * 
 * 描述登录API所需的参数
 */
export interface LoginParams {
  username: string   // 用户名
  password: string   // 密码
  captcha: string    // 验证码
}

/**
 * 注册参数接口
 * 
 * 描述注册API所需的参数
 */
export interface RegisterParams {
  username: string   // 用户名
  password: string   // 密码
  email?: string     // 邮箱（可选）
}

/**
 * 登录响应接口
 * 
 * 描述登录API的响应数据结构
 */
export interface LoginResponse {
  success: boolean           // 是否成功
  message: string           // 响应消息
  session_token?: string    // 会话令牌（成功时返回）
  redirect_url?: string     // 重定向URL（成功时返回）
}

/**
 * 注册响应接口
 */
export interface RegisterResponse {
  success: boolean   // 是否成功
  message: string   // 响应消息
}

/**
 * 认证检查响应接口
 */
export interface CheckAuthResponse {
  authenticated: boolean   // 是否已认证
  user_id?: number        // 用户ID（已认证时返回）
  message?: string        // 消息
}

/**
 * 验证码响应接口
 */
export interface CaptchaResponse {
  success: boolean   // 是否成功
  captcha: string   // 验证码文本或图片数据
  message: string   // 消息
}
