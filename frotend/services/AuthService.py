"""
用户认证服务
提供用户注册、登录验证、密码管理等功能
"""

import time
from typing import Optional, Tuple
from model.BaseUser import BaseUser
from services.DatabaseService import DatabaseService
from config.DatabaseConfig import DatabaseConfig
from config.LoggerConfig import log_auth, log_error, log_security,log_info

class AuthService:
    """用户认证服务类"""
    
    def __init__(self):
        """初始化认证服务"""
        self.db_service = DatabaseService()
        self.db_config = DatabaseConfig()
    
    def register_user(self, username: str, password: str, email: Optional[str] = None) -> Tuple[bool, str]:
        """
        注册新用户
        
        Args:
            username: 用户名
            password: 密码
            email: 邮箱地址
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        start_time = time.time()
        
        try:
            # 检查用户名是否已存在
            if self._user_exists(username):
                log_auth("用户注册", username, success=False, extra_info="用户名已存在")
                return False, "用户名已存在"
            
            # 验证输入参数
            validation_result = self._validate_user_input(username, password, email)
            if not validation_result[0]:
                return validation_result
            
            # 加密密码
            password_hash = self.db_config.hash_password(password)
            
            # 插入新用户
            sql = """
            INSERT INTO users (username, password_hash, email) 
            VALUES (%s, %s, %s)
            """
            user_id = self.db_service.execute_insert(sql, (username, password_hash, email))
            
            if user_id:
                execution_time = time.time() - start_time
                log_auth("用户注册", username, success=True, extra_info=f"邮箱: {email}")
                return True, "用户创建成功"
            else:
                return False, "创建用户失败"
                
        except Exception as e:
            log_error(e, f"用户注册失败 - 用户名: {username}")
            return False, f"注册失败: {str(e)}"
    
    def authenticate_user(self, username: str, password: str, ip_address: Optional[str] = None) -> Tuple[bool, Optional[BaseUser], str]:
        """
        验证用户登录
        
        Args:
            username: 用户名
            password: 密码
            ip_address: IP地址
            
        Returns:
            Tuple[bool, Optional[BaseUser], str]: (是否成功, 用户对象, 消息)
        """
        start_time = time.time()
        
        try:
            # 查询用户信息
            sql = """
            SELECT id, username, password_hash, email, role, is_active, created_at, last_login
            FROM users 
            WHERE username = %s
            """
            # 传入从前端获取的用户名，在数据库中查询对应的用户信息。返回用户信息
            result = self.db_service.execute_query(sql, (username,))
            log_info('根据前端表单输入的账号查询用户信息',result)
            
            if not result:
                log_auth("用户登录", username, ip_address, success=False, extra_info="用户名不存在")
                log_security("登录尝试", f"用户名不存在: {username}", ip_address)
                return False, None, "用户名不存在"
            
            user_data = result[0]
            
            # 检查账户状态
            if not user_data['is_active']:
                log_auth("用户登录", username, ip_address, success=False, extra_info="账户已被禁用")
                log_security("登录尝试", f"禁用账户登录尝试: {username}", ip_address, user_data['id'])
                return False, None, "账户已被禁用"

            # 验证密码,判断密码是否正确
            if not self.db_config.verify_password(password, user_data['password_hash']):
                log_auth("用户登录", username, ip_address, success=False, extra_info="密码错误")
                log_security("登录尝试", f"密码错误: {username}", ip_address, user_data['id'])
                return False, None, "密码错误"
            else:
                log_info('密码验证通过',None)
            # 更新最后登录时间,更新用户最后登录时间
            self._update_last_login(user_data['id'])
            
            # 创建用户对象
            user = BaseUser()
            user.from_dict(user_data)
            
            execution_time = time.time() - start_time
            log_info('登录耗费时间',execution_time)
            log_auth("用户登录", username, ip_address, success=True, extra_info=f"用户ID: {user_data['id']}")
            
            return True, user, "登录成功"
            
        except Exception as e:
            log_error(e, f"用户认证失败 - 用户名: {username}")
            log_auth("用户登录", username, ip_address, success=False, extra_info=f"数据库错误: {e}")
            return False, None, f"认证失败: {str(e)}"
    
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
        try:
            # 验证旧密码
            sql = "SELECT password_hash FROM users WHERE id = %s"
            result = self.db_service.execute_query(sql, (user_id,))
            
            if not result:
                return False, "用户不存在"
            
            if not self.db_config.verify_password(old_password, result[0]['password_hash']):
                return False, "旧密码错误"
            
            # 验证新密码
            validation_result = self._validate_password(new_password)
            if not validation_result[0]:
                return validation_result
            
            # 更新密码
            new_password_hash = self.db_config.hash_password(new_password)
            update_sql = "UPDATE users SET password_hash = %s WHERE id = %s"
            
            if self.db_service.execute_update(update_sql, (new_password_hash, user_id)):
                log_auth("修改密码", f"用户ID: {user_id}", success=True)
                return True, "密码修改成功"
            else:
                return False, "密码修改失败"
                
        except Exception as e:
            log_error(e, f"修改密码失败 - 用户ID: {user_id}")
            return False, f"修改密码失败: {str(e)}"
    
    def get_user_by_id(self, user_id: int) -> Optional[BaseUser]:
        """
        根据用户ID获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[BaseUser]: 用户对象，不存在返回None
        """
        try:
            sql = """
            SELECT id, username, email, role, is_active, created_at, last_login
            FROM users 
            WHERE id = %s
            """
            result = self.db_service.execute_query(sql, (user_id,))
            
            if result:
                user = BaseUser()
                user.from_dict(result[0])
                return user
            return None
            
        except Exception as e:
            log_error(e, f"获取用户信息失败 - 用户ID: {user_id}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[BaseUser]:
        """
        根据用户名获取用户信息
        
        Args:
            username: 用户名
            
        Returns:
            Optional[BaseUser]: 用户对象，不存在返回None
        """
        try:
            sql = """
            SELECT id, username, email, role, is_active, created_at, last_login
            FROM users 
            WHERE username = %s
            """
            result = self.db_service.execute_query(sql, (username,))
            
            if result:
                user = BaseUser()
                user.from_dict(result[0])
                return user
            return None
            
        except Exception as e:
            log_error(e, f"获取用户信息失败 - 用户名: {username}")
            return None
    
    def _user_exists(self, username: str) -> bool:
        """
        检查用户名是否存在
        
        Args:
            username: 用户名
            
        Returns:
            bool: 是否存在
        """
        sql = "SELECT COUNT(*) as count FROM users WHERE username = %s"
        result = self.db_service.execute_query(sql, (username,))
        return result[0]['count'] > 0 if result else False
    
    def _validate_user_input(self, username: str, password: str, email: Optional[str] = None) -> Tuple[bool, str]:
        """
        验证用户输入参数
        
        Args:
            username: 用户名
            password: 密码
            email: 邮箱
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误消息)
        """
        # 验证用户名
        if not username or len(username.strip()) < 3:
            return False, "用户名至少3个字符"
        
        # 验证密码
        password_validation = self._validate_password(password)
        if not password_validation[0]:
            return password_validation
        
        # 验证邮箱（如果提供）
        if email and not self._validate_email(email):
            return False, "邮箱格式不正确"
        
        return True, ""
    
    def _validate_password(self, password: str) -> Tuple[bool, str]:
        """
        验证密码强度
        
        Args:
            password: 密码
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误消息)
        """
        if not password or len(password) < 6:
            return False, "密码至少6个字符"
        
        if len(password) > 128:
            return False, "密码不能超过128个字符"
        
        return True, ""
    
    def _validate_email(self, email: str) -> bool:
        """
        验证邮箱格式
        
        Args:
            email: 邮箱地址
            
        Returns:
            bool: 是否有效
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _update_last_login(self, user_id: int) -> bool:
        """
        更新用户最后登录时间
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否成功
        """
        sql = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s"
        return self.db_service.execute_update(sql, (user_id,))
