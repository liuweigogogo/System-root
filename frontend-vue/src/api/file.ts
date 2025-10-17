/**
 * 文件转换相关API接口
 * 
 * 职责：
 * - 封装文件转换相关的HTTP请求
 * - 处理文件上传和下载
 * - 提供类型安全的API调用方法
 */

import { get, post, upload, download } from '@/utils/request'
import type {
  SupportedConversionsResponse,
  ConvertFileResponse,
  BatchConvertResponse,
  FileInfo
} from '@/types/file'

/**
 * 文件转换API集合
 */
export const fileAPI = {
  /**
   * 获取支持的转换格式
   * 
   * 调用后端的/api/convert/supported接口
   * 获取系统支持的所有文件转换类型
   * 
   * @returns Promise<SupportedConversionsResponse> - 支持的转换格式列表
   */
  getSupportedConversions(): Promise<SupportedConversionsResponse> {
    return get<SupportedConversionsResponse>('/convert/supported')
  },

  /**
   * 单文件转换
   * 
   * 调用后端的/api/convert/single接口
   * 上传文件并进行格式转换
   * 
   * @param file - 要转换的文件
   * @param targetFormat - 目标格式（如'pdf', 'docx'等）
   * @param onProgress - 上传进度回调函数
   * @returns Promise<ConvertFileResponse> - 转换结果
   * 
   * 示例：
   * ```typescript
   * const result = await fileAPI.convertFile(
   *   file,
   *   'pdf',
   *   (progress) => console.log(`上传进度: ${progress}%`)
   * )
   * ```
   */
  convertFile(
    file: File,
    targetFormat: string,
    onProgress?: (progress: number) => void
  ): Promise<ConvertFileResponse> {
    // 创建FormData对象
    const formData = new FormData()
    formData.append('file', file)
    formData.append('target_format', targetFormat)
    
    // 使用upload方法上传文件
    return upload<ConvertFileResponse>('/convert/single', formData, onProgress)
  },

  /**
   * 批量文件转换
   * 
   * 调用后端的/api/convert/batch接口
   * 批量上传文件并转换为指定格式
   * 
   * @param files - 文件列表
   * @param targetFormat - 目标格式
   * @param onProgress - 上传进度回调函数
   * @returns Promise<BatchConvertResponse> - 批量转换结果
   */
  batchConvert(
    files: File[],
    targetFormat: string,
    onProgress?: (progress: number) => void
  ): Promise<BatchConvertResponse> {
    // 创建FormData对象
    const formData = new FormData()
    
    // 添加所有文件
    files.forEach((file, index) => {
      formData.append(`files`, file)  // 注意：键名为'files'，支持多个文件
    })
    
    formData.append('target_format', targetFormat)
    
    // 使用upload方法上传文件
    return upload<BatchConvertResponse>('/convert/batch', formData, onProgress)
  },

  /**
   * 获取文件信息
   * 
   * 调用后端的/api/convert/info接口
   * 获取文件的详细信息和支持的转换类型
   * 
   * @param file - 文件对象
   * @returns Promise<FileInfo> - 文件信息
   */
  getFileInfo(file: File): Promise<FileInfo> {
    const formData = new FormData()
    formData.append('file', file)
    
    return post<FileInfo>('/convert/info', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  /**
   * 下载转换后的文件
   * 
   * 调用后端的/api/convert/download/{filename}接口
   * 下载转换完成的文件
   * 
   * @param filename - 文件名（服务器返回的）
   * @param saveAsFilename - 保存到本地的文件名
   * @returns Promise<void>
   */
  downloadFile(filename: string, saveAsFilename?: string): Promise<void> {
    const url = `/convert/download/${encodeURIComponent(filename)}`
    return download(url, saveAsFilename || filename)
  },

  /**
   * 清理临时文件
   * 
   * 调用后端的/api/convert/cleanup接口
   * 清理服务器上的临时转换文件
   * 
   * @returns Promise<{ success: boolean, message: string }>
   */
  cleanupTempFiles(): Promise<{ success: boolean, message: string }> {
    return post('/convert/cleanup')
  }
}
