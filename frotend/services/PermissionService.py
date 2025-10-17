"""
权限装饰器
提供管理员权限验证等装饰器
"""

from functools import wraps
from flask import session, jsonify
from model.UserModel import UserModel
from config.LoggerConfig import log_security, log_info

def admin_required(f):
    """
    管理员权限装饰器
    只允许管理员角色访问被装饰的路由
    
    Usage:
        @app.route('/admin/users')
        @admin_required
        def manage_users():
            return jsonify({'message': 'Admin only'})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查用户是否登录
        session_token = session.get('session_token')
        if not session_token:
            log_security("权限验证", "未登录用户尝试访问管理员功能")
            return jsonify({
                'success': False,
                'message': '请先登录',
                'error_code': 'NOT_AUTHENTICATED'
            }), 401
        
        # 验证会话并获取用户信息
        user_model = UserModel()
        is_valid, user_id = user_model.validate_session(session_token)
        
        if not is_valid or not user_id:
            log_security("权限验证", "无效会话尝试访问管理员功能")
            return jsonify({
                'success': False,
                'message': '会话已过期，请重新登录',
                'error_code': 'SESSION_EXPIRED'
            }), 401
        
        # 获取用户详细信息
        user = user_model.get_user_by_id(user_id)
        if not user:
            log_security("权限验证", f"用户ID {user_id} 不存在")
            return jsonify({
                'success': False,
                'message': '用户不存在',
                'error_code': 'USER_NOT_FOUND'
            }), 404
        
        # 检查用户角色
        if user.role != 'admin':
            log_security("权限验证", f"普通用户 {user.username} 尝试访问管理员功能", user_id=user_id)
            return jsonify({
                'success': False,
                'message': '权限不足，仅限管理员访问',
                'error_code': 'PERMISSION_DENIED'
            }), 403
        
        # 权限验证通过
        log_info(f"管理员 {user.username} 访问管理功能", f"功能: {f.__name__}")
        
        # 将用户信息传递给被装饰的函数
        kwargs['current_user'] = user
        return f(*args, **kwargs)
    
    return decorated_function


def login_required(f):
    """
    登录验证装饰器
    只允许已登录用户访问被装饰的路由
    
    Usage:
        @app.route('/profile')
        @login_required
        def view_profile():
            return jsonify({'message': 'Profile page'})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查用户是否登录
        session_token = session.get('session_token')
        if not session_token:
            return jsonify({
                'success': False,
                'message': '请先登录',
                'error_code': 'NOT_AUTHENTICATED'
            }), 401
        
        # 验证会话
        user_model = UserModel()
        is_valid, user_id = user_model.validate_session(session_token)
        
        if not is_valid or not user_id:
            return jsonify({
                'success': False,
                'message': '会话已过期，请重新登录',
                'error_code': 'SESSION_EXPIRED'
            }), 401
        
        # 获取用户信息
        user = user_model.get_user_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在',
                'error_code': 'USER_NOT_FOUND'
            }), 404
        
        # 将用户信息传递给被装饰的函数
        kwargs['current_user'] = user
        return f(*args, **kwargs)
    
    return decorated_function
