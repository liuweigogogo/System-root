/**
 * Axios HTTP请求封装
 * 
 * 职责：
 * - 创建和配置axios实例
 * - 添加请求拦截器（自动添加token）
 * - 添加响应拦截器（统一错误处理）
 * - 提供统一的API调用接口
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { ElMessage } from 'element-plus'

/**
 * API响应的统一格式接口
 */
export interface ApiResponse<T = any> {
  success: boolean   // 请求是否成功
  message: string   // 响应消息
  data?: T         // 响应数据
  [key: string]: any  // 其他字段
}

/**
 * 创建axios实例
 * 
 * 配置：
 * - baseURL: API基础路径
 * - timeout: 请求超时时间
 * - headers: 默认请求头
 */
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',  // API基础路径
  timeout: 15000,  // 请求超时时间：15秒
  headers: {
    'Content-Type': 'application/json'  // 默认Content-Type
  }
})

/**
 * 请求拦截器
 * 
 * 在发送请求之前执行
 * 主要用途：
 * 1. 自动添加认证token到请求头
 * 2. 添加自定义请求头
 * 3. 请求参数处理
 */
service.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // 从localStorage获取token
    const token = localStorage.getItem('auth_token')
    
    // 如果token存在，添加到请求头
    if (token && config.headers) {
      config.headers['Authorization'] = `Bearer ${token}`
      // 或者使用Cookie方式，Flask会自动从session获取
    }
    
    // 打印请求信息（开发环境）
    if (import.meta.env.DEV) {
      console.log('发送请求:', {
        method: config.method,
        url: config.url,
        params: config.params,
        data: config.data
      })
    }
    
    return config
  },
  (error: AxiosError) => {
    // 请求错误处理
    console.error('请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器
 * 
 * 在接收响应之后执行
 * 主要用途：
 * 1. 统一处理响应数据
 * 2. 统一处理错误（网络错误、HTTP错误、业务错误）
 * 3. Token过期处理
 */
service.interceptors.response.use(
  (response: AxiosResponse) => {
    // 打印响应信息（开发环境）
    if (import.meta.env.DEV) {
      console.log('接收响应:', {
        url: response.config.url,
        status: response.status,
        data: response.data
      })
    }
    
    // 直接返回响应数据部分
    return response.data
  },
  (error: AxiosError) => {
    // 响应错误处理
    console.error('响应错误:', error)
    
    let errorMessage = '请求失败'
    
    if (error.response) {
      // 服务器返回了错误响应（状态码不是2xx）
      const { status, data } = error.response
      
      switch (status) {
        case 400:
          errorMessage = (data as any)?.message || '请求参数错误'
          break
        case 401:
          errorMessage = '未授权，请重新登录'
          // 清除token，跳转到登录页
          localStorage.removeItem('auth_token')
          // 可以在这里触发路由跳转到登录页
          // router.push('/login')
          break
        case 403:
          errorMessage = '拒绝访问'
          break
        case 404:
          errorMessage = '请求的资源不存在'
          break
        case 500:
          errorMessage = '服务器内部错误'
          break
        case 502:
          errorMessage = '网关错误'
          break
        case 503:
          errorMessage = '服务不可用'
          break
        default:
          errorMessage = (data as any)?.message || `请求失败 (${status})`
      }
    } else if (error.request) {
      // 请求已发送，但没有收到响应
      errorMessage = '网络错误，请检查您的网络连接'
    } else {
      // 请求配置出错
      errorMessage = error.message || '请求配置错误'
    }
    
    // 显示错误提示
    ElMessage.error(errorMessage)
    
    // 返回包含错误信息的Promise
    return Promise.reject({
      success: false,
      message: errorMessage,
      error: error
    })
  }
)

/**
 * 导出封装好的请求方法
 */
export default service

/**
 * GET请求
 * 
 * @param url - 请求URL
 * @param params - URL参数
 * @param config - 额外的axios配置
 */
export function get<T = any>(
  url: string,
  params?: any,
  config?: AxiosRequestConfig
): Promise<T> {
  return service.get(url, { params, ...config })
}

/**
 * POST请求
 * 
 * @param url - 请求URL
 * @param data - 请求体数据
 * @param config - 额外的axios配置
 */
export function post<T = any>(
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<T> {
  return service.post(url, data, config)
}

/**
 * PUT请求
 */
export function put<T = any>(
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<T> {
  return service.put(url, data, config)
}

/**
 * DELETE请求
 */
export function del<T = any>(
  url: string,
  params?: any,
  config?: AxiosRequestConfig
): Promise<T> {
  return service.delete(url, { params, ...config })
}

/**
 * 文件上传请求
 * 
 * @param url - 上传URL
 * @param formData - 表单数据（包含文件）
 * @param onProgress - 上传进度回调
 */
export function upload<T = any>(
  url: string,
  formData: FormData,
  onProgress?: (progress: number) => void
): Promise<T> {
  return service.post(url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(progress)
      }
    }
  })
}

/**
 * 文件下载请求
 * 
 * @param url - 下载URL
 * @param filename - 保存的文件名
 */
export function download(url: string, filename: string): Promise<void> {
  return service.get(url, {
    responseType: 'blob'  // 二进制数据
  }).then((response: any) => {
    // 创建下载链接
    const blob = new Blob([response])
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
  })
}
