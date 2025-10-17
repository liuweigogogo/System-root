#!/usr/bin/env python3
"""
测试新的日志格式
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'frotend'))

from frotend.config.LoggerConfig import log_info, log_error, log_auth, log_db

def test_logging_formats():
    """测试各种日志格式"""
    print("=== 测试新的日志格式 ===\n")
    
    # 测试信息日志
    log_info("这是一条信息日志", "额外信息")
    
    # 测试错误日志
    try:
        raise ValueError("这是一个测试错误")
    except Exception as e:
        log_error(e, "测试错误上下文")
    
    # 测试认证日志
    log_auth("用户登录", "admin", "127.0.0.1", success=True, extra_info="测试登录")
    
    # 测试数据库日志
    log_db("测试操作", "test_table", success=True, execution_time=0.123)
    
    print("\n=== 日志格式说明 ===")
    print("格式: 时间 - 日志器名称 - 级别 - 文件名:行号:函数名() - 消息")
    print("示例: 10:30:45 - app - INFO - test_logging.py:15:test_logging_formats() - 这是一条信息日志")

if __name__ == "__main__":
    test_logging_formats()
