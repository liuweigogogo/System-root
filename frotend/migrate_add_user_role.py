#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 添加用户角色字段

用途：
- 为现有的users表添加role字段
- 设置默认用户为admin角色
- 其他用户为普通用户角色

运行：python migrate_add_user_role.py
"""

from config.LoggerConfig import log_info, log_error
import sys

def migrate_add_user_role():
    """添加用户角色字段"""
    from config.DatabaseConfig import DatabaseConfig
    import MySQLdb
    
    try:
        print("=== 数据库迁移：添加用户角色字段 ===")
        print()
        
        # 直接连接数据库
        connection = MySQLdb.connect(
            host=DatabaseConfig.MYSQL_HOST,
            user=DatabaseConfig.MYSQL_USER,
            passwd=DatabaseConfig.MYSQL_PASSWORD,
            db=DatabaseConfig.MYSQL_DB,
            charset='utf8mb4'
        )
        cursor = connection.cursor()
        
        # 检查role列是否已存在
        print("1. 检查role列是否已存在...")
        check_sql = """
        SELECT COUNT(*) as count
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'users'
        AND COLUMN_NAME = 'role'
        """
        cursor.execute(check_sql)
        result = cursor.fetchone()
        
        if result and result[0] > 0:
            print("   ✓ role列已存在，无需迁移")
            log_info("数据库迁移", "role列已存在")
            connection.close()
            return True
        
        # 添加role列
        print("2. 添加role列...")
        alter_sql = """
        ALTER TABLE users 
        ADD COLUMN role ENUM('user', 'admin') DEFAULT 'user' NOT NULL COMMENT '用户角色：user-普通用户，admin-管理员'
        AFTER email
        """
        
        cursor.execute(alter_sql)
        connection.commit()
        print("   ✓ role列添加成功")
        log_info("数据库迁移", "role列添加成功")
        
        # 添加索引
        print("3. 添加role索引...")
        index_sql = "ALTER TABLE users ADD INDEX idx_role (role)"
        
        try:
            cursor.execute(index_sql)
            connection.commit()
            print("   ✓ role索引添加成功")
            log_info("数据库迁移", "role索引添加成功")
        except MySQLdb.Error as e:
            print(f"   ⚠ role索引添加失败（可能已存在）: {e}")
        
        # 将admin用户设置为管理员角色
        print("4. 设置admin用户为管理员角色...")
        update_admin_sql = "UPDATE users SET role = 'admin' WHERE username = 'admin'"
        
        cursor.execute(update_admin_sql)
        connection.commit()
        print("   ✓ admin用户角色更新成功")
        log_info("数据库迁移", "admin用户设置为管理员")
        
        connection.close()
        
        print()
        print("=== 迁移完成 ===")
        print("现在可以使用用户管理功能")
        log_info("数据库迁移", "用户角色字段迁移完成")
        return True
        
    except Exception as e:
        print(f"迁移失败: {e}")
        log_error(e, "数据库迁移失败")
        return False

def main():
    """主函数"""
    success = migrate_add_user_role()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
