"""
基础用户模型
只包含用户的基础属性和数据结构定义
"""

from datetime import datetime
from typing import Optional

class BaseUser:
    """基础用户模型类"""
    
    def __init__(self, user_id: Optional[int] = None, username: str = "", 
                 email: Optional[str] = None, is_active: bool = True, 
                 role: str = "user"):
        """
        初始化用户对象
        
        Args:
            user_id: 用户ID
            username: 用户名
            email: 邮箱地址
            is_active: 是否激活
            role: 用户角色 ('user' 或 'admin')
        """
        self.id = user_id
        self.username = username
        self.email = email
        self.is_active = is_active
        self.role = role
        self.created_at = None
        self.last_login = None
    
    def to_dict(self) -> dict:
        """
        将用户对象转换为字典
        
        Returns:
            dict: 用户信息字典
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def from_dict(self, data: dict) -> 'BaseUser':
        """
        从字典创建用户对象
        
        Args:
            data: 用户数据字典
            
        Returns:
            BaseUser: 用户对象
        """
        self.id = data.get('id')
        self.username = data.get('username', '')
        self.email = data.get('email')
        self.role = data.get('role', 'user')
        self.is_active = data.get('is_active', True)
        self.created_at=data.get('created_at')
        self.last_login=data.get('last_login')
        # # 处理时间字段
        # if data.get('created_at'):
        #     self.created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        # if data.get('last_login'):
        #     self.last_login = datetime.fromisoformat(data['last_login'].replace('Z', '+00:00'))
        #
        return self
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')"
    
    def __repr__(self) -> str:
        """调试表示"""
        return f"BaseUser(id={self.id}, username='{self.username}', email='{self.email}', is_active={self.is_active})"


class UserSession:
    """用户会话模型类"""
    
    def __init__(self, session_id: Optional[int] = None, user_id: Optional[int] = None,
                 session_token: str = "", expires_at: Optional[datetime] = None,
                 ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """
        初始化会话对象
        
        Args:
            session_id: 会话ID
            user_id: 用户ID
            session_token: 会话令牌
            expires_at: 过期时间
            ip_address: IP地址
            user_agent: 用户代理
        """
        self.id = session_id
        self.user_id = user_id
        self.session_token = session_token
        self.expires_at = expires_at
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.created_at = None
        self.is_active = True
    
    def is_expired(self) -> bool:
        """
        检查会话是否已过期
        
        Returns:
            bool: 是否已过期
        """
        if not self.expires_at:
            return True
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> dict:
        """
        将会话对象转换为字典
        
        Returns:
            dict: 会话信息字典
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_token': self.session_token,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }
    
    def from_dict(self, data: dict) -> 'UserSession':
        """
        从字典创建会话对象
        
        Args:
            data: 会话数据字典
            
        Returns:
            UserSession: 会话对象
        """
        self.id = data.get('id')
        self.user_id = data.get('user_id')
        self.session_token = data.get('session_token', '')
        self.ip_address = data.get('ip_address')
        self.user_agent = data.get('user_agent')
        self.is_active = data.get('is_active', True)
        
        # 处理时间字段
        if data.get('expires_at'):
            self.expires_at = datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00'))
        if data.get('created_at'):
            self.created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        
        return self
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"UserSession(id={self.id}, user_id={self.user_id}, token='{self.session_token[:10]}...')"
    
    def __repr__(self) -> str:
        """调试表示"""
        return f"UserSession(id={self.id}, user_id={self.user_id}, token='{self.session_token[:10]}...', expires_at={self.expires_at})"
