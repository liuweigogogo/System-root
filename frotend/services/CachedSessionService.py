#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存会话服务模块

职责：
- 提供基于Redis的会话管理
- 缓存用户会话信息
- 提供会话验证和过期管理

特性：
- Redis缓存加速会话查询
- 自动过期机制
- 支持会话刷新
"""

import time
import secrets
from typing import Optional, Tuple, Dict, Any
from config.RedisConfig import cache_service, RedisConfig
from services.DatabaseService import DatabaseService
from config.LoggerConfig import log_info, log_error, log_security

class CachedSessionService:
    """
    缓存会话服务类
    
    使用Redis缓存用户会话信息，减少数据库查询
    会话数据同时存储在MySQL和Redis中，实现数据持久化和高速访问
    """
    
    # 缓存键前缀
    CACHE_PREFIX_SESSION = "session:"  # 会话缓存前缀
    CACHE_PREFIX_USER_SESSIONS = "user_sessions:"  # 用户所有会话列表前缀
    
    def __init__(self):
        """
        初始化缓存会话服务
        
        创建数据库服务实例用于持久化存储
        """
        self.db_service = DatabaseService()
        self.cache = cache_service
        # 会话默认过期时间（秒）
        self.session_timeout = RedisConfig.CACHE_SESSION_TIMEOUT
    
    def _get_session_cache_key(self, session_token: str) -> str:
        """
        生成会话缓存键
        
        Args:
            session_token: 会话令牌
            
        Returns:
            str: 缓存键名，格式：session:{token}
        """
        return f"{self.CACHE_PREFIX_SESSION}{session_token}"
    
    def _get_user_sessions_cache_key(self, user_id: int) -> str:
        """
        生成用户会话列表缓存键
        
        Args:
            user_id: 用户ID
            
        Returns:
            str: 缓存键名，格式：user_sessions:{user_id}
        """
        return f"{self.CACHE_PREFIX_USER_SESSIONS}{user_id}"
    
    def create_session(self, user_id: int, ip_address: str, user_agent: str = '') -> Optional[str]:
        """
        创建新的用户会话
        
        会话信息同时保存到MySQL和Redis中
        
        Args:
            user_id: 用户ID
            ip_address: 客户端IP地址
            user_agent: 用户代理字符串（浏览器信息）
            
        Returns:
            Optional[str]: 会话令牌，失败返回None
        """
        start_time = time.time()
        
        try:
            # 生成唯一的会话令牌（使用secrets模块生成安全的随机令牌）
            session_token = secrets.token_urlsafe(32)
            
            # 准备会话数据
            session_data = {
                'session_token': session_token,
                'user_id': user_id,
                'ip_address': ip_address,
                'user_agent': user_agent[:255] if user_agent else '',  # 限制长度
                'created_at': time.time(),
                'last_activity': time.time()
            }
            
            # 1. 保存到数据库（持久化存储）
            sql = """
            INSERT INTO user_sessions (session_token, user_id, ip_address, user_agent)
            VALUES (%s, %s, %s, %s)
            """
            success = self.db_service.execute_insert(
                sql,
                (session_token, user_id, ip_address, session_data['user_agent'])
            )
            
            if not success:
                log_error("创建会话失败", f"数据库插入失败 - 用户ID: {user_id}")
                return None
            
            # 2. 保存到Redis缓存（快速访问）
            cache_key = self._get_session_cache_key(session_token)
            self.cache.set_json(cache_key, session_data, self.session_timeout)
            
            # 3. 更新用户的会话列表缓存
            user_sessions_key = self._get_user_sessions_cache_key(user_id)
            # 删除旧的会话列表缓存，下次查询时会重新从数据库加载
            self.cache.delete(user_sessions_key)
            
            execution_time = time.time() - start_time
            log_info(f"会话创建成功 - 用户ID: {user_id}, 耗时: {execution_time:.3f}s")
            
            return session_token
            
        except Exception as e:
            log_error(e, f"创建会话异常 - 用户ID: {user_id}")
            return None
    
    def validate_session(self, session_token: str) -> Tuple[bool, Optional[int]]:
        """
        验证会话是否有效
        
        首先从Redis缓存查询，缓存未命中则查询数据库
        
        Args:
            session_token: 会话令牌
            
        Returns:
            Tuple[bool, Optional[int]]: (是否有效, 用户ID)
        """
        try:
            # 1. 先从Redis缓存获取
            cache_key = self._get_session_cache_key(session_token)
            cached_session = self.cache.get_json(cache_key)
            
            if cached_session:
                # 缓存命中
                user_id = cached_session.get('user_id')
                log_info(f"会话验证成功（缓存命中） - 令牌: {session_token[:10]}..., 用户ID: {user_id}")
                
                # 更新最后活动时间
                self._update_session_activity(session_token, cached_session)
                
                return True, user_id
            
            # 2. 缓存未命中，查询数据库
            log_info(f"缓存未命中，查询数据库 - 令牌: {session_token[:10]}...")
            sql = """
            SELECT user_id, ip_address, user_agent, created_at, last_activity
            FROM user_sessions
            WHERE session_token = %s AND is_active = 1
            """
            result = self.db_service.execute_query(sql, (session_token,))
            
            if not result:
                log_security("会话验证", f"无效的会话令牌: {session_token[:10]}...")
                return False, None
            
            session_info = result[0]
            user_id = session_info['user_id']
            
            # 检查会话是否过期（2小时）
            last_activity = session_info.get('last_activity')
            if last_activity:
                # 如果last_activity是datetime对象，转换为时间戳
                if hasattr(last_activity, 'timestamp'):
                    last_activity_timestamp = last_activity.timestamp()
                else:
                    last_activity_timestamp = float(last_activity)
                
                # 检查是否超过2小时未活动
                if time.time() - last_activity_timestamp > self.session_timeout:
                    log_security("会话验证", f"会话已过期 - 用户ID: {user_id}")
                    # 标记会话为非活动状态
                    self._deactivate_session(session_token)
                    return False, None
            
            # 3. 将数据库查询结果写入缓存
            session_data = {
                'session_token': session_token,
                'user_id': user_id,
                'ip_address': session_info['ip_address'],
                'user_agent': session_info['user_agent'],
                'created_at': time.time(),
                'last_activity': time.time()
            }
            self.cache.set_json(cache_key, session_data, self.session_timeout)
            
            # 更新最后活动时间
            self._update_session_activity(session_token, session_data)
            
            log_info(f"会话验证成功（数据库查询） - 用户ID: {user_id}")
            return True, user_id
            
        except Exception as e:
            log_error(e, f"会话验证异常 - 令牌: {session_token[:10]}...")
            return False, None
    
    def _update_session_activity(self, session_token: str, session_data: dict):
        """
        更新会话最后活动时间
        
        Args:
            session_token: 会话令牌
            session_data: 会话数据字典
        """
        try:
            # 更新缓存中的最后活动时间
            session_data['last_activity'] = time.time()
            cache_key = self._get_session_cache_key(session_token)
            self.cache.set_json(cache_key, session_data, self.session_timeout)
            
            # 更新数据库（异步更新，不影响性能）
            sql = "UPDATE user_sessions SET last_activity = CURRENT_TIMESTAMP WHERE session_token = %s"
            self.db_service.execute_update(sql, (session_token,))
            
        except Exception as e:
            log_error(e, f"更新会话活动时间失败 - 令牌: {session_token[:10]}...")
    
    def logout_session(self, session_token: str) -> bool:
        """
        登出会话（标记为非活动状态）
        
        Args:
            session_token: 会话令牌
            
        Returns:
            bool: 是否成功
        """
        try:
            # 1. 从缓存删除
            cache_key = self._get_session_cache_key(session_token)
            self.cache.delete(cache_key)
            
            # 2. 更新数据库状态
            return self._deactivate_session(session_token)
            
        except Exception as e:
            log_error(e, f"登出会话失败 - 令牌: {session_token[:10]}...")
            return False
    
    def _deactivate_session(self, session_token: str) -> bool:
        """
        将会话标记为非活动状态
        
        Args:
            session_token: 会话令牌
            
        Returns:
            bool: 是否成功
        """
        try:
            sql = "UPDATE user_sessions SET is_active = 0 WHERE session_token = %s"
            success = self.db_service.execute_update(sql, (session_token,))
            
            if success:
                log_info(f"会话已停用 - 令牌: {session_token[:10]}...")
            
            return success
            
        except Exception as e:
            log_error(e, f"停用会话失败 - 令牌: {session_token[:10]}...")
            return False
    
    def logout_user_all_sessions(self, user_id: int) -> bool:
        """
        登出用户的所有会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否成功
        """
        try:
            # 1. 查询用户所有活动会话
            sql = """
            SELECT session_token 
            FROM user_sessions 
            WHERE user_id = %s AND is_active = 1
            """
            sessions = self.db_service.execute_query(sql, (user_id,))
            
            if sessions:
                # 2. 删除所有会话的缓存
                for session in sessions:
                    cache_key = self._get_session_cache_key(session['session_token'])
                    self.cache.delete(cache_key)
            
            # 3. 更新数据库，标记所有会话为非活动
            update_sql = "UPDATE user_sessions SET is_active = 0 WHERE user_id = %s"
            success = self.db_service.execute_update(update_sql, (user_id,))
            
            # 4. 删除用户会话列表缓存
            user_sessions_key = self._get_user_sessions_cache_key(user_id)
            self.cache.delete(user_sessions_key)
            
            if success:
                log_info(f"用户所有会话已登出 - 用户ID: {user_id}")
            
            return success
            
        except Exception as e:
            log_error(e, f"登出用户所有会话失败 - 用户ID: {user_id}")
            return False
    
    def get_user_sessions(self, user_id: int) -> list:
        """
        获取用户的所有活动会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            list: 会话信息列表
        """
        try:
            # 1. 尝试从缓存获取
            cache_key = self._get_user_sessions_cache_key(user_id)
            cached_sessions = self.cache.get_json(cache_key)
            
            if cached_sessions:
                log_info(f"用户会话列表（缓存命中） - 用户ID: {user_id}")
                return cached_sessions
            
            # 2. 从数据库查询
            sql = """
            SELECT session_token, ip_address, user_agent, created_at, last_activity
            FROM user_sessions
            WHERE user_id = %s AND is_active = 1
            ORDER BY last_activity DESC
            """
            sessions = self.db_service.execute_query(sql, (user_id,))
            
            # 3. 写入缓存
            if sessions:
                # 将datetime对象转换为字符串以便JSON序列化
                sessions_for_cache = []
                for session in sessions:
                    session_copy = dict(session)
                    if 'created_at' in session_copy and session_copy['created_at']:
                        session_copy['created_at'] = str(session_copy['created_at'])
                    if 'last_activity' in session_copy and session_copy['last_activity']:
                        session_copy['last_activity'] = str(session_copy['last_activity'])
                    sessions_for_cache.append(session_copy)
                
                self.cache.set_json(cache_key, sessions_for_cache, 300)  # 缓存5分钟
            
            log_info(f"用户会话列表（数据库查询） - 用户ID: {user_id}, 会话数: {len(sessions)}")
            return sessions or []
            
        except Exception as e:
            log_error(e, f"获取用户会话列表失败 - 用户ID: {user_id}")
            return []
    
    def clean_expired_sessions(self) -> int:
        """
        清理过期的会话
        
        定期任务调用，清理超过指定时间未活动的会话
        
        Returns:
            int: 清理的会话数量
        """
        try:
            # 计算过期时间点
            expire_time = time.time() - self.session_timeout
            
            sql = """
            UPDATE user_sessions 
            SET is_active = 0 
            WHERE is_active = 1 
            AND last_activity < FROM_UNIXTIME(%s)
            """
            
            affected_rows = self.db_service.execute_update(sql, (expire_time,))
            
            if affected_rows > 0:
                log_info(f"清理过期会话 - 数量: {affected_rows}")
            
            return affected_rows
            
        except Exception as e:
            log_error(e, "清理过期会话失败")
            return 0

# 创建全局缓存会话服务实例
cached_session_service = CachedSessionService()
