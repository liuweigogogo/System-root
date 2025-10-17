#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本

用途：
- 创建业务数据库（如不存在）
- 初始化表结构（users/user_sessions）
- 创建默认管理员账户

运行：python setup_db.py
"""

from model.UserModel import UserModel
from config.DatabaseConfig import DatabaseConfig
from config.LoggerConfig import log_info, log_error
import MySQLdb
import sys

def create_database():
    """创建数据库"""
    try:
        # 连接到MySQL服务器（不指定数据库）
        connection = MySQLdb.connect(
            host=DatabaseConfig.MYSQL_HOST,
            user=DatabaseConfig.MYSQL_USER,
            passwd=DatabaseConfig.MYSQL_PASSWORD,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # 创建数据库
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DatabaseConfig.MYSQL_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"数据库 '{DatabaseConfig.MYSQL_DB}' 创建成功")
        log_info(f"数据库 '{DatabaseConfig.MYSQL_DB}' 创建成功")
        
        connection.close()
        return True
        
    except MySQLdb.Error as e:
        print(f"创建数据库失败: {e}")
        log_error(e, "创建数据库失败")
        return False

def create_tables():
    """创建表结构"""
    try:
        user_model = UserModel()
        success = user_model.create_tables()
        
        if success:
            print("数据表创建成功")
            log_info("数据表创建成功")
            return True
        else:
            print("数据表创建失败")
            log_error("数据表创建失败")
            return False
            
    except Exception as e:
        print(f"创建表失败: {e}")
        log_error(e, "创建表失败")
        return False

def create_admin_user():
    """创建管理员用户"""
    try:
        user_model = UserModel()
        success, message = user_model.create_user("admin", "admin123", "admin@example.com")
        
        if success:
            print("管理员用户创建成功")
            print("用户名: admin")
            print("密码: admin123")
            print("请登录后立即修改密码！")
            log_info("管理员用户创建成功 - 用户名: admin")
            return True
        else:
            print(f"创建管理员用户失败: {message}")
            log_error(f"创建管理员用户失败: {message}")
            return False
            
    except Exception as e:
        print(f"创建管理员用户失败: {e}")
        log_error(e, "创建管理员用户失败")
        return False

def main():
    """主函数"""
    print("=== 数据库初始化脚本 ===")
    print()
    
    # 检查数据库配置
    print("检查数据库配置...")
    print(f"主机: {DatabaseConfig.MYSQL_HOST}")
    print(f"用户: {DatabaseConfig.MYSQL_USER}")
    print(f"数据库: {DatabaseConfig.MYSQL_DB}")
    print()
    
    # 创建数据库
    print("1. 创建数据库...")
    if not create_database():
        print("数据库创建失败，请检查MySQL连接配置")
        sys.exit(1)
    
    # 创建表结构
    print("2. 创建数据表...")
    if not create_tables():
        print("数据表创建失败")
        sys.exit(1)
    
    # 创建管理员用户
    print("3. 创建管理员用户...")
    if not create_admin_user():
        print("管理员用户创建失败")
        sys.exit(1)
    
    print()
    print("=== 初始化完成 ===")
    print("现在可以运行 'python app.py' 启动应用")
    print("访问 http://localhost:5000 进行登录")

if __name__ == "__main__":
    main()
