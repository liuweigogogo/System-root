import pymysql
import hashlib
import secrets
import os
import time
from .LoggerConfig import log_db, log_error

# 使用pymysql替代MySQLdb
pymysql.install_as_MySQLdb()

# 创建数据库类，初始化数据库配置
class DatabaseConfig:
    MYSQL_HOST = os.environ.get('DB_HOST', 'localhost')
    MYSQL_USER = os.environ.get('DB_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('DB_PASSWORD', '123456')
    MYSQL_DB = os.environ.get('DB_NAME', 'file_converter')
    DB_NAME = os.environ.get('DB_NAME', 'file_converter')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a05ab64b33707b594e053d99537e300ef29295684c8ceeb03655a3d03aa01c55')
    
    @staticmethod
    def get_connection():
        """获取数据库连接"""
        start_time = time.time()
        try:
            connection = pymysql.connect(
                host=DatabaseConfig.MYSQL_HOST,
                user=DatabaseConfig.MYSQL_USER,
                password=DatabaseConfig.MYSQL_PASSWORD,
                database=DatabaseConfig.MYSQL_DB,
                charset='utf8mb4'
            )
            execution_time = time.time() - start_time
            log_db("连接数据库", "connection", True, execution_time=execution_time)
            return connection
        except pymysql.Error as e:
            execution_time = time.time() - start_time
            log_db("连接数据库", "connection", False, str(e), execution_time)
            log_error(e, "数据库连接失败")
            return None
    
    @staticmethod
    def hash_password(password):
        """密码哈希加密"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    @staticmethod
    def verify_password(password, stored_hash):
        """验证密码"""
        try:
            salt, hash_value = stored_hash.split(':')
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            print(password_hash.hex()== hash_value)
            return password_hash.hex() == hash_value
        except:
            return False

