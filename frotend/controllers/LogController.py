"""
日志管理控制器
处理日志查看、清空、下载等日志管理功能
"""

from flask import request, jsonify, send_file
from typing import Dict, Any, List
from config.LoggerConfig import LoggerConfig, log_info, log_error
import os
import tempfile
from datetime import datetime

class LogController:
    """日志管理控制器类"""
    
    def __init__(self):
        """初始化日志控制器"""
        self.logger_config = LoggerConfig()
    
    def get_logs(self) -> tuple[Dict[str, Any], int]:
        """
        获取日志列表
        
        Returns:
            Tuple[Dict, int]: (响应数据, HTTP状态码)
        """
        try:
            log_type = request.args.get('type', 'all')
            log_level = request.args.get('level', 'all')
            lines = int(request.args.get('lines', 100))
            
            logs = []
            stats = {'total': 0, 'error': 0, 'auth': 0, 'access': 0}
            
            # 根据类型选择日志文件
            if log_type == 'all':
                log_files = self.logger_config.LOG_FILES.values()
            else:
                log_files = [self.logger_config.LOG_FILES.get(log_type, 'app.log')]
            
            for log_file in log_files:
                log_path = os.path.join(self.logger_config.LOG_DIR, log_file)
                if os.path.exists(log_path):
                    with open(log_path, 'r', encoding='utf-8') as f:
                        file_logs = f.readlines()
                        
                        # 过滤日志级别
                        filtered_logs = []
                        for line in file_logs:
                            if log_level == 'all' or f' - {log_level} - ' in line:
                                filtered_logs.append(line.strip())
                        
                        # 取最后N行
                        filtered_logs = filtered_logs[-lines:]
                        
                        # 解析日志格式
                        for line in filtered_logs:
                            if line:
                                parts = line.split(' - ', 3)
                                if len(parts) >= 4:
                                    logs.append({
                                        'timestamp': parts[0],
                                        'logger': parts[1],
                                        'level': parts[2],
                                        'message': parts[3]
                                    })
                                    
                                    # 统计
                                    stats['total'] += 1
                                    if 'ERROR' in parts[2]:
                                        stats['error'] += 1
                                    if 'auth' in parts[1]:
                                        stats['auth'] += 1
                                    if 'access' in parts[1]:
                                        stats['access'] += 1
            
            # 按时间排序（最新的在前）
            logs.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return {
                'success': True,
                'logs': logs,
                'stats': stats
            }, 200
            
        except Exception as e:
            log_error(e, "获取日志失败")
            return {
                'success': False,
                'message': f'获取日志失败: {str(e)}'
            }, 500
    
    def clear_logs(self) -> tuple[Dict[str, Any], int]:
        """
        清空日志文件
        
        Returns:
            Tuple[Dict, int]: (响应数据, HTTP状态码)
        """
        try:
            cleared_files = []
            for log_file in self.logger_config.LOG_FILES.values():
                log_path = os.path.join(self.logger_config.LOG_DIR, log_file)
                if os.path.exists(log_path):
                    with open(log_path, 'w', encoding='utf-8') as f:
                        f.write('')
                    cleared_files.append(log_file)
            
            log_info(f"日志已清空，涉及文件: {', '.join(cleared_files)}")
            
            return {
                'success': True,
                'message': f'已清空 {len(cleared_files)} 个日志文件'
            }, 200
            
        except Exception as e:
            log_error(e, "清空日志失败")
            return {
                'success': False,
                'message': f'清空日志失败: {str(e)}'
            }, 500
    
    def download_logs(self) -> tuple[Any, int]:
        """
        下载日志文件
        
        Returns:
            Tuple[Any, int]: (文件响应, HTTP状态码)
        """
        try:
            log_type = request.args.get('type', 'all')
            
            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8')
            
            # 根据类型选择日志文件
            if log_type == 'all':
                log_files = self.logger_config.LOG_FILES.values()
            else:
                log_files = [self.logger_config.LOG_FILES.get(log_type, 'app.log')]
            
            for log_file in log_files:
                log_path = os.path.join(self.logger_config.LOG_DIR, log_file)
                if os.path.exists(log_path):
                    temp_file.write(f"=== {log_file} ===\n")
                    with open(log_path, 'r', encoding='utf-8') as f:
                        temp_file.write(f.read())
                    temp_file.write("\n\n")
            
            temp_file.close()
            
            log_info(f"日志下载请求 - 类型: {log_type}")
            
            return send_file(
                temp_file.name,
                as_attachment=True,
                download_name=f'logs_{log_type}_{datetime.now().strftime("%Y%m%d")}.txt',
                mimetype='text/plain'
            ), 200
            
        except Exception as e:
            log_error(e, "下载日志失败")
            return {
                'success': False,
                'message': f'下载日志失败: {str(e)}'
            }, 500
