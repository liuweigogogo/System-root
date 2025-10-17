<!--
  日志管理页面
-->

<template>
  <div class="logs-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>日志管理</h2>
          <div>
            <el-button type="primary" @click="loadLogs">刷新</el-button>
            <el-button type="primary" @click="goBack">返回首页</el-button>
          </div>
        </div>
      </template>

      <el-table :data="logs" border stripe>
        <el-table-column prop="timestamp" label="时间" width="180" />
        <el-table-column prop="level" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getLogLevelType(row.level)">
              {{ row.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="消息" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const logs = ref<Array<{
  timestamp: string
  level: string
  message: string
}>>([])

const loadLogs = () => {
  // 模拟日志数据
  logs.value = [
    { timestamp: new Date().toLocaleString(), level: 'INFO', message: '用户登录成功' },
    { timestamp: new Date().toLocaleString(), level: 'WARNING', message: '验证码错误' },
    { timestamp: new Date().toLocaleString(), level: 'ERROR', message: '文件转换失败' }
  ]
}

const getLogLevelType = (level: string) => {
  const typeMap: Record<string, any> = {
    'INFO': 'success',
    'WARNING': 'warning',
    'ERROR': 'danger'
  }
  return typeMap[level] || 'info'
}

const goBack = () => {
  router.push('/dashboard')
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.logs-container {
  min-height: 100vh;
  background-color: #f0f2f5;
  padding: 30px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
}
</style>
