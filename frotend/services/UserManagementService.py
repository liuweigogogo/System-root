"""
用户管理服务
提供用户的增删改查功能（仅限管理员）
"""

from typing import Optional, Tuple, List, Dict, Any
from model.BaseUser import BaseUser
from services.DatabaseService import DatabaseService
from config.DatabaseConfig import DatabaseConfig
from config.LoggerConfig import log_info, log_error, log_security

class UserManagementService:
    """用户管理服务类"""
    
    def __init__(self):
        """初始化用户管理服务"""
        self.db_service = DatabaseService()
        self.db_config = DatabaseConfig()
    
    def get_all_users(self, page: int = 1, page_size: int = 10, 
                      search: Optional[str] = None, role_filter: Optional[str] = None) -> Tuple[List[BaseUser], int]:
        """
        获取所有用户列表（分页）
        
        Args:
            page: 页码（从1开始）
            page_size: 每页数量
            search: 搜索关键词（用户名或邮箱）
            role_filter: 角色过滤（'admin' 或 'user'）
            
        Returns:
            Tuple[List[BaseUser], int]: (用户列表, 总数量)
        """
        try:
            # 构建查询条件
            conditions = []
            params = []
            
            if search:
                conditions.append("(username LIKE %s OR email LIKE %s)")
                search_pattern = f"%{search}%"
                params.extend([search_pattern, search_pattern])
            
            if role_filter and role_filter in ['admin', 'user']:
                conditions.append("role = %s")
                params.append(role_filter)
            
            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
            
            # 查询总数
            count_sql = f"SELECT COUNT(*) as total FROM users {where_clause}"
            count_result = self.db_service.execute_query(count_sql, tuple(params))
            total = count_result[0]['total'] if count_result else 0
            
            # 查询用户列表
            offset = (page - 1) * page_size
            sql = f"""
            SELECT id, username, email, role, is_active, created_at, last_login
            FROM users 
            {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """
            params.extend([page_size, offset])
            results = self.db_service.execute_query(sql, tuple(params))
            
            # 转换为用户对象列表
            users = []
            for row in results:
                user = BaseUser()
                user.from_dict(row)
                users.append(user)
            
            log_info(f"获取用户列表成功", f"页码: {page}, 数量: {len(users)}, 总数: {total}")
            return users, total
            
        except Exception as e:
            log_error(e, "获取用户列表失败")
            return [], 0
    
    def get_user_by_id(self, user_id: int) -> Optional[BaseUser]:
        """
        根据ID获取用户详情
        
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
            log_error(e, f"获取用户详情失败 - 用户ID: {user_id}")
            return None
    
    def create_user(self, username: str, password: str, email: Optional[str] = None, 
                   role: str = 'user') -> Tuple[bool, str, Optional[int]]:
        """
        创建新用户
        
        Args:
            username: 用户名
            password: 密码
            email: 邮箱地址
            role: 用户角色（'user' 或 'admin'）
            
        Returns:
            Tuple[bool, str, Optional[int]]: (是否成功, 消息, 用户ID)
        """
        try:
            # 验证角色
            if role not in ['user', 'admin']:
                return False, "无效的用户角色", None
            
            # 检查用户名是否已存在
            check_sql = "SELECT id FROM users WHERE username = %s"
            existing = self.db_service.execute_query(check_sql, (username,))
            if existing:
                return False, "用户名已存在", None
            
            # 检查邮箱是否已存在
            if email:
                email_check_sql = "SELECT id FROM users WHERE email = %s"
                existing_email = self.db_service.execute_query(email_check_sql, (email,))
                if existing_email:
                    return False, "邮箱已被使用", None
            
            # 加密密码
            password_hash = self.db_config.hash_password(password)
            
            # 插入新用户
            sql = """
            INSERT INTO users (username, password_hash, email, role) 
            VALUES (%s, %s, %s, %s)
            """
            user_id = self.db_service.execute_insert(sql, (username, password_hash, email, role))
            
            if user_id:
                log_info(f"创建用户成功", f"用户名: {username}, 角色: {role}, ID: {user_id}")
                return True, "用户创建成功", user_id
            else:
                return False, "创建用户失败", None
                
        except Exception as e:
            log_error(e, f"创建用户失败 - 用户名: {username}")
            return False, f"创建用户失败: {str(e)}", None
    
    def update_user(self, user_id: int, username: Optional[str] = None, 
                   email: Optional[str] = None, role: Optional[str] = None, 
                   is_active: Optional[bool] = None, password: Optional[str] = None) -> Tuple[bool, str]:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            username: 新用户名
            email: 新邮箱
            role: 新角色
            is_active: 新状态
            password: 新密码
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 检查用户是否存在
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在"
            
            # 构建更新语句
            updates = []
            params = []
            
            if username is not None:
                # 检查新用户名是否已被使用
                check_sql = "SELECT id FROM users WHERE username = %s AND id != %s"
                existing = self.db_service.execute_query(check_sql, (username, user_id))
                if existing:
                    return False, "用户名已被使用"
                updates.append("username = %s")
                params.append(username)
            
            if email is not None:
                # 检查新邮箱是否已被使用
                check_sql = "SELECT id FROM users WHERE email = %s AND id != %s"
                existing = self.db_service.execute_query(check_sql, (email, user_id))
                if existing:
                    return False, "邮箱已被使用"
                updates.append("email = %s")
                params.append(email)
            
            if role is not None:
                if role not in ['user', 'admin']:
                    return False, "无效的用户角色"
                updates.append("role = %s")
                params.append(role)
            
            if is_active is not None:
                updates.append("is_active = %s")
                params.append(is_active)
            
            if password is not None:
                password_hash = self.db_config.hash_password(password)
                updates.append("password_hash = %s")
                params.append(password_hash)
            
            if not updates:
                return False, "没有需要更新的字段"
            
            # 执行更新
            params.append(user_id)
            sql = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            
            if self.db_service.execute_update(sql, tuple(params)):
                log_info(f"更新用户信息成功", f"用户ID: {user_id}")
                return True, "用户信息更新成功"
            else:
                return False, "更新用户信息失败"
                
        except Exception as e:
            log_error(e, f"更新用户信息失败 - 用户ID: {user_id}")
            return False, f"更新用户信息失败: {str(e)}"
    
    def delete_user(self, user_id: int) -> Tuple[bool, str]:
        """
        删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 检查用户是否存在
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在"
            
            # 不允许删除管理员账户（可根据需要调整）
            if user.role == 'admin':
                # 检查是否是最后一个管理员
                admin_count_sql = "SELECT COUNT(*) as count FROM users WHERE role = 'admin'"
                result = self.db_service.execute_query(admin_count_sql)
                if result and result[0]['count'] <= 1:
                    return False, "不能删除最后一个管理员账户"
            
            # 删除用户（会级联删除相关会话）
            sql = "DELETE FROM users WHERE id = %s"
            
            if self.db_service.execute_update(sql, (user_id,)):
                log_security("删除用户", f"用户ID: {user_id}, 用户名: {user.username}")
                return True, "用户删除成功"
            else:
                return False, "删除用户失败"
                
        except Exception as e:
            log_error(e, f"删除用户失败 - 用户ID: {user_id}")
            return False, f"删除用户失败: {str(e)}"
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """
        获取用户统计信息
        
        Returns:
            Dict[str, Any]: 统计信息字典
        """
        try:
            stats = {}
            
            # 总用户数
            total_sql = "SELECT COUNT(*) as count FROM users"
            result = self.db_service.execute_query(total_sql)
            stats['total_users'] = result[0]['count'] if result else 0
            
            # 管理员数量
            admin_sql = "SELECT COUNT(*) as count FROM users WHERE role = 'admin'"
            result = self.db_service.execute_query(admin_sql)
            stats['admin_count'] = result[0]['count'] if result else 0
            
            # 活跃用户数
            active_sql = "SELECT COUNT(*) as count FROM users WHERE is_active = TRUE"
            result = self.db_service.execute_query(active_sql)
            stats['active_users'] = result[0]['count'] if result else 0
            
            # 本月新增用户
            month_sql = "SELECT COUNT(*) as count FROM users WHERE created_at >= DATE_FORMAT(NOW(), '%Y-%m-01')"
            result = self.db_service.execute_query(month_sql)
            stats['new_this_month'] = result[0]['count'] if result else 0
            
            # 在线用户数（从活跃会话统计）
            online_sql = """
            SELECT COUNT(DISTINCT user_id) as count 
            FROM user_sessions 
            WHERE is_active = TRUE AND expires_at > NOW()
            """
            result = self.db_service.execute_query(online_sql)
            stats['online_users'] = result[0]['count'] if result else 0
            
            return stats
            
        except Exception as e:
            log_error(e, "获取用户统计信息失败")
            return {
                'total_users': 0,
                'admin_count': 0,
                'active_users': 0,
                'new_this_month': 0,
                'online_users': 0
            }
