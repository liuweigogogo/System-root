"""
文件转换控制器
处理文件格式转换相关的HTTP请求
"""

import os
import tempfile
from flask import request, jsonify, send_file
from typing import Dict, Any, Tuple
from werkzeug.utils import secure_filename
from services.FileConverterService import FileConverterService
from config.LoggerConfig import log_info, log_error, log_access

class FileConverterController:
    """文件转换控制器类"""
    
    def __init__(self):
        """初始化文件转换控制器"""
        self.converter_service = FileConverterService()
        # 允许的文件上传目录
        self.upload_folder = os.path.join(tempfile.gettempdir(), 'file_converter_uploads')
        # 确保上传目录存在
        os.makedirs(self.upload_folder, exist_ok=True)
        # 允许的文件扩展名
        self.allowed_extensions = {
            'docx', 'pdf', 'pptx', 'xlsx', 'csv', 'json',
            'jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp'
        }
    
    def get_supported_conversions(self) -> Tuple[Dict[str, Any], int]:
        """
        获取支持的转换格式列表
        
        Returns:
            Tuple[Dict, int]: (响应数据, HTTP状态码)
        """
        try:
            conversions = self.converter_service.get_supported_conversions()
            dependencies = self.converter_service.dependencies
            
            return {
                'success': True,
                'conversions': conversions,
                'dependencies': dependencies,
                'message': '获取支持的转换格式成功'
            }, 200
            
        except Exception as e:
            log_error(e, "获取支持的转换格式失败")
            return {
                'success': False,
                'message': f'获取转换格式失败: {str(e)}'
            }, 500
    
    def convert_file(self) -> Tuple[Dict[str, Any], int]:
        """
        转换单个文件
        
        Returns:
            Tuple[Dict, int]: (响应数据, HTTP状态码)
        """
        try:
            # 检查是否有文件上传
            if 'file' not in request.files:
                return {
                    'success': False,
                    'message': '没有上传文件'
                }, 400
            
            file = request.files['file']
            target_format = request.form.get('target_format', '').lower()
            
            # 验证参数
            if not target_format:
                return {
                    'success': False,
                    'message': '缺少目标格式参数'
                }, 400
            
            if file.filename == '':
                return {
                    'success': False,
                    'message': '没有选择文件'
                }, 400
            
            # 检查文件扩展名
            if not self._allowed_file(file.filename):
                return {
                    'success': False,
                    'message': f'不支持的文件格式: {file.filename}'
                }, 400
            
            # 保存上传的文件
            filename = secure_filename(file.filename)
            input_path = os.path.join(self.upload_folder, filename)
            file.save(input_path)
            
            # 执行转换
            result = self.converter_service.convert_file(input_path, target_format)
            
            # 清理上传的文件
            try:
                os.remove(input_path)
            except:
                pass
            
            if result['success']:
                # 返回转换后的文件
                return self._send_converted_file(result['output_path'])
            else:
                return {
                    'success': False,
                    'message': result['message'],
                    'error_code': result.get('error_code', 'UNKNOWN_ERROR')
                }, 400
                
        except Exception as e:
            log_error(e, "文件转换失败")
            return {
                'success': False,
                'message': f'文件转换失败: {str(e)}'
            }, 500
    
    def batch_convert(self) -> Tuple[Dict[str, Any], int]:
        """
        批量转换文件
        
        Returns:
            Tuple[Dict, int]: (响应数据, HTTP状态码)
        """
        try:
            # 检查是否有文件上传
            if 'files' not in request.files:
                return {
                    'success': False,
                    'message': '没有上传文件'
                }, 400
            
            files = request.files.getlist('files')
            target_format = request.form.get('target_format', '').lower()
            
            # 验证参数
            if not target_format:
                return {
                    'success': False,
                    'message': '缺少目标格式参数'
                }, 400
            
            if not files or all(f.filename == '' for f in files):
                return {
                    'success': False,
                    'message': '没有选择文件'
                }, 400
            
            # 保存上传的文件
            file_paths = []
            for file in files:
                if file.filename and self._allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    input_path = os.path.join(self.upload_folder, filename)
                    file.save(input_path)
                    file_paths.append(input_path)
            
            if not file_paths:
                return {
                    'success': False,
                    'message': '没有有效的文件可以转换'
                }, 400
            
            # 执行批量转换
            result = self.converter_service.batch_convert(file_paths, target_format)
            
            # 清理上传的文件
            for file_path in file_paths:
                try:
                    os.remove(file_path)
                except:
                    pass
            
            return {
                'success': True,
                'message': f'批量转换完成，成功: {result["success_count"]}, 失败: {result["failed_count"]}',
                'result': result
            }, 200
            
        except Exception as e:
            log_error(e, "批量文件转换失败")
            return {
                'success': False,
                'message': f'批量转换失败: {str(e)}'
            }, 500
    
    def get_file_info(self) -> Tuple[Dict[str, Any], int]:
        """
        获取文件信息
        
        Returns:
            Tuple[Dict, int]: (响应数据, HTTP状态码)
        """
        try:
            # 检查是否有文件上传
            if 'file' not in request.files:
                return {
                    'success': False,
                    'message': '没有上传文件'
                }, 400
            
            file = request.files['file']
            
            if file.filename == '':
                return {
                    'success': False,
                    'message': '没有选择文件'
                }, 400
            
            # 保存上传的文件
            filename = secure_filename(file.filename)
            input_path = os.path.join(self.upload_folder, filename)
            file.save(input_path)
            
            # 获取文件信息
            result = self.converter_service.get_file_info(input_path)
            
            # 清理上传的文件
            try:
                os.remove(input_path)
            except:
                pass
            
            if result['success']:
                return {
                    'success': True,
                    'file_info': result,
                    'message': '获取文件信息成功'
                }, 200
            else:
                return {
                    'success': False,
                    'message': result['message']
                }, 400
                
        except Exception as e:
            log_error(e, "获取文件信息失败")
            return {
                'success': False,
                'message': f'获取文件信息失败: {str(e)}'
            }, 500
    
    def _allowed_file(self, filename: str) -> bool:
        """
        检查文件扩展名是否允许
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 是否允许
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def _send_converted_file(self, file_path: str) -> Tuple[Any, int]:
        """
        发送转换后的文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            Tuple: (文件响应, HTTP状态码)
        """
        try:
            # 记录访问日志
            log_access("GET", f"/api/convert/download", "127.0.0.1", 
                     user_agent=request.headers.get('User-Agent', ''))
            
            # 发送文件
            return send_file(
                file_path,
                as_attachment=True,
                download_name=os.path.basename(file_path),
                mimetype='application/octet-stream'
            ), 200
            
        except Exception as e:
            log_error(e, f"发送转换文件失败: {file_path}")
            return {
                'success': False,
                'message': f'发送文件失败: {str(e)}'
            }, 500
    
    def download_converted_file(self, filename: str) -> Tuple[Any, int]:
        """
        下载转换后的文件
        
        Args:
            filename: 文件名
            
        Returns:
            Tuple: (文件响应, HTTP状态码)
        """
        try:
            # 构建文件路径
            file_path = os.path.join(self.upload_folder, filename)
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'message': '文件不存在'
                }, 404
            
            # 记录访问日志
            log_access("GET", f"/api/convert/download/{filename}", "127.0.0.1",
                     user_agent=request.headers.get('User-Agent', ''))
            
            # 发送文件
            return send_file(
                file_path,
                as_attachment=True,
                download_name=filename,
                mimetype='application/octet-stream'
            ), 200
            
        except Exception as e:
            log_error(e, f"下载转换文件失败: {filename}")
            return {
                'success': False,
                'message': f'下载文件失败: {str(e)}'
            }, 500
    
    def cleanup_temp_files(self) -> Tuple[Dict[str, Any], int]:
        """
        清理临时文件
        
        Returns:
            Tuple[Dict, int]: (响应数据, HTTP状态码)
        """
        try:
            cleaned_count = 0
            error_count = 0
            
            # 清理上传目录中的文件
            for filename in os.listdir(self.upload_folder):
                file_path = os.path.join(self.upload_folder, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        cleaned_count += 1
                except Exception as e:
                    log_error(e, f"清理文件失败: {file_path}")
                    error_count += 1
            
            return {
                'success': True,
                'message': f'清理完成，成功清理: {cleaned_count} 个文件',
                'cleaned_count': cleaned_count,
                'error_count': error_count
            }, 200
            
        except Exception as e:
            log_error(e, "清理临时文件失败")
            return {
                'success': False,
                'message': f'清理失败: {str(e)}'
            }, 500
