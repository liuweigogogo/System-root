"""
数据库控制器
处理数据库初始化等数据库相关功能
"""

from typing import Dict, Any
from model.UserModel import UserModel
from config.LoggerConfig import log_info, log_error

class DatabaseController:
    """数据库控制器类"""
    
    def __init__(self):
        """初始化数据库控制器"""
        self.user_model = UserModel()
    
    def init_database(self) -> tuple[Dict[str, Any], int]:
        """
        初始化数据库表
        
        Returns:
            Tuple[Dict, int]: (响应数据, HTTP状态码)
        """
        try:
            log_info("开始初始化数据库")
            success = self.user_model.create_tables()
            
            if success:
                log_info("数据库初始化成功")
                return {
                    'success': True,
                    'message': '数据库初始化成功'
                }, 200
            else:
                log_error("数据库初始化失败", "数据库表创建失败")
                return {
                    'success': False,
                    'message': '数据库初始化失败'
                }, 500
                
        except Exception as e:
            log_error(e, "数据库初始化异常")
            return {
                'success': False,
                'message': f'数据库初始化失败: {str(e)}'
            }, 500
