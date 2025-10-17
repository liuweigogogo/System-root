/**
 * 文件转换相关的TypeScript类型定义
 */

/**
 * 支持的转换格式接口
 */
export interface ConversionType {
  from: string           // 源格式
  to: string            // 目标格式
  description: string   // 描述
}

/**
 * 支持的转换格式列表响应
 */
export interface SupportedConversionsResponse {
  success: boolean
  conversions: Record<string, ConversionType>  // 转换类型映射
}

/**
 * 文件转换参数接口
 */
export interface ConvertFileParams {
  file: File              // 要转换的文件
  target_format: string   // 目标格式
}

/**
 * 文件转换响应接口
 */
export interface ConvertFileResponse {
  success: boolean              // 是否成功
  message: string              // 响应消息
  output_path?: string         // 输出文件路径
  conversion_type?: string     // 转换类型
  download_url?: string        // 下载URL
  error_code?: string          // 错误代码
}

/**
 * 批量转换参数接口
 */
export interface BatchConvertParams {
  files: File[]           // 文件列表
  target_format: string   // 目标格式
}

/**
 * 批量转换响应接口
 */
export interface BatchConvertResponse {
  success_count: number           // 成功数量
  failed_count: number            // 失败数量
  total_files: number             // 总文件数
  results: Array<{                // 每个文件的转换结果
    file: string
    result: ConvertFileResponse
  }>
}

/**
 * 文件信息接口
 */
export interface FileInfo {
  success: boolean
  file_name?: string                  // 文件名
  file_size?: number                  // 文件大小（字节）
  file_extension?: string             // 文件扩展名
  modified_time?: number              // 修改时间（时间戳）
  supported_conversions?: string[]    // 支持的转换类型
  message?: string                    // 错误消息
}
