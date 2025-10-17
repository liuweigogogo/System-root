"""
用户模型 - 重构版本
使用模块化设计，将功能分离到不同的服务中
"""

from typing import Optional, Tuple
from model.BaseUser import BaseUser
from services.DatabaseService import DatabaseService
from services.AuthService import AuthService
from services.SessionService import SessionService
from config.LoggerConfig import log_info, log_error

class UserModel:
    """用户数据模型 - 重构版本"""
    
    def __init__(self):
        """初始化用户模型"""
        self.db_service = DatabaseService()
        self.auth_service = AuthService()
        self.session_service = SessionService()
    
    def create_tables(self) -> bool:
        """
        创建用户相关表
        
        Returns:
            bool: 创建是否成功
        """
        try:
            log_info("开始创建用户相关表")
            success = self.db_service.create_tables(['users', 'user_sessions'])
            
            if success:
                log_info("用户相关表创建成功")
            else:
                log_error("用户相关表创建失败")
            
            return success
            
        except Exception as e:
            log_error(e, "创建用户表异常")
            return False
    
    def create_user(self, username: str, password: str, email: Optional[str] = None) -> Tuple[bool, str]:
        """
        创建新用户
        
        Args:
            username: 用户名
            password: 密码
            email: 邮箱地址
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        return self.auth_service.register_user(username, password, email)
    
    def authenticate_user(self, username: str, password: str, ip_address: Optional[str] = None) -> Tuple[bool, Optional[int], str]:
        """
        验证用户登录
        model是对服务的封装，返回更简洁的结果，不暴露服务的复杂性。
        Args:
            username: 用户名
            password: 密码
            ip_address: IP地址
            
        Returns:
            Tuple[bool, Optional[int], str]: (是否成功, 用户ID, 消息)
        """
        success, user, message = self.auth_service.authenticate_user(username, password, ip_address)
        return success, user.id if user else None, message
    
    def create_session(self, user_id: int, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Optional[str]:
        """
        创建用户会话
        
        Args:
            user_id: 用户ID
            ip_address: IP地址
            user_agent: 用户代理
            
        Returns:
            Optional[str]: 会话令牌
        """
        return self.session_service.create_session(user_id, ip_address, user_agent)
    
    def validate_session(self, session_token: str) -> Tuple[bool, Optional[int]]:
        """
        验证会话是否有效
        
        Args:
            session_token: 会话令牌
            
        Returns:
            Tuple[bool, Optional[int]]: (是否有效, 用户ID)
        """
        success, user = self.session_service.validate_session(session_token)
        return success, user.id if user else None
    
    def logout_session(self, session_token: str) -> bool:
        """
        注销会话
        
        Args:
            session_token: 会话令牌
            
        Returns:
            bool: 是否成功
        """
        return self.session_service.logout_session(session_token)
    
    def get_user_by_id(self, user_id: int) -> Optional[BaseUser]:
        """
        根据用户ID获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[BaseUser]: 用户对象
        """
        return self.auth_service.get_user_by_id(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[BaseUser]:
        """
        根据用户名获取用户信息
        
        Args:
            username: 用户名
            
        Returns:
            Optional[BaseUser]: 用户对象
        """
        return self.auth_service.get_user_by_username(username)
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
        """
        修改用户密码

        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码

        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        return self.auth_service.change_password(user_id, old_password, new_password)
    
    def logout_user_sessions(self, user_id: int) -> bool:
        """
        注销用户的所有会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否成功
        """
        return self.session_service.logout_user_sessions(user_id)
    
    def get_user_sessions(self, user_id: int) -> list:
        """
        获取用户的所有活跃会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            list: 会话列表
        """
        return self.session_service.get_user_sessions(user_id)
    
    def cleanup_expired_sessions(self) -> int:
        """
        清理过期会话
        
        Returns:
            int: 清理的会话数量
        """
        return self.session_service.cleanup_expired_sessions()
    
    def extend_session(self, session_token: str, hours: int = 24) -> bool:
        """
        延长会话时间
        
        Args:
            session_token: 会话令牌
            hours: 延长的小时数
            
        Returns:
            bool: 是否成功
        """
        return self.session_service.extend_session(session_token, hours)
    
    def get_session_info(self, session_token: str) -> Optional[dict]:
        """
        获取会话详细信息
        
        Args:
            session_token: 会话令牌
            
        Returns:
            Optional[dict]: 会话信息字典
        """
        session = self.session_service.get_session_info(session_token)
        return session.to_dict() if session else None