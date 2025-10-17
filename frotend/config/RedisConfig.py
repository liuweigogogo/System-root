#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis配置模块

职责：
- 提供Redis连接配置
- 管理Redis连接池
- 提供缓存操作的基础方法

特性：
- 连接池管理
- 自动重连机制
- 异常处理
"""

import redis
from redis.connection import ConnectionPool
from typing import Optional, Any
import json
import pickle
from .LoggerConfig import log_info, log_error

class RedisConfig:
    """Redis配置类"""
    
    # Redis连接配置
    REDIS_HOST = 'localhost'  # Redis服务器地址
    REDIS_PORT = 6379  # Redis服务器端口
    REDIS_PASSWORD = None  # Redis密码，如果没有设置密码则为None
    REDIS_DB = 0  # 使用的数据库编号（0-15）
    REDIS_DECODE_RESPONSES = True  # 是否自动解码响应为字符串
    
    # 连接池配置
    REDIS_MAX_CONNECTIONS = 50  # 最大连接数
    REDIS_SOCKET_TIMEOUT = 5  # Socket超时时间（秒）
    REDIS_SOCKET_CONNECT_TIMEOUT = 5  # 连接超时时间（秒）
    
    # 缓存过期时间配置（秒）
    CACHE_DEFAULT_TIMEOUT = 300  # 默认缓存过期时间：5分钟
    CACHE_SHORT_TIMEOUT = 60  # 短期缓存：1分钟
    CACHE_MEDIUM_TIMEOUT = 600  # 中期缓存：10分钟
    CACHE_LONG_TIMEOUT = 3600  # 长期缓存：1小时
    CACHE_SESSION_TIMEOUT = 7200  # 会话缓存：2小时
    
    # 连接池实例（类变量，所有实例共享）
    _pool: Optional[ConnectionPool] = None
    _redis_client: Optional[redis.Redis] = None
    
    @classmethod
    def get_connection_pool(cls) -> ConnectionPool:
        """
        获取Redis连接池（单例模式）
        
        Returns:
            ConnectionPool: Redis连接池对象
        """
        # 如果连接池不存在，则创建新的连接池
        if cls._pool is None:
            try:
                cls._pool = redis.ConnectionPool(
                    host=cls.REDIS_HOST,
                    port=cls.REDIS_PORT,
                    password=cls.REDIS_PASSWORD,
                    db=cls.REDIS_DB,
                    max_connections=cls.REDIS_MAX_CONNECTIONS,
                    socket_timeout=cls.REDIS_SOCKET_TIMEOUT,
                    socket_connect_timeout=cls.REDIS_SOCKET_CONNECT_TIMEOUT,
                    decode_responses=cls.REDIS_DECODE_RESPONSES
                )
                log_info(f"Redis连接池创建成功 - {cls.REDIS_HOST}:{cls.REDIS_PORT}")
            except Exception as e:
                log_error(e, "创建Redis连接池失败")
                raise
        
        return cls._pool
    
    @classmethod
    def get_redis_client(cls) -> redis.Redis:
        """
        获取Redis客户端（单例模式）
        
        Returns:
            redis.Redis: Redis客户端对象
        """
        # 如果Redis客户端不存在，则使用连接池创建
        if cls._redis_client is None:
            try:
                pool = cls.get_connection_pool()
                cls._redis_client = redis.Redis(connection_pool=pool)
                
                # 测试连接
                cls._redis_client.ping()
                log_info("Redis客户端连接成功")
            except redis.ConnectionError as e:
                log_error(e, "Redis连接失败")
                raise
            except Exception as e:
                log_error(e, "创建Redis客户端失败")
                raise
        
        return cls._redis_client
    
    @classmethod
    def close_connection(cls):
        """
        关闭Redis连接
        
        注意：通常不需要手动调用，连接池会自动管理连接
        """
        if cls._redis_client is not None:
            cls._redis_client.close()
            cls._redis_client = None
            log_info("Redis客户端连接已关闭")
        
        if cls._pool is not None:
            cls._pool.disconnect()
            cls._pool = None
            log_info("Redis连接池已断开")

class CacheService:
    """
    缓存服务类
    
    提供常用的缓存操作方法，包括：
    - 基础的get/set/delete操作
    - 支持JSON和对象序列化
    - 批量操作
    - 过期时间管理
    """
    
    def __init__(self):
        """
        初始化缓存服务
        
        自动获取Redis客户端连接
        """
        try:
            self.redis = RedisConfig.get_redis_client()
            self.default_timeout = RedisConfig.CACHE_DEFAULT_TIMEOUT
        except Exception as e:
            log_error(e, "初始化缓存服务失败")
            self.redis = None
    
    def is_available(self) -> bool:
        """
        检查Redis服务是否可用
        
        Returns:
            bool: True表示可用，False表示不可用
        """
        if self.redis is None:
            return False
        
        try:
            self.redis.ping()
            return True
        except:
            return False
    
    # ==================== 基础操作 ====================
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键名
            
        Returns:
            Optional[Any]: 缓存值，如果不存在或出错返回None
        """
        if not self.is_available():
            return None
        
        try:
            value = self.redis.get(key)
            return value
        except Exception as e:
            log_error(e, f"获取缓存失败 - key: {key}")
            return None
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键名
            value: 缓存值
            timeout: 过期时间（秒），None使用默认值
            
        Returns:
            bool: 是否设置成功
        """
        if not self.is_available():
            return False
        
        try:
            # 使用默认超时时间或指定的超时时间
            ex = timeout if timeout is not None else self.default_timeout
            result = self.redis.set(key, value, ex=ex)
            return bool(result)
        except Exception as e:
            log_error(e, f"设置缓存失败 - key: {key}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键名
            
        Returns:
            bool: 是否删除成功
        """
        if not self.is_available():
            return False
        
        try:
            result = self.redis.delete(key)
            return bool(result)
        except Exception as e:
            log_error(e, f"删除缓存失败 - key: {key}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        检查缓存键是否存在
        
        Args:
            key: 缓存键名
            
        Returns:
            bool: 是否存在
        """
        if not self.is_available():
            return False
        
        try:
            return bool(self.redis.exists(key))
        except Exception as e:
            log_error(e, f"检查缓存存在性失败 - key: {key}")
            return False
    
    def expire(self, key: str, timeout: int) -> bool:
        """
        设置缓存过期时间
        
        Args:
            key: 缓存键名
            timeout: 过期时间（秒）
            
        Returns:
            bool: 是否设置成功
        """
        if not self.is_available():
            return False
        
        try:
            result = self.redis.expire(key, timeout)
            return bool(result)
        except Exception as e:
            log_error(e, f"设置缓存过期时间失败 - key: {key}")
            return False
    
    # ==================== JSON操作 ====================
    
    def get_json(self, key: str) -> Optional[Any]:
        """
        获取JSON格式的缓存值
        
        Args:
            key: 缓存键名
            
        Returns:
            Optional[Any]: 反序列化后的Python对象，失败返回None
        """
        value = self.get(key)
        if value is None:
            return None
        
        try:
            return json.loads(value)
        except Exception as e:
            log_error(e, f"反序列化JSON缓存失败 - key: {key}")
            return None
    
    def set_json(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """
        设置JSON格式的缓存值
        
        Args:
            key: 缓存键名
            value: 要序列化的Python对象
            timeout: 过期时间（秒）
            
        Returns:
            bool: 是否设置成功
        """
        try:
            json_value = json.dumps(value, ensure_ascii=False)
            return self.set(key, json_value, timeout)
        except Exception as e:
            log_error(e, f"序列化JSON缓存失败 - key: {key}")
            return False
    
    # ==================== 对象序列化操作 ====================
    
    def get_object(self, key: str) -> Optional[Any]:
        """
        获取序列化的Python对象
        
        使用pickle进行序列化/反序列化
        
        Args:
            key: 缓存键名
            
        Returns:
            Optional[Any]: Python对象，失败返回None
        """
        if not self.is_available():
            return None
        
        try:
            value = self.redis.get(key)
            if value is None:
                return None
            return pickle.loads(value)
        except Exception as e:
            log_error(e, f"反序列化对象缓存失败 - key: {key}")
            return None
    
    def set_object(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """
        设置序列化的Python对象
        
        使用pickle进行序列化
        
        Args:
            key: 缓存键名
            value: Python对象
            timeout: 过期时间（秒）
            
        Returns:
            bool: 是否设置成功
        """
        if not self.is_available():
            return False
        
        try:
            pickled_value = pickle.dumps(value)
            ex = timeout if timeout is not None else self.default_timeout
            result = self.redis.set(key, pickled_value, ex=ex)
            return bool(result)
        except Exception as e:
            log_error(e, f"序列化对象缓存失败 - key: {key}")
            return False
    
    # ==================== 批量操作 ====================
    
    def mget(self, keys: list) -> list:
        """
        批量获取缓存值
        
        Args:
            keys: 缓存键名列表
            
        Returns:
            list: 缓存值列表，不存在的为None
        """
        if not self.is_available():
            return [None] * len(keys)
        
        try:
            return self.redis.mget(keys)
        except Exception as e:
            log_error(e, f"批量获取缓存失败 - keys: {keys}")
            return [None] * len(keys)
    
    def mset(self, mapping: dict, timeout: Optional[int] = None) -> bool:
        """
        批量设置缓存值
        
        Args:
            mapping: 键值对字典 {key: value, ...}
            timeout: 过期时间（秒）
            
        Returns:
            bool: 是否设置成功
        """
        if not self.is_available():
            return False
        
        try:
            # Redis的mset不支持过期时间，需要使用pipeline
            pipe = self.redis.pipeline()
            ex = timeout if timeout is not None else self.default_timeout
            
            for key, value in mapping.items():
                pipe.set(key, value, ex=ex)
            
            pipe.execute()
            return True
        except Exception as e:
            log_error(e, "批量设置缓存失败")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        删除匹配模式的所有键
        
        Args:
            pattern: 键名模式，支持通配符 * 和 ?
            
        Returns:
            int: 删除的键数量
        """
        if not self.is_available():
            return 0
        
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            log_error(e, f"删除缓存模式失败 - pattern: {pattern}")
            return 0
    
    # ==================== 计数器操作 ====================
    
    def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """
        递增计数器
        
        Args:
            key: 计数器键名
            amount: 递增量，默认为1
            
        Returns:
            Optional[int]: 递增后的值，失败返回None
        """
        if not self.is_available():
            return None
        
        try:
            return self.redis.incr(key, amount)
        except Exception as e:
            log_error(e, f"递增计数器失败 - key: {key}")
            return None
    
    def decr(self, key: str, amount: int = 1) -> Optional[int]:
        """
        递减计数器
        
        Args:
            key: 计数器键名
            amount: 递减量，默认为1
            
        Returns:
            Optional[int]: 递减后的值，失败返回None
        """
        if not self.is_available():
            return None
        
        try:
            return self.redis.decr(key, amount)
        except Exception as e:
            log_error(e, f"递减计数器失败 - key: {key}")
            return None

# 创建全局缓存服务实例
cache_service = CacheService()
