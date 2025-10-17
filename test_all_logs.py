#!/usr/bin/env python3
"""
测试所有类型的日志格式
"""

import sys
import os
import logging

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'frotend'))

from frotend.config.LoggerConfig import log_info, log_error, log_auth, log_db, log_security, log_access

def test_all_log_levels():
    """测试所有日志级别"""
    print("=== 测试所有日志级别 ===\n")
    
    # 获取各种日志器
    app_logger = logging.getLogger('app')
    auth_logger = logging.getLogger('auth')
    db_logger = logging.getLogger('database')
    error_logger = logging.getLogger('error')
    access_logger = logging.getLogger('access')
    
    # 测试不同级别
    print("1. 应用日志 (INFO):")
    log_info("应用启动成功")
    
    print("\n2. 认证日志 (INFO):")
    log_auth("用户登录", "admin", "127.0.0.1", success=True)
    
    print("\n3. 数据库日志 (INFO):")
    log_db("查询用户", "users", success=True, execution_time=0.045)
    
    print("\n4. 访问日志 (INFO):")
    log_access("GET", "/api/users", "127.0.0.1", "Mozilla/5.0", 1, 200)
    
    print("\n5. 安全日志 (WARNING):")
    log_security("异常登录", "多次失败登录尝试", "192.168.1.100", 1)
    
    print("\n6. 错误日志 (ERROR):")
    try:
        result = 1 / 0
    except Exception as e:
        log_error(e, "除零错误", 1)
    
    print("\n7. 直接使用日志器:")
    app_logger.debug("这是DEBUG级别日志")
    app_logger.info("这是INFO级别日志")
    app_logger.warning("这是WARNING级别日志")
    app_logger.error("这是ERROR级别日志")
    app_logger.critical("这是CRITICAL级别日志")

def show_log_format_info():
    """显示日志格式信息"""
    print("\n=== 日志格式说明 ===")
    print("📝 格式: 时间 - 日志器名称 - 级别 - 文件名:行号:函数名() - 消息")
    print("🎨 颜色: INFO(绿) WARNING(黄) ERROR(红) CRITICAL(紫) DEBUG(青)")
    print("📁 文件: 日志文件保存在 logs/ 目录下")
    print("🔄 轮转: 每个日志文件最大10MB，保留5个备份")
    print("\n📋 日志器类型:")
    print("  - app: 应用主日志")
    print("  - auth: 认证相关日志")
    print("  - database: 数据库操作日志")
    print("  - error: 错误日志")
    print("  - access: 访问日志")

if __name__ == "__main__":
    test_all_log_levels()
    show_log_format_info()
