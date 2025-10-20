#!/bin/bash

# 项目部署脚本
# 使用方法：bash deploy.sh [start|stop|restart|logs|status]

set -e

PROJECT_NAME="flask-file-converter"
COMPOSE_FILE="docker-compose.yml"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Docker 和 Docker Compose 是否安装
check_dependencies() {
    print_info "检查依赖..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    # 检查 Docker Compose（兼容新旧版本）
    if docker compose version &> /dev/null; then
        DOCKER_COMPOSE="docker compose"
        print_info "检测到 Docker Compose V2 (docker compose)"
    elif command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
        print_info "检测到 Docker Compose V1 (docker-compose)"
    else
        print_error "Docker Compose 未安装"
        print_info "请运行以下命令安装："
        print_info "  sudo apt install docker-compose-plugin"
        print_info "或访问: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    print_info "依赖检查通过 - 使用: ${DOCKER_COMPOSE}"
}

# 创建必要的目录
create_directories() {
    print_info "创建必要的目录..."
    mkdir -p logs uploads nginx/ssl
    print_info "目录创建完成"
}

# 检查环境变量文件
check_env_file() {
    if [ ! -f .env ]; then
        print_warn ".env 文件不存在，从 .env.example 复制..."
        if [ -f .env.example ]; then
            cp .env.example .env
            print_warn "请编辑 .env 文件，配置正确的数据库密码和其他参数"
            exit 1
        else
            print_error ".env.example 文件不存在"
            exit 1
        fi
    fi
}

# 启动服务
start_services() {
    print_info "启动 ${PROJECT_NAME} 服务..."
    check_dependencies
    create_directories
    check_env_file
    
    ${DOCKER_COMPOSE} -f ${COMPOSE_FILE} up -d
    
    print_info "等待服务启动..."
    sleep 10
    
    print_info "服务状态："
    ${DOCKER_COMPOSE} -f ${COMPOSE_FILE} ps
    
    print_info "${PROJECT_NAME} 启动完成！"
    print_info "访问地址: http://localhost"
    print_info "Flask 应用: http://localhost:5000"
}

# 停止服务
stop_services() {
    print_info "停止 ${PROJECT_NAME} 服务..."
    ${DOCKER_COMPOSE} -f ${COMPOSE_FILE} down
    print_info "${PROJECT_NAME} 已停止"
}

# 重启服务
restart_services() {
    print_info "重启 ${PROJECT_NAME} 服务..."
    stop_services
    start_services
}

# 查看日志
view_logs() {
    print_info "查看服务日志（按 Ctrl+C 退出）..."
    ${DOCKER_COMPOSE} -f ${COMPOSE_FILE} logs -f --tail=100
}

# 查看服务状态
check_status() {
    print_info "${PROJECT_NAME} 服务状态："
    ${DOCKER_COMPOSE} -f ${COMPOSE_FILE} ps
}

# 构建镜像
build_images() {
    print_info "构建 Docker 镜像..."
    ${DOCKER_COMPOSE} -f ${COMPOSE_FILE} build --no-cache
    print_info "镜像构建完成"
}

# 清理数据
clean_data() {
    print_warn "警告：此操作将删除所有容器、镜像和数据卷！"
    read -p "确定要继续吗？(yes/no): " confirm
    
    if [ "$confirm" == "yes" ]; then
        print_info "清理中..."
        ${DOCKER_COMPOSE} -f ${COMPOSE_FILE} down -v --rmi all
        print_info "清理完成"
    else
        print_info "取消清理"
    fi
}

# 备份数据库
backup_database() {
    print_info "备份数据库..."
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    ${DOCKER_COMPOSE} exec mysql mysqldump -u root -p file_converter > ${BACKUP_FILE}
    print_info "数据库已备份到: ${BACKUP_FILE}"
}

# 主菜单
case "${1}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    logs)
        view_logs
        ;;
    status)
        check_status
        ;;
    build)
        build_images
        ;;
    clean)
        clean_data
        ;;
    backup)
        backup_database
        ;;
    *)
        echo "使用方法: $0 {start|stop|restart|logs|status|build|clean|backup}"
        echo ""
        echo "命令说明："
        echo "  start   - 启动所有服务"
        echo "  stop    - 停止所有服务"
        echo "  restart - 重启所有服务"
        echo "  logs    - 查看服务日志"
        echo "  status  - 查看服务状态"
        echo "  build   - 重新构建镜像"
        echo "  clean   - 清理所有数据（谨慎使用）"
        echo "  backup  - 备份数据库"
        exit 1
        ;;
esac

exit 0
