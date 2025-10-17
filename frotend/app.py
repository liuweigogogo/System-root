"""
Flask 应用入口 - 重构版本
只负责路由定义和控制器调用，具体业务逻辑分离到各个控制器中
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from config.DatabaseConfig import DatabaseConfig
from config.LoggerConfig import log_access, log_error, log_security
from controllers import AuthController, LogController, PageController, DatabaseController, FileConverterController
from controllers.UserManagementController import user_mgmt_bp
import os
import shutil

# 创建Flask应用
app = Flask(__name__)
app.secret_key = DatabaseConfig.SECRET_KEY
CORS(app)  # 允许跨域请求

# 注册蓝图
app.register_blueprint(user_mgmt_bp)

# 初始化控制器
auth_controller = AuthController()
log_controller = LogController()
page_controller = PageController()
db_controller = DatabaseController()
file_converter_controller = FileConverterController()

# ===== 中间件 =====

def get_client_ip():
    """获取客户端真实IP地址"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

@app.before_request
def log_request():
    """记录请求日志"""
    client_ip = get_client_ip()
    user_agent = request.headers.get('User-Agent', '')
    user_id = session.get('user_id')
    
    log_access(
        method=request.method,
        path=request.path,
        ip_address=client_ip,
        user_agent=user_agent,
        user_id=user_id
    )

@app.errorhandler(Exception)
def handle_exception(e):
    """全局异常处理"""
    client_ip = get_client_ip()
    user_id = session.get('user_id')
    
    log_error(e, f"请求路径: {request.path}, 方法: {request.method}", user_id)
    log_security("系统异常", f"未处理的异常: {str(e)}", client_ip, user_id)
    
    return jsonify({
        'success': False,
        'message': '服务器内部错误'
    }), 500

# ===== 页面路由 =====

@app.route('/')
def index():
    """主页 - 重定向到登录页面"""
    return page_controller.index()

@app.route('/login', methods=['GET'])
def login_page():
    """登录页面"""
    return page_controller.login_page()

@app.route('/dashboard')
def dashboard():
    """用户仪表板"""
    return page_controller.dashboard()

@app.route('/logs')
def logs_page():
    """日志管理页面"""
    return page_controller.logs_page()

@app.route('/converter')
def converter_page():
    """文件转换页面"""
    return page_controller.converter_page()

# ===== 认证API路由 =====

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录API，这个最终返回的是JSON数据包含主页URL"""
    response_data, status_code = auth_controller.login()
    return jsonify(response_data), status_code

@app.route('/api/register', methods=['POST'])
def register():
    """用户注册API"""
    response_data, status_code = auth_controller.register()
    return jsonify(response_data), status_code

@app.route('/api/logout', methods=['POST'])
def logout():
    """用户登出API"""
    response_data, status_code = auth_controller.logout()
    return jsonify(response_data), status_code

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    """检查用户认证状态"""
    response_data, status_code = auth_controller.check_auth()
    return jsonify(response_data), status_code

@app.route('/api/captcha', methods=['GET'])
def get_captcha():
    """获取验证码"""
    response_data, status_code = auth_controller.get_captcha()
    return jsonify(response_data), status_code

# ===== 日志管理API路由 =====

@app.route('/api/logs')
def get_logs():
    """获取日志API"""
    response_data, status_code = log_controller.get_logs()
    return jsonify(response_data), status_code

@app.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    """清空日志API"""
    response_data, status_code = log_controller.clear_logs()
    return jsonify(response_data), status_code

@app.route('/api/logs/download')
def download_logs():
    """下载日志API"""
    return log_controller.download_logs()

# ===== 数据库API路由 =====

@app.route('/api/init-db', methods=['POST'])
def init_database():
    """初始化数据库表"""
    response_data, status_code = db_controller.init_database()
    return jsonify(response_data), status_code

# ===== 文件转换API路由 =====

@app.route('/api/convert/supported', methods=['GET'])
def get_supported_conversions():
    """获取支持的转换格式"""
    response_data, status_code = file_converter_controller.get_supported_conversions()
    return jsonify(response_data), status_code

@app.route('/api/convert/single', methods=['POST'])
def convert_single_file():
    """单文件转换"""
    response_data, status_code = file_converter_controller.convert_file()
    return jsonify(response_data), status_code

@app.route('/api/convert/batch', methods=['POST'])
def convert_batch_files():
    """批量文件转换"""
    response_data, status_code = file_converter_controller.batch_convert()
    return jsonify(response_data), status_code

@app.route('/api/convert/info', methods=['POST'])
def get_file_info():
    """获取文件信息"""
    response_data, status_code = file_converter_controller.get_file_info()
    return jsonify(response_data), status_code

@app.route('/api/convert/download/<filename>')
def download_converted_file(filename):
    """下载转换后的文件"""
    return file_converter_controller.download_converted_file(filename)

@app.route('/api/convert/cleanup', methods=['POST'])
def cleanup_temp_files():
    """清理临时文件"""
    response_data, status_code = file_converter_controller.cleanup_temp_files()
    return jsonify(response_data), status_code

# ===== 静态资源路由 =====

@app.route('/css/<path:filename>')
def static_css(filename):
    """提供CSS文件"""
    return page_controller.serve_css(filename)

@app.route('/js/<path:filename>')
def static_js(filename):
    """提供JavaScript文件"""
    return page_controller.serve_js(filename)

@app.route('/assets/<path:filename>')
def static_assets(filename):
    """提供静态资源（图片等）"""
    return page_controller.serve_assets(filename)

@app.route('/favicon.ico')
def favicon():
    """提供网站图标"""
    return page_controller.serve_favicon()

# ===== 特殊路由 =====

@app.route('/.well-known/appspecific/com.chrome.devtools.json')
def chrome_probe():
    """Chrome开发者工具探测"""
    return page_controller.chrome_probe()

# ===== 应用启动 =====

if __name__ == '__main__':
    # 确保模板目录存在
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # 将index.html移动到templates目录
    if os.path.exists('index.html'):
        shutil.copy('index.html', 'templates/index.html')
    
    app.run(debug=True, host='127.0.0.1', port=5000)