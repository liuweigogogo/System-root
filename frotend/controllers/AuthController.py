"""
认证控制器
处理用户登录、注册、登出、认证检查等认证相关功能
ctroller 作为控制前用来验证前端请求并调用相应的模型和服务。过滤第一层输入，记录日志，处理异常等。
"""

from flask import request, jsonify, session
from typing import Tuple, Dict, Any
from model.UserModel import UserModel
from services.CaptchaService import CaptchaService
from config.LoggerConfig import log_info, log_auth, log_error, log_security

class AuthController:
    """认证控制器类"""
    
    def __init__(self):
        """初始化认证控制器"""
        self.user_model = UserModel()
        self.captcha_service = CaptchaService()
    
    def get_client_ip(self) -> str:
        """
        获取客户端真实IP地址
        
        Returns:
            str: 客户端IP地址
        """
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr
    
    def login(self) -> Tuple[Dict[str, Any], int]:
        """
        用户登录处理
        
        Returns:
            Tuple[Dict, int]: (响应数据, HTTP状态码)
        """
        client_ip = self.get_client_ip()
        
        try:
            data = request.get_json()
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
            captcha = data.get('captcha', '').strip()
            
            log_info(f"登录尝试 - 用户名: {username}, IP: {client_ip}")
            
            # 基本验证
            if not username or not password:
                log_auth("登录尝试", username, client_ip, success=False, extra_info="用户名或密码为空")
                return {
                    'success': False,
                    'message': '用户名和密码不能为空'
                }, 400
            
            if not captcha:
                log_auth("登录尝试", username, client_ip, success=False, extra_info="验证码为空")
                return {
                    'success': False,
                    'message': '请输入验证码'
                }, 400
            
            # 验证码验证
            session_id = session.get('_id', 'default')
            if not self.captcha_service.verify_captcha(session_id, captcha):
                log_auth("登录尝试", username, client_ip, success=False, extra_info="验证码错误")
                return {
                    'success': False,
                    'message': '验证码错误'
                }, 400
            
            log_info(f"验证码验证通过 - 用户名: {username}")
            
            # 传入从前端获取的用户输入的账号，密码以及用户IP,验证用户凭据,是否满足登录条件。
            success, user_id, message = self.user_model.authenticate_user(username, password, client_ip)
            
            if not success:
                log_auth("登录失败", username, client_ip, success=False, extra_info=message)
                return {
                    'success': False,
                    'message': message
                }, 401
            
            # 创建会话
            session_token = self.user_model.create_session(user_id, client_ip, request.headers.get('User-Agent', ''))
            if not session_token:
                log_error("会话创建失败", f"用户ID: {user_id}, 用户名: {username}", user_id)
                return {
                    'success': False,
                    'message': '创建会话失败'
                }, 500
            
            # 设置会话
            session['user_id'] = user_id
            session['session_token'] = session_token
            
            log_auth("登录成功", username, client_ip, success=True, extra_info=f"用户ID: {user_id}")
            log_info(f"用户 {username} 成功登录，会话已创建")
            
            return {
                'success': True,
                'message': '登录成功',
                'redirect_url': '/dashboard'
            }, 200
            
        except Exception as e:
            log_error(e, f"登录API异常 - 用户名: {username}, IP: {client_ip}")
            log_security("登录异常", f"登录API发生异常: {str(e)}", client_ip)
            return {
                'success': False,
                'message': f'登录失败: {str(e)}'
            }, 500
    
    def register(self) -> Tuple[Dict[str, Any], int]:
        """
        用户注册处理
        
        Returns:
            Tuple[Dict, int]: (响应数据, HTTP状态码)
        """
        try:
            data = request.get_json()
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
            email = data.get('email', '').strip()
            
            # 基本验证
            if not username or not password:
                return {
                    'success': False,
                    'message': '用户名和密码不能为空'
                }, 400
            
            if len(username) < 3:
                return {
                    'success': False,
                    'message': '用户名至少3个字符'
                }, 400
            
            if len(password) < 6:
                return {
                    'success': False,
                    'message': '密码至少6个字符'
                }, 400
            
            # 创建用户
            success, message = self.user_model.create_user(username, password, email)
            
            return {
                'success': success,
                'message': message
            }, 200 if success else 400
            
        except Exception as e:
            return {
                'success': False,
                'message': f'注册失败: {str(e)}'
            }, 500
    
    def logout(self) -> Tuple[Dict[str, Any], int]:
        """
        用户登出处理
        
        Returns:
            Tuple[Dict, int]: (响应数据, HTTP状态码)
        """
        client_ip = self.get_client_ip()
        user_id = session.get('user_id')
        
        try:
            session_token = session.get('session_token')
            if session_token:
                self.user_model.logout_session(session_token)
                log_auth("用户登出", f"用户ID: {user_id}", client_ip, success=True)
            
            session.clear()
            log_info(f"用户 {user_id} 已登出，会话已清除")
            
            return {
                'success': True,
                'message': '登出成功'
            }, 200
            
        except Exception as e:
            log_error(e, f"登出失败 - 用户ID: {user_id}, IP: {client_ip}", user_id)
            return {
                'success': False,
                'message': f'登出失败: {str(e)}'
            }, 500
    
    def check_auth(self) -> Tuple[Dict[str, Any], int]:
        """
        检查用户认证状态
        
        Returns:
            Tuple[Dict, int]: (响应数据, HTTP状态码)
        """
        try:
            session_token = session.get('session_token')
            if not session_token:
                return {
                    'authenticated': False,
                    'message': '未登录'
                }, 200
            
            is_valid, user_id = self.user_model.validate_session(session_token)
            
            if not is_valid:
                session.clear()
                return {
                    'authenticated': False,
                    'message': '会话已过期'
                }, 200
            
            # 获取用户完整信息（包括role）
            user = self.user_model.get_user_by_id(user_id)
            
            if not user:
                session.clear()
                return {
                    'authenticated': False,
                    'message': '用户不存在'
                }, 200
            
            return {
                'authenticated': True,
                'user_id': user_id,
                'username': user.username,
                'role': user.role,  # 返回角色信息
                'email': user.email
            }, 200
            
        except Exception as e:
            return {
                'authenticated': False,
                'message': f'认证检查失败: {str(e)}'
            }, 500
    
    def get_captcha(self) -> Tuple[Dict[str, Any], int]:
        """
        获取验证码
        
        Returns:
            Tuple[Dict, int]: (响应数据, HTTP状态码)
        """
        try:
            # 使用session ID作为验证码标识
            session_id = session.get('_id', 'default')
            captcha_text, captcha_data = self.captcha_service.generate_captcha(session_id)
            
            if captcha_text:
                return {
                    'success': True,
                    'captcha': captcha_text,  # 暂时返回文本，实际应该返回图片
                    'message': '验证码生成成功'
                }, 200
            else:
                return {
                    'success': False,
                    'message': '验证码生成失败'
                }, 500
                
        except Exception as e:
            log_error(e, "生成验证码失败")
            return {
                'success': False,
                'message': f'验证码生成失败: {str(e)}'
            }, 500
