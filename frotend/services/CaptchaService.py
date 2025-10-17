"""
验证码服务
提供验证码生成、验证等功能
"""

import random
import string
import time
from typing import Tuple, Optional
from config.LoggerConfig import log_info, log_error

class CaptchaService:
    """验证码服务类"""
    
    def __init__(self):
        """初始化验证码服务"""
        # 存储验证码的字典 {session_id: {'code': code, 'expires': timestamp}}
        self.captcha_storage = {}
        self.captcha_expire_time = 300  # 验证码5分钟过期
    
    def generate_captcha(self, session_id: str) -> Tuple[str, str]:
        """
        生成验证码
        
        Args:
            session_id: 会话ID
            
        Returns:
            Tuple[str, str]: (验证码文本, 验证码图片数据)
        """
        try:
            # 生成4位随机验证码
            captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            
            # 存储验证码
            self.captcha_storage[session_id] = {
                'code': captcha_text,
                'expires': time.time() + self.captcha_expire_time
            }
            
            # 生成验证码图片（简化版，返回文本）
            # 在实际应用中，这里应该生成图片
            log_info(f"生成验证码 - 会话ID: {session_id}, 验证码: {captcha_text}")
            
            return captcha_text, captcha_text  # 暂时返回文本，实际应该返回图片数据
            
        except Exception as e:
            log_error(e, f"生成验证码失败 - 会话ID: {session_id}")
            return "", ""
    
    def verify_captcha(self, session_id: str, input_code: str) -> bool:
        """
        验证验证码
        
        Args:
            session_id: 会话ID
            input_code: 用户输入的验证码
            
        Returns:
            bool: 验证是否成功
        """
        try:
            # 清理过期验证码
            self._cleanup_expired_captchas()
            
            # 检查验证码是否存在
            if session_id not in self.captcha_storage:
                log_info(f"验证码验证失败 - 会话ID: {session_id}, 原因: 验证码不存在")
                return False
            
            stored_data = self.captcha_storage[session_id]
            
            # 检查是否过期
            if time.time() > stored_data['expires']:
                del self.captcha_storage[session_id]
                log_info(f"验证码验证失败 - 会话ID: {session_id}, 原因: 验证码已过期")
                return False
            
            # 验证码比较（不区分大小写）
            is_valid = stored_data['code'].upper() == input_code.upper()
            
            if is_valid:
                # 验证成功后删除验证码（一次性使用）
                del self.captcha_storage[session_id]
                log_info(f"验证码验证成功 - 会话ID: {session_id}")
            else:
                log_info(f"验证码验证失败 - 会话ID: {session_id}, 输入: {input_code}, 正确: {stored_data['code']}")
            
            return is_valid
            
        except Exception as e:
            log_error(e, f"验证码验证异常 - 会话ID: {session_id}")
            return False
    
    def get_captcha_text(self, session_id: str) -> Optional[str]:
        """
        获取验证码文本（用于测试）
        
        Args:
            session_id: 会话ID
            
        Returns:
            Optional[str]: 验证码文本，不存在返回None
        """
        if session_id in self.captcha_storage:
            return self.captcha_storage[session_id]['code']
        return None
    
    def _cleanup_expired_captchas(self):
        """清理过期的验证码"""
        current_time = time.time()
        expired_sessions = [
            session_id for session_id, data in self.captcha_storage.items()
            if current_time > data['expires']
        ]
        
        for session_id in expired_sessions:
            del self.captcha_storage[session_id]
        
        if expired_sessions:
            log_info(f"清理过期验证码 - 数量: {len(expired_sessions)}")
    
    def get_captcha_count(self) -> int:
        """
        获取当前存储的验证码数量
        
        Returns:
            int: 验证码数量
        """
        return len(self.captcha_storage)
