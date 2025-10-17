#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统功能测试脚本
用于逐步验证系统各个功能模块
"""

import sys
import os

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        from config.DatabaseConfig import DatabaseConfig
        print("✅ DatabaseConfig 导入成功")
    except Exception as e:
        print(f"❌ DatabaseConfig 导入失败: {e}")
        return False
    
    try:
        from config.LoggerConfig import LoggerConfig
        print("✅ LoggerConfig 导入成功")
    except Exception as e:
        print(f"❌ LoggerConfig 导入失败: {e}")
        return False
    
    try:
        from model.UserModel import UserModel
        print("✅ UserModel 导入成功")
    except Exception as e:
        print(f"❌ UserModel 导入失败: {e}")
        return False
    
    return True

def test_database_connection():
    """测试数据库连接"""
    print("\n🔍 测试数据库连接...")
    
    try:
        from config.DatabaseConfig import DatabaseConfig
        connection = DatabaseConfig.get_connection()
        
        if connection:
            print("✅ 数据库连接成功")
            connection.close()
            return True
        else:
            print("❌ 数据库连接失败")
            return False
    except Exception as e:
        print(f"❌ 数据库连接异常: {e}")
        return False

def test_logger():
    """测试日志功能"""
    print("\n🔍 测试日志功能...")
    
    try:
        from config.LoggerConfig import log_info, log_error
        
        log_info("测试日志功能", "这是一条测试信息")
        log_error("测试错误日志", "这是一条测试错误")
        
        print("✅ 日志功能正常")
        return True
    except Exception as e:
        print(f"❌ 日志功能异常: {e}")
        return False

def test_user_model():
    """测试用户模型"""
    print("\n🔍 测试用户模型...")
    
    try:
        from model.UserModel import UserModel
        
        user_model = UserModel()
        
        # 测试创建表
        print("  - 测试创建表...")
        success = user_model.create_tables()
        if success:
            print("  ✅ 表创建成功")
        else:
            print("  ❌ 表创建失败")
            return False
        
        # 测试创建用户
        print("  - 测试创建用户...")
        success, message = user_model.create_user("test_user", "test_password", "test@example.com")
        if success:
            print("  ✅ 用户创建成功")
        else:
            print(f"  ❌ 用户创建失败: {message}")
            return False
        
        # 测试用户认证
        print("  - 测试用户认证...")
        success, user_id, message = user_model.authenticate_user("test_user", "test_password")
        if success:
            print(f"  ✅ 用户认证成功，用户ID: {user_id}")
        else:
            print(f"  ❌ 用户认证失败: {message}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ 用户模型测试异常: {e}")
        return False

def test_flask_app():
    """测试Flask应用"""
    print("\n🔍 测试Flask应用...")
    
    try:
        # 检查app.py文件
        if not os.path.exists('app.py'):
            print("❌ app.py 文件不存在")
            return False
        
        print("✅ app.py 文件存在")
        
        # 检查模板文件
        if not os.path.exists('templates/dashboard.html'):
            print("❌ dashboard.html 模板不存在")
            return False
        
        print("✅ 模板文件存在")
        
        # 检查静态文件
        if not os.path.exists('css/style.css'):
            print("❌ style.css 文件不存在")
            return False
        
        print("✅ 静态文件存在")
        
        return True
    except Exception as e:
        print(f"❌ Flask应用测试异常: {e}")
        return False

def test_log_files():
    """测试日志文件"""
    print("\n🔍 测试日志文件...")
    
    try:
        # 检查logs目录
        if not os.path.exists('logs'):
            os.makedirs('logs')
            print("✅ logs 目录已创建")
        else:
            print("✅ logs 目录存在")
        
        # 测试日志记录
        from config.LoggerConfig import log_info, log_error
        
        log_info("系统测试", "开始系统功能测试")
        log_error("测试错误", "这是一条测试错误信息")
        
        # 检查日志文件是否生成
        log_files = ['app.log', 'auth.log', 'database.log', 'error.log', 'access.log']
        for log_file in log_files:
            log_path = os.path.join('logs', log_file)
            if os.path.exists(log_path):
                print(f"✅ {log_file} 文件已生成")
            else:
                print(f"⚠️  {log_file} 文件未生成（可能还没有相关操作）")
        
        return True
    except Exception as e:
        print(f"❌ 日志文件测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始系统功能测试\n")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("数据库连接", test_database_connection),
        ("日志功能", test_logger),
        ("用户模型", test_user_model),
        ("Flask应用", test_flask_app),
        ("日志文件", test_log_files)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统准备就绪")
        print("\n📝 下一步操作:")
        print("1. 运行 'python app.py' 启动应用")
        print("2. 访问 http://localhost:5000 进行登录")
        print("3. 使用用户名: admin, 密码: admin123")
    else:
        print("⚠️  部分测试失败，请检查上述错误信息")
        print("\n🔧 故障排除建议:")
        print("1. 检查数据库配置是否正确")
        print("2. 确保所有依赖已安装")
        print("3. 检查文件权限")

if __name__ == "__main__":
    main()

