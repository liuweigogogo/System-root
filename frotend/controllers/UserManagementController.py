"""
用户管理控制器
提供用户CRUD操作的RESTful API接口
仅限管理员访问
"""

from flask import Blueprint, request, jsonify
from services.UserManagementService import UserManagementService
from services.PermissionService import admin_required
from config.LoggerConfig import log_info, log_error

# 创建蓝图
user_mgmt_bp = Blueprint('user_management', __name__, url_prefix='/api/users')

# 初始化服务
user_mgmt_service = UserManagementService()


@user_mgmt_bp.route('', methods=['GET'])
@admin_required
def get_users(current_user):
    """
    获取用户列表（分页、搜索、过滤）
    
    Query Parameters:
        page: 页码（默认1）
        page_size: 每页数量（默认10）
        search: 搜索关键词
        role: 角色过滤（'admin' 或 'user'）
    
    Returns:
        JSON响应包含用户列表和分页信息
    """
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        search = request.args.get('search', None, type=str)
        role_filter = request.args.get('role', None, type=str)
        
        # 参数验证
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10
        
        # 获取用户列表
        users, total = user_mgmt_service.get_all_users(page, page_size, search, role_filter)
        
        # 转换为字典列表
        users_data = [user.to_dict() for user in users]
        
        return jsonify({
            'success': True,
            'data': {
                'users': users_data,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total': total,
                    'total_pages': (total + page_size - 1) // page_size
                }
            }
        })
        
    except Exception as e:
        log_error(e, "获取用户列表失败")
        return jsonify({
            'success': False,
            'message': f'获取用户列表失败: {str(e)}'
        }), 500


@user_mgmt_bp.route('/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id, current_user):
    """
    获取单个用户详情
    
    Args:
        user_id: 用户ID
        
    Returns:
        JSON响应包含用户详细信息
    """
    try:
        user = user_mgmt_service.get_user_by_id(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': user.to_dict()
        })
        
    except Exception as e:
        log_error(e, f"获取用户详情失败 - 用户ID: {user_id}")
        return jsonify({
            'success': False,
            'message': f'获取用户详情失败: {str(e)}'
        }), 500


@user_mgmt_bp.route('', methods=['POST'])
@admin_required
def create_user(current_user):
    """
    创建新用户
    
    Request Body:
        username: 用户名（必填）
        password: 密码（必填）
        email: 邮箱（可选）
        role: 角色 'user' 或 'admin'（默认'user'）
        
    Returns:
        JSON响应包含新创建的用户ID
    """
    try:
        data = request.get_json()
        
        # 参数验证
        if not data:
            return jsonify({
                'success': False,
                'message': '请求体不能为空'
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        role = data.get('role', 'user')
        
        if not username:
            return jsonify({
                'success': False,
                'message': '用户名不能为空'
            }), 400
        
        if not password:
            return jsonify({
                'success': False,
                'message': '密码不能为空'
            }), 400
        
        # 创建用户
        success, message, user_id = user_mgmt_service.create_user(
            username, password, email, role
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': {
                    'user_id': user_id
                }
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
    except Exception as e:
        log_error(e, "创建用户失败")
        return jsonify({
            'success': False,
            'message': f'创建用户失败: {str(e)}'
        }), 500


@user_mgmt_bp.route('/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id, current_user):
    """
    更新用户信息
    
    Args:
        user_id: 用户ID
        
    Request Body:
        username: 新用户名（可选）
        email: 新邮箱（可选）
        password: 新密码（可选）
        role: 新角色（可选）
        is_active: 新状态（可选）
        
    Returns:
        JSON响应
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求体不能为空'
            }), 400
        
        # 提取更新字段
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        is_active = data.get('is_active')
        
        # 更新用户
        success, message = user_mgmt_service.update_user(
            user_id, username, email, role, is_active, password
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
    except Exception as e:
        log_error(e, f"更新用户失败 - 用户ID: {user_id}")
        return jsonify({
            'success': False,
            'message': f'更新用户失败: {str(e)}'
        }), 500


@user_mgmt_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id, current_user):
    """
    删除用户
    
    Args:
        user_id: 用户ID
        
    Returns:
        JSON响应
    """
    try:
        # 防止管理员删除自己
        if user_id == current_user.id:
            return jsonify({
                'success': False,
                'message': '不能删除自己的账户'
            }), 400
        
        # 删除用户
        success, message = user_mgmt_service.delete_user(user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
    except Exception as e:
        log_error(e, f"删除用户失败 - 用户ID: {user_id}")
        return jsonify({
            'success': False,
            'message': f'删除用户失败: {str(e)}'
        }), 500


@user_mgmt_bp.route('/statistics', methods=['GET'])
@admin_required
def get_statistics(current_user):
    """
    获取用户统计信息
    
    Returns:
        JSON响应包含统计数据
    """
    try:
        stats = user_mgmt_service.get_user_statistics()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        log_error(e, "获取用户统计信息失败")
        return jsonify({
            'success': False,
            'message': f'获取统计信息失败: {str(e)}'
        }), 500
