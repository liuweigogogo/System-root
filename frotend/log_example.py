#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志系统使用示例
演示如何在代码中使用日志功能
"""

from config.LoggerConfig import log_info, log_auth, log_db, log_error, log_access, log_security

def example_usage():
    """日志使用示例"""
    
    print("=== 日志系统使用示例 ===\n")
    
    # 1. 记录应用信息
    log_info("应用启动", "系统初始化完成")
    log_info("用户操作", "用户执行了某个操作")
    
    # 2. 记录认证事件
    log_auth("用户登录", "admin", "192.168.1.100", success=True, extra_info="登录成功")
    log_auth("用户登录", "hacker", "192.168.1.200", success=False, extra_info="密码错误")
    
    # 3. 记录数据库操作
    log_db("查询用户", "users", success=True, execution_time=0.025)
    log_db("插入数据", "user_sessions", success=False, error_msg="连接超时", execution_time=5.0)
    
    # 4. 记录错误信息
    try:
        # 模拟一个错误
        result = 1 / 0
    except Exception as e:
        log_error(e, "计算错误", user_id=1)
    
    # 5. 记录访问日志
    log_access("GET", "/api/users", "192.168.1.100", "Mozilla/5.0...", user_id=1, status_code=200)
    log_access("POST", "/api/login", "192.168.1.200", "curl/7.68.0", status_code=401)
    
    # 6. 记录安全事件
    log_security("暴力破解", "检测到多次登录失败", "192.168.1.200")
    log_security("异常访问", "访问频率过高", "192.168.1.150", user_id=2)
    
    print("日志记录完成！")
    print("请查看 logs/ 目录下的日志文件")

if __name__ == "__main__":
    example_usage()
