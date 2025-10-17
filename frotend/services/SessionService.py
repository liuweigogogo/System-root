"""
会话管理服务
提供会话创建、验证、注销等功能
"""

import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple
from model.BaseUser import BaseUser, UserSession
from services.DatabaseService import DatabaseService
from config.LoggerConfig import log_auth, log_error, log_security

class SessionService:
    """会话管理服务类"""
    
    def __init__(self):
        """初始化会话服务"""
        self.db_service = DatabaseService()
        self.session_timeout_hours = 24  # 会话超时时间（小时）
    
    def create_session(self, user_id: int, ip_address: Optional[str] = None, 
                      user_agent: Optional[str] = None) -> Optional[str]:
        """
        创建用户会话
        
        Args:
            user_id: 用户ID
            ip_address: IP地址
            user_agent: 用户代理
            
        Returns:
            Optional[str]: 会话令牌，失败返回None
        """
        try:
            # 生成会话令牌
            session_token = secrets.token_urlsafe(32)
            
            # 设置过期时间
            expires_at = datetime.now() + timedelta(hours=self.session_timeout_hours)
            
            # 插入会话记录
            sql = """
            INSERT INTO user_sessions
            (user_id, session_token, expires_at, ip_address, user_agent) 
            VALUES (%s, %s, %s, %s, %s)
            """
            session_id = self.db_service.execute_insert(
                sql, (user_id, session_token, expires_at, ip_address, user_agent)
            )
            
            if session_id:
                log_auth("创建会话", f"用户ID: {user_id}", success=True, extra_info=f"会话ID: {session_id}")
                return session_token
            else:
                log_error("创建会话失败", f"用户ID: {user_id}")
                return None
                
        except Exception as e:
            log_error(e, f"创建会话失败 - 用户ID: {user_id}")
            return None
    
    def validate_session(self, session_token: str) -> Tuple[bool, Optional[BaseUser]]:
        """
        验证会话是否有效
        
        Args:
            session_token: 会话令牌
            
        Returns:
            Tuple[bool, Optional[BaseUser]]: (是否有效, 用户对象)
        """
        try:
            # 查询会话信息
            sql = """
            SELECT s.id, s.user_id, s.session_token, s.expires_at, s.ip_address, s.user_agent, 
                   s.created_at, s.is_active, u.username, u.email, u.is_active as user_active
            FROM user_sessions s 
            JOIN users u ON s.user_id = u.id 
            WHERE s.session_token = %s AND s.is_active = 1 AND u.is_active = 1
            """
            result = self.db_service.execute_query(sql, (session_token,))
            
            if not result:
                return False, None
            
            session_data = result[0]
            
            # 检查会话是否过期
            if session_data['expires_at'] and datetime.now() > session_data['expires_at']:
                # 标记会话为过期
                self._mark_session_expired(session_data['id'])
                return False, None
            
            # 创建用户对象
            user = BaseUser(
                user_id=session_data['user_id'],
                username=session_data['username'],
                email=session_data['email'],
                is_active=session_data['user_active']
            )
            
            return True, user
            
        except Exception as e:
            log_error(e, f"验证会话失败 - Token: {session_token[:10]}...")
            return False, None
    
    def logout_session(self, session_token: str) -> bool:
        """
        注销会话
        
        Args:
            session_token: 会话令牌
            
        Returns:
            bool: 是否成功
        """
        try:
            sql = "UPDATE user_sessions SET is_active = 0 WHERE session_token = %s"
            success = self.db_service.execute_update(sql, (session_token,))
            
            if success:
                log_auth("注销会话", f"Token: {session_token[:10]}...", success=True)
            else:
                log_error("注销会话失败", f"Token: {session_token[:10]}...")
            
            return success
            
        except Exception as e:
            log_error(e, f"注销会话失败 - Token: {session_token[:10]}...")
            return False
    
    def logout_user_sessions(self, user_id: int) -> bool:
        """
        注销用户的所有会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否成功
        """
        try:
            sql = "UPDATE user_sessions SET is_active = 0 WHERE user_id = %s"
            success = self.db_service.execute_update(sql, (user_id,))
            
            if success:
                log_auth("注销用户所有会话", f"用户ID: {user_id}", success=True)
            else:
                log_error("注销用户所有会话失败", f"用户ID: {user_id}")
            
            return success
            
        except Exception as e:
            log_error(e, f"注销用户所有会话失败 - 用户ID: {user_id}")
            return False
    
    def get_user_sessions(self, user_id: int) -> list:
        """
        获取用户的所有活跃会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            list: 会话列表
        """
        try:
            sql = """
            SELECT id, session_token, created_at, expires_at, ip_address, user_agent, is_active
            FROM user_sessions 
            WHERE user_id = %s AND is_active = 1
            ORDER BY created_at DESC
            """
            result = self.db_service.execute_query(sql, (user_id,))
            
            sessions = []
            for session_data in result:
                session = UserSession()
                session.from_dict(session_data)
                sessions.append(session)
            
            return sessions
            
        except Exception as e:
            log_error(e, f"获取用户会话失败 - 用户ID: {user_id}")
            return []
    
    def cleanup_expired_sessions(self) -> int:
        """
        清理过期会话
        
        Returns:
            int: 清理的会话数量
        """
        try:
            # 标记过期会话为非活跃
            sql = """
            UPDATE user_sessions 
            SET is_active = 0 
            WHERE expires_at < NOW() AND is_active = 1
            """
            self.db_service.execute_update(sql)
            
            # 查询清理的会话数量
            count_sql = """
            SELECT COUNT(*) as count 
            FROM user_sessions 
            WHERE expires_at < NOW() AND is_active = 0
            """
            result = self.db_service.execute_query(count_sql)
            cleaned_count = result[0]['count'] if result else 0
            
            log_auth("清理过期会话", f"清理数量: {cleaned_count}", success=True)
            return cleaned_count
            
        except Exception as e:
            log_error(e, "清理过期会话失败")
            return 0
    
    def extend_session(self, session_token: str, hours: int = 24) -> bool:
        """
        延长会话时间
        
        Args:
            session_token: 会话令牌
            hours: 延长的小时数
            
        Returns:
            bool: 是否成功
        """
        try:
            new_expires_at = datetime.now() + timedelta(hours=hours)
            sql = "UPDATE user_sessions SET expires_at = %s WHERE session_token = %s AND is_active = 1"
            
            success = self.db_service.execute_update(sql, (new_expires_at, session_token))
            
            if success:
                log_auth("延长会话", f"Token: {session_token[:10]}...", success=True, extra_info=f"延长{hours}小时")
            else:
                log_error("延长会话失败", f"Token: {session_token[:10]}...")
            
            return success
            
        except Exception as e:
            log_error(e, f"延长会话失败 - Token: {session_token[:10]}...")
            return False
    
    def get_session_info(self, session_token: str) -> Optional[UserSession]:
        """
        获取会话详细信息
        
        Args:
            session_token: 会话令牌
            
        Returns:
            Optional[UserSession]: 会话对象，不存在返回None
        """
        try:
            sql = """
            SELECT id, user_id, session_token, created_at, expires_at, ip_address, user_agent, is_active
            FROM user_sessions 
            WHERE session_token = %s
            """
            result = self.db_service.execute_query(sql, (session_token,))
            
            if result:
                session = UserSession()
                session.from_dict(result[0])
                return session
            return None
            
        except Exception as e:
            log_error(e, f"获取会话信息失败 - Token: {session_token[:10]}...")
            return None
    
    def _mark_session_expired(self, session_id: int) -> bool:
        """
        标记会话为过期
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 是否成功
        """
        try:
            sql = "UPDATE user_sessions SET is_active = 0 WHERE id = %s"
            return self.db_service.execute_update(sql, (session_id,))
        except Exception as e:
            log_error(e, f"标记会话过期失败 - 会话ID: {session_id}")
            return False
