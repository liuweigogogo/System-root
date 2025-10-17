"""
页面渲染控制器
处理页面渲染和静态资源服务
"""

from flask import render_template, redirect, send_from_directory
from typing import Union
from model.UserModel import UserModel
from config.LoggerConfig import log_info, log_error

class PageController:
    """页面渲染控制器类"""
    
    def __init__(self):
        """初始化页面控制器"""
        self.user_model = UserModel()
    
    def index(self) -> str:
        """
        主页 - 重定向到登录页面
        
        Returns:
            str: 重定向响应
        """
        return redirect('/login')
    
    def login_page(self) -> str:
        """
        登录页面
        
        Returns:
            str: 登录页面HTML
        """
        return render_template('index.html')
    
    def dashboard(self) -> Union[str, redirect]:
        """
        用户仪表板页面
        
        Returns:
            Union[str, redirect]: 仪表板页面HTML或重定向到登录页
        """
        # 检查认证状态
        session_token = self._get_session_token()
        if not session_token:
            return redirect('/login')
        
        is_valid, user_id = self.user_model.validate_session(session_token)
        if not is_valid:
            self._clear_session()
            return redirect('/login')
        
        return render_template('dashboard.html')
    
    def logs_page(self) -> Union[str, redirect]:
        """
        日志管理页面
        
        Returns:
            Union[str, redirect]: 日志页面HTML或重定向到登录页
        """
        # 检查认证状态
        session_token = self._get_session_token()
        if not session_token:
            return redirect('/login')
        
        is_valid, user_id = self.user_model.validate_session(session_token)
        if not is_valid:
            self._clear_session()
            return redirect('/login')
        
        return render_template('logs.html')
    
    def converter_page(self) -> Union[str, redirect]:
        """
        文件转换页面
        
        Returns:
            Union[str, redirect]: 转换页面HTML或重定向到登录页
        """
        # 检查认证状态
        session_token = self._get_session_token()
        if not session_token:
            return redirect('/login')
        
        is_valid, user_id = self.user_model.validate_session(session_token)
        if not is_valid:
            self._clear_session()
            return redirect('/login')
        
        return render_template('file_converter.html')
    
    def serve_css(self, filename: str) -> str:
        """
        提供CSS文件
        
        Args:
            filename: CSS文件名
            
        Returns:
            str: CSS文件内容
        """
        try:
            return send_from_directory('css', filename)
        except Exception as e:
            log_error(e, f"提供CSS文件失败: {filename}")
            return "CSS文件不存在", 404
    
    def serve_js(self, filename: str) -> str:
        """
        提供JavaScript文件
        
        Args:
            filename: JS文件名
            
        Returns:
            str: JS文件内容
        """
        try:
            return send_from_directory('js', filename)
        except Exception as e:
            log_error(e, f"提供JS文件失败: {filename}")
            return "JS文件不存在", 404
    
    def serve_assets(self, filename: str) -> str:
        """
        提供静态资源文件
        
        Args:
            filename: 资源文件名
            
        Returns:
            str: 资源文件内容
        """
        try:
            return send_from_directory('assets', filename)
        except Exception as e:
            log_error(e, f"提供静态资源失败: {filename}")
            return "资源文件不存在", 404
    
    def serve_favicon(self) -> str:
        """
        提供网站图标
        
        Returns:
            str: 网站图标文件
        """
        try:
            return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')
        except Exception as e:
            log_error(e, "提供网站图标失败")
            return "图标文件不存在", 404
    
    def chrome_probe(self) -> tuple[str, int]:
        """
        Chrome开发者工具探测
        
        Returns:
            Tuple[str, int]: 空响应和204状态码
        """
        return ('', 204)
    
    def _get_session_token(self) -> str:
        """
        获取会话令牌
        
        Returns:
            str: 会话令牌
        """
        from flask import session
        return session.get('session_token')
    
    def _clear_session(self) -> None:
        """
        清除会话
        """
        from flask import session
        session.clear()
