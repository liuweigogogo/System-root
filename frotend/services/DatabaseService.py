"""
数据库操作服务
提供数据库连接、表创建、基础CRUD操作等功能
"""

import MySQLdb
import MySQLdb.cursors
import time
from typing import List, Dict, Any, Optional, Tuple
from config.DatabaseConfig import DatabaseConfig
from config.DatabaseSchema import DatabaseSchema
from config.LoggerConfig import log_db, log_error

class DatabaseService:
    """数据库操作服务类"""
    
    def __init__(self):
        """初始化数据库服务"""
        self.db_config = DatabaseConfig()
    
    def get_connection(self) -> Optional[MySQLdb.Connection]:
        """
        获取数据库连接
        
        Returns:
            MySQLdb.Connection: 数据库连接对象，失败返回None
        """
        try:
            return self.db_config.get_connection()
        except Exception as e:
            log_error(e, "获取数据库连接失败")
            return None
    
    def create_tables(self, table_names: Optional[List[str]] = None) -> bool:
        """
        创建数据库表
        
        Args:
            table_names: 要创建的表名列表，None表示创建所有表
            
        Returns:
            bool: 创建是否成功
        """
        start_time = time.time()
        connection = self.get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            
            # 获取要创建的表
            if table_names:
                tables_to_create = {name: sql for name, sql in DatabaseSchema.get_all_tables().items() 
                                  if name in table_names}
            else:
                tables_to_create = DatabaseSchema.get_all_tables()
            
            # 执行创建表语句
            for table_name, sql in tables_to_create.items():
                cursor.execute(sql)
                log_db(f"创建表: {table_name}", table_name, True)
            
            connection.commit()
            
            execution_time = time.time() - start_time
            log_db("批量创建表", f"{len(tables_to_create)}个表", True, execution_time=execution_time)
            return True
            
        except MySQLdb.Error as e:
            execution_time = time.time() - start_time
            log_db("批量创建表", f"{len(tables_to_create)}个表", False, str(e), execution_time)
            log_error(e, "创建数据库表失败")
            return False
        finally:
            connection.close()
    
    def execute_query(self, sql: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """
        执行查询语句
        
        Args:
            sql: SQL查询语句
            params: 查询参数
            
        Returns:
            List[Dict]: 查询结果列表
        """
        connection = self.get_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(sql, params)
            return cursor.fetchall()
        except MySQLdb.Error as e:
            log_error(e, f"执行查询失败: {sql}")
            return []
        finally:
            connection.close()
    
    def execute_update(self, sql: str, params: Optional[Tuple] = None) -> bool:
        """
        执行更新语句（INSERT, UPDATE, DELETE）
        
        Args:
            sql: SQL更新语句
            params: 更新参数
            
        Returns:
            bool: 执行是否成功
        """
        connection = self.get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            cursor.execute(sql, params)
            connection.commit()
            return True
        except MySQLdb.Error as e:
            log_error(e, f"执行更新失败: {sql}")
            return False
        finally:
            connection.close()
    
    def execute_insert(self, sql: str, params: Optional[Tuple] = None) -> Optional[int]:
        """
        执行插入语句并返回新插入记录的ID
        
        Args:
            sql: SQL插入语句
            params: 插入参数
            
        Returns:
            int: 新插入记录的ID，失败返回None
        """
        connection = self.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor()
            cursor.execute(sql, params)
            connection.commit()
            return cursor.lastrowid
        except MySQLdb.Error as e:
            log_error(e, f"执行插入失败: {sql}")
            return None
        finally:
            connection.close()
    
    def check_table_exists(self, table_name: str) -> bool:
        """
        检查表是否存在
        
        Args:
            table_name: 表名
            
        Returns:
            bool: 表是否存在
        """
        sql = """
        SELECT COUNT(*) as count 
        FROM information_schema.tables 
        WHERE table_schema = %s AND table_name = %s
        """
        result = self.execute_query(sql, (self.db_config.DB_NAME, table_name))
        return result[0]['count'] > 0 if result else False
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        获取表结构信息
        
        Args:
            table_name: 表名
            
        Returns:
            List[Dict]: 表结构信息
        """
        sql = """
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY, COLUMN_DEFAULT, EXTRA
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
        """
        return self.execute_query(sql, (self.db_config.DB_NAME, table_name))
    
    def backup_table(self, table_name: str, backup_suffix: str = None) -> bool:
        """
        备份表数据
        
        Args:
            table_name: 表名
            backup_suffix: 备份后缀，默认为时间戳
            
        Returns:
            bool: 备份是否成功
        """
        if not backup_suffix:
            backup_suffix = str(int(time.time()))
        
        backup_table_name = f"{table_name}_backup_{backup_suffix}"
        
        connection = self.get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            
            # 创建备份表
            create_backup_sql = f"CREATE TABLE {backup_table_name} LIKE {table_name}"
            cursor.execute(create_backup_sql)
            
            # 复制数据
            copy_data_sql = f"INSERT INTO {backup_table_name} SELECT * FROM {table_name}"
            cursor.execute(copy_data_sql)
            
            connection.commit()
            log_db(f"备份表: {table_name}", f"备份到: {backup_table_name}", True)
            return True
            
        except MySQLdb.Error as e:
            log_error(e, f"备份表失败: {table_name}")
            return False
        finally:
            connection.close()
