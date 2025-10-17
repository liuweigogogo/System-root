#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置模块

职责：
- 初始化并暴露多类日志记录器（app/auth/database/error/access）
- 提供便捷函数用于记录信息、认证、数据库、错误、访问、安全等日志

特性：
- 滚动日志文件（10MB x 5 份备份）
- 控制台与文件双输出
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
import traceback
# traceback是Python内置模块，用于跟踪错误堆栈信息

class LoggerConfig:
    """日志配置类"""
    
    # 日志目录
    LOG_DIR = "logs"
    
    # 日志文件配置
    LOG_FILES = {
        'app': 'app.log',           # 应用主日志
        'auth': 'auth.log',         # 认证相关日志
        'database': 'database.log', # 数据库操作日志
        'error': 'error.log',       # 错误日志
        'access': 'access.log'      # 访问日志
    }
    
    # 日志级别
    LOG_LEVEL = logging.INFO
    
    @classmethod
    def setup_logger(cls, name, log_file=None, level=None):
        """
        设置并返回指定名称的日志记录器。

        参数:
        - name: str，日志记录器名称（例如 'app'、'auth'）。
        - log_file: str|None，日志文件名（位于 LOG_DIR 下）。None 表示仅输出到控制台。
        - level: int|None，日志级别（如 logging.INFO / logging.ERROR）。None 使用默认 LOG_LEVEL。

        返回:
        - logging.Logger，配置完成的日志记录器（包含文件与控制台 handler）。
        """
        
        # 确保日志目录存在
        if not os.path.exists(cls.LOG_DIR):
            os.makedirs(cls.LOG_DIR)
        
        # 创建日志记录器
        logger = logging.getLogger(name)
        logger.setLevel(level or cls.LOG_LEVEL)
        
        # 避免重复添加处理器
        if logger.handlers:
            return logger
        
        # 创建文件处理器
        if log_file:
            log_path = os.path.join(cls.LOG_DIR, log_file)
            
            # 使用RotatingFileHandler实现日志轮转
            file_handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            
            # 设置文件日志格式
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d:%(funcName)s() - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        
        # 创建带颜色的格式化器
        class ColoredFormatter(logging.Formatter):
            """带颜色的日志格式化器"""
            
            # 颜色代码
            COLORS = {
                'DEBUG': '\033[36m',    # 青色
                'INFO': '\033[32m',     # 绿色
                'WARNING': '\033[33m',  # 黄色
                'ERROR': '\033[31m',    # 红色
                'CRITICAL': '\033[35m', # 紫色
                'RESET': '\033[0m'      # 重置
            }
            
            def format(self, record):
                # 获取颜色
                color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
                reset = self.COLORS['RESET']
                
                # 格式化消息
                formatted = super().format(record)
                
                # 添加颜色（只在终端中）
                if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
                    return f"{color}{formatted}{reset}"
                else:
                    return formatted
        
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d:%(funcName)s() - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    @classmethod
    def get_app_logger(cls):
        """获取应用主日志记录器。返回 logging.Logger。"""
        return cls.setup_logger('app', cls.LOG_FILES['app'])
    
    @classmethod
    def get_auth_logger(cls):
        """获取认证日志记录器。返回 logging.Logger。"""
        return cls.setup_logger('auth', cls.LOG_FILES['auth'])
    
    @classmethod
    def get_database_logger(cls):
        """获取数据库日志记录器。返回 logging.Logger。"""
        return cls.setup_logger('database', cls.LOG_FILES['database'])
    
    @classmethod
    def get_error_logger(cls):
        """获取错误日志记录器（级别默认 ERROR）。返回 logging.Logger。"""
        return cls.setup_logger('error', cls.LOG_FILES['error'], logging.ERROR)
    
    @classmethod
    def get_access_logger(cls):
        """获取访问日志记录器。返回 logging.Logger。"""
        return cls.setup_logger('access', cls.LOG_FILES['access'])

class LogManager:
    """日志管理器"""
    
    def __init__(self):
        self.app_logger = LoggerConfig.get_app_logger()
        self.auth_logger = LoggerConfig.get_auth_logger()
        self.db_logger = LoggerConfig.get_database_logger()
        self.error_logger = LoggerConfig.get_error_logger()
        self.access_logger = LoggerConfig.get_access_logger()
    
    def log_app_info(self, message, extra_data=None):
        """
        记录应用信息级别日志。



        参数:
        - message: str，核心日志内容。
        - extra_data: Any|None，附加信息，会拼接到日志末尾。
        """
        log_msg = message
        if extra_data:
            log_msg += f" | 额外信息: {extra_data}"
        self.app_logger.info(log_msg)
    
    def log_auth_event(self, event_type, username, ip_address=None, success=True, extra_info=None):
        """
        记录认证相关事件（登录/登出/注册等）。

        参数:
        - event_type: str，事件类型（如 '用户登录'、'用户登出'、'用户注册'）。
        - username: str，关联用户名。
        - ip_address: str|None，来源 IP。
        - success: bool，是否成功。
        - extra_info: str|None，补充说明。
        """
        status = "成功" if success else "失败"
        log_msg = f"认证事件: {event_type} | 用户: {username} | 状态: {status}"
        
        if ip_address:
            log_msg += f" | IP: {ip_address}"
        
        if extra_info:
            log_msg += f" | 详情: {extra_info}"
        
        if success:
            self.auth_logger.info(log_msg)
        else:
            self.auth_logger.warning(log_msg)
    
    def log_database_operation(self, operation, table, success=True, error_msg=None, execution_time=None):
        """
        记录数据库操作及其结果与性能。

        参数:
        - operation: str，操作描述（如 '创建表'、'插入'、'查询'）。
        - table: str，涉及的表名或资源名（可为多个以逗号分隔）。
        - success: bool，是否成功。
        - error_msg: str|None，错误信息（失败时填写）。
        - execution_time: float|None，执行耗时（秒）。
        """
        status = "成功" if success else "失败"
        log_msg = f"数据库操作: {operation} | 表: {table} | 状态: {status}"
        
        if execution_time:
            log_msg += f" | 执行时间: {execution_time:.3f}s"
        
        if error_msg:
            log_msg += f" | 错误: {error_msg}"
        
        if success:
            self.db_logger.info(log_msg)
        else:
            self.db_logger.error(log_msg)
    
    def log_error(self, error, context=None, user_id=None):
        """
        记录错误级别日志，包含堆栈。

        参数:
        - error: Exception|str，异常对象或错误描述。
        - context: str|None，错误发生的上下文说明。
        - user_id: int|None，相关用户 ID。
        """
        error_msg = f"错误: {str(error)}"
        
        if context:
            error_msg += f" | 上下文: {context}"
        
        if user_id:
            error_msg += f" | 用户ID: {user_id}"
        
        # 记录错误堆栈
        error_msg += f" | 堆栈: {traceback.format_exc()}"
        
        self.error_logger.error(error_msg)
    
    def log_access(self, method, path, ip_address, user_agent=None, user_id=None, status_code=200):
        """
        记录 HTTP 访问日志。

        参数:
        - method: str，请求方法（GET/POST/...）。
        - path: str，请求路径。
        - ip_address: str，客户端 IP。
        - user_agent: str|None，UA 字符串。
        - user_id: int|None，登录用户 ID。
        - status_code: int，响应状态码。
        """
        log_msg = f"访问: {method} {path} | IP: {ip_address} | 状态码: {status_code}"
        
        if user_agent:
            log_msg += f" | 用户代理: {user_agent[:100]}"
        
        if user_id:
            log_msg += f" | 用户ID: {user_id}"
        
        self.access_logger.info(log_msg)
    
    def log_security_event(self, event_type, details, ip_address=None, user_id=None):
        """
        记录安全相关事件（如异常登录、暴力破解等）。

        参数:
        - event_type: str，安全事件类型。
        - details: str，事件详情描述。
        - ip_address: str|None，来源 IP。
        - user_id: int|None，关联用户 ID。
        """
        log_msg = f"安全事件: {event_type} | 详情: {details}"
        
        if ip_address:
            log_msg += f" | IP: {ip_address}"
        
        if user_id:
            log_msg += f" | 用户ID: {user_id}"
        
        self.auth_logger.warning(log_msg)

# 创建全局日志管理器实例
log_manager = LogManager()

# 便捷函数
def log_info(message, extra_data=None):
    """
    便捷函数：记录信息级别日志。

    参数:
    - message: st r，日志内容。
    - extra_data: Any|None，附加信息。
    """
    log_manager.log_app_info(message, extra_data)

def log_auth(event_type, username, ip_address=None, success=True, extra_info=None):
    """
    便捷函数：记录认证事件日志。

    参数见 LogManager.log_auth_event。
    """
    log_manager.log_auth_event(event_type, username, ip_address, success, extra_info)

def log_db(operation, table, success=True, error_msg=None, execution_time=None):
    """
    便捷函数：记录数据库操作日志。

    参数见 LogManager.log_database_operation。
    """
    log_manager.log_database_operation(operation, table, success, error_msg, execution_time)

def log_error(error, context=None, user_id=None):
    """
    便捷函数：记录错误日志（含堆栈）。

    参数见 LogManager.log_error。
    """
    log_manager.log_error(error, context, user_id)

def log_access(method, path, ip_address, user_agent=None, user_id=None, status_code=200):
    """
    便捷函数：记录访问日志。

    参数见 LogManager.log_access。
    """
    log_manager.log_access(method, path, ip_address, user_agent, user_id, status_code)

def log_security(event_type, details, ip_address=None, user_id=None):
    """
    便捷函数：记录安全事件日志。

    参数见 LogManager.log_security_event。
    """
    log_manager.log_security_event(event_type, details, ip_address, user_id)
