<!--
  404页面
-->

<template>
  <div class="not-found">
    <div class="content">
      <h1>404</h1>
      <h2>页面不存在</h2>
      <p>您访问的页面不存在或已被删除</p>
      <el-button type="primary" @click="goHome">返回首页</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/dashboard')
}
</script>

<style scoped>
.not-found {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;
}

.content {
  text-align: center;
}

.content h1 {
  font-size: 120px;
  margin: 0;
  color: #409eff;
}

.content h2 {
  font-size: 32px;
  margin: 20px 0;
}

.content p {
  color: #909399;
  margin: 20px 0 30px 0;
}
</style>
