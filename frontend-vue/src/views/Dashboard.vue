<!--
  仪表板页面
  
  显示系统概况和快捷操作
-->

<template>
  <div class="dashboard-container">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-content">
        <h1>文件转换系统</h1>
        <div class="user-info">
          <span>欢迎，{{ authStore.username }}</span>
          <el-button type="danger" size="small" @click="handleLogout">
            退出登录
          </el-button>
        </div>
      </div>
    </el-header>

    <!-- 主要内容区域 -->
    <el-main class="main-content">
      <el-row :gutter="20">
        <!-- 文件转换卡片 -->
        <el-col :span="8">
          <el-card shadow="hover" class="feature-card" @click="goToConverter">
            <el-icon :size="60" color="#409eff">
              <DocumentCopy />
            </el-icon>
            <h3>文件转换</h3>
            <p>支持多种格式的文件转换</p>
          </el-card>
        </el-col>

        <!-- 日志管理卡片 -->
        <el-col :span="8">
          <el-card shadow="hover" class="feature-card" @click="goToLogs">
            <el-icon :size="60" color="#67c23a">
              <Document />
            </el-icon>
            <h3>日志管理</h3>
            <p>查看和管理系统日志</p>
          </el-card>
        </el-col>

        <!-- 使用统计卡片 -->
        <el-col :span="8">
          <el-card shadow="hover" class="feature-card">
            <el-icon :size="60" color="#e6a23c">
              <TrendCharts />
            </el-icon>
            <h3>使用统计</h3>
            <p>查看文件转换统计信息</p>
          </el-card>
        </el-col>
      </el-row>

      <!-- 系统信息 -->
      <el-row :gutter="20" class="mt-20">
        <el-col :span="24">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>系统信息</span>
              </div>
            </template>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="用户名">
                {{ authStore.username }}
              </el-descriptions-item>
              <el-descriptions-item label="用户ID">
                {{ authStore.userId }}
              </el-descriptions-item>
              <el-descriptions-item label="登录时间">
                {{ new Date().toLocaleString() }}
              </el-descriptions-item>
              <el-descriptions-item label="系统版本">
                v1.0.0
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/store/auth'
import { DocumentCopy, Document, TrendCharts } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

// 跳转到文件转换页面
const goToConverter = () => {
  router.push('/converter')
}

// 跳转到日志管理页面
const goToLogs = () => {
  router.push('/logs')
}

// 退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch (error) {
    // 用户取消
  }
}
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background-color: #f0f2f5;
}

.header {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 0;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h1 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}

.feature-card {
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-card h3 {
  margin: 15px 0 10px 0;
  font-size: 20px;
  color: #303133;
}

.feature-card p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.mt-20 {
  margin-top: 20px;
}

.card-header {
  font-weight: 600;
  font-size: 16px;
}
</style>
