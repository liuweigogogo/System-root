"""
数据库表结构配置模块
包含所有数据库表的创建语句和索引定义
"""

class DatabaseSchema:
    """数据库表结构配置类"""
    
    # ===== 用户相关表结构 =====
    
    @staticmethod
    def get_users_table_sql():
        """获取用户表创建SQL语句"""
        return """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            email VARCHAR(100),
            role ENUM('user', 'admin') DEFAULT 'user' NOT NULL COMMENT '用户角色：user-普通用户，admin-管理员',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP NULL,
            is_active BOOLEAN DEFAULT TRUE,
            INDEX idx_username (username),
            INDEX idx_email (email),
            INDEX idx_role (role),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    
    @staticmethod
    def get_user_sessions_table_sql():
        """获取用户会话表创建SQL语句"""
        return """
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            session_token VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            ip_address VARCHAR(45),
            user_agent TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_session_token (session_token),
            INDEX idx_expires_at (expires_at),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    
    # ===== 系统配置表结构 =====
    
    @staticmethod
    def get_system_config_table_sql():
        """获取系统配置表创建SQL语句"""
        return """
        CREATE TABLE IF NOT EXISTS system_config (
            id INT AUTO_INCREMENT PRIMARY KEY,
            config_key VARCHAR(100) UNIQUE NOT NULL,
            config_value TEXT,
            description VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_config_key (config_key)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    
    # ===== 操作日志表结构 =====
    
    @staticmethod
    def get_operation_logs_table_sql():
        """获取操作日志表创建SQL语句"""
        return """
        CREATE TABLE IF NOT EXISTS operation_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            operation_type VARCHAR(50) NOT NULL,
            operation_desc TEXT,
            ip_address VARCHAR(45),
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
            INDEX idx_user_id (user_id),
            INDEX idx_operation_type (operation_type),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    
    # ===== 获取所有表创建语句 =====
    
    @staticmethod
    def get_all_tables():
        """获取所有表的创建语句"""
        return {
            'users': DatabaseSchema.get_users_table_sql(),
            'user_sessions': DatabaseSchema.get_user_sessions_table_sql(),
            'system_config': DatabaseSchema.get_system_config_table_sql(),
            'operation_logs': DatabaseSchema.get_operation_logs_table_sql()
        }
    
    @staticmethod
    def get_user_related_tables():
        """获取用户相关表的创建语句"""
        return {
            'users': DatabaseSchema.get_users_table_sql(),
            'user_sessions': DatabaseSchema.get_user_sessions_table_sql()
        }
