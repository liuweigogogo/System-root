<!--
  用户登录页面
  
  职责：
  - 提供用户登录界面
  - 处理用户登录逻辑
  - 验证码显示和刷新
  - 表单验证
-->

<template>
  <div class="login-container">
    <!-- 登录卡片 -->
    <el-card class="login-card" shadow="always">
      <!-- 标题 -->
      <template #header>
        <div class="card-header">
          <h2>文件转换系统</h2>
          <p>用户登录</p>
        </div>
      </template>

      <!-- 登录表单 -->
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-width="80px"
        size="large"
      >
        <!-- 用户名输入框 -->
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <!-- 密码输入框 -->
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <!-- 验证码输入框 -->
        <el-form-item label="验证码" prop="captcha">
          <div class="captcha-wrapper">
            <el-input
              v-model="loginForm.captcha"
              placeholder="请输入验证码"
              prefix-icon="Picture"
              clearable
              @keyup.enter="handleLogin"
            />
            <!-- 验证码显示 -->
            <div class="captcha-display" @click="refreshCaptcha">
              <span v-if="captchaText">{{ captchaText }}</span>
              <el-button v-else :loading="captchaLoading" type="primary">
                获取验证码
              </el-button>
            </div>
          </div>
        </el-form-item>

        <!-- 登录按钮 -->
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            @click="handleLogin"
            class="login-button"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>

        <!-- 注册链接 -->
        <el-form-item>
          <div class="footer-links">
            <span>还没有账号？</span>
            <el-link type="primary" @click="goToRegister">
              立即注册
            </el-link>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
/**
 * 使用Vue 3 Composition API
 * 
 * 这个组件展示了：
 * 1. 响应式状态管理（ref, reactive）
 * 2. 表单验证
 * 3. API调用
 * 4. 路由导航
 * 5. Element Plus组件使用
 */

import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/store/auth'
import { authAPI } from '@/api/auth'

// ==================== 路由和状态管理 ====================

const router = useRouter()  // 路由实例，用于页面跳转
const route = useRoute()    // 当前路由信息
const authStore = useAuthStore()  // 认证状态管理

// ==================== 表单状态 ====================

/**
 * 登录表单引用
 * 用于调用表单的验证方法
 */
const loginFormRef = ref<FormInstance>()

/**
 * 登录表单数据
 * 使用reactive创建响应式对象
 */
const loginForm = reactive({
  username: '',   // 用户名
  password: '',   // 密码
  captcha: ''     // 验证码
})

/**
 * 表单验证规则
 * 定义每个字段的验证规则
 */
const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 128, message: '密码长度至少 6 个字符', trigger: 'blur' }
  ],
  captcha: [
    { required: true, message: '请输入验证码', trigger: 'blur' }
  ]
}

// ==================== 验证码相关 ====================

/**
 * 验证码文本
 * 从服务器获取的验证码字符串
 */
const captchaText = ref<string>('')

/**
 * 验证码加载状态
 */
const captchaLoading = ref<boolean>(false)

/**
 * 刷新验证码
 * 
 * 从服务器获取新的验证码
 */
const refreshCaptcha = async () => {
  captchaLoading.value = true
  
  try {
    // 调用获取验证码API
    const response = await authAPI.getCaptcha()
    
    if (response.success) {
      captchaText.value = response.captcha
    } else {
      ElMessage.error(response.message || '获取验证码失败')
    }
  } catch (error) {
    console.error('获取验证码失败:', error)
    ElMessage.error('获取验证码失败，请重试')
  } finally {
    captchaLoading.value = false
  }
}

// ==================== 登录逻辑 ====================

/**
 * 登录加载状态
 */
const loading = ref<boolean>(false)

/**
 * 处理登录
 * 
 * 流程：
 * 1. 验证表单
 * 2. 调用登录API
 * 3. 登录成功后跳转到目标页面
 */
const handleLogin = async () => {
  // 验证表单
  if (!loginFormRef.value) return
  
  const valid = await loginFormRef.value.validate().catch(() => false)
  
  if (!valid) {
    return
  }
  
  loading.value = true
  
  try {
    // 调用store的登录方法
    const success = await authStore.login({
      username: loginForm.username,
      password: loginForm.password,
      captcha: loginForm.captcha
    })
    
    if (success) {
      ElMessage.success('登录成功！')
      
      // 跳转到目标页面（如果有redirect参数则跳转到该页面，否则跳转到仪表板）
      const redirect = route.query.redirect as string
      router.push(redirect || '/dashboard')
    } else {
      ElMessage.error('登录失败，请检查用户名和密码')
      // 刷新验证码
      refreshCaptcha()
      // 清空密码和验证码
      loginForm.password = ''
      loginForm.captcha = ''
    }
  } catch (error: any) {
    console.error('登录错误:', error)
    ElMessage.error(error.message || '登录失败，请重试')
    // 刷新验证码
    refreshCaptcha()
    // 清空密码和验证码
    loginForm.password = ''
    loginForm.captcha = ''
  } finally {
    loading.value = false
  }
}

/**
 * 跳转到注册页面
 */
const goToRegister = () => {
  router.push('/register')
}

// ==================== 生命周期 ====================

/**
 * 组件挂载时执行
 * 
 * 自动获取验证码
 */
onMounted(() => {
  refreshCaptcha()
})
</script>

<style scoped>
/**
 * 组件样式
 * 
 * scoped：样式仅作用于当前组件
 */

/* 登录容器 - 居中布局 */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 登录卡片 */
.login-card {
  width: 450px;
  border-radius: 12px;
}

/* 卡片头部 */
.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
}

.card-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

/* 验证码包装器 */
.captcha-wrapper {
  display: flex;
  gap: 10px;
  width: 100%;
}

.captcha-wrapper .el-input {
  flex: 1;
}

/* 验证码显示区域 */
.captcha-display {
  width: 120px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  user-select: none;
  font-size: 18px;
  font-weight: bold;
  letter-spacing: 5px;
  color: #409eff;
  transition: all 0.3s;
}

.captcha-display:hover {
  background-color: #ecf5ff;
  border-color: #409eff;
}

/* 登录按钮 */
.login-button {
  width: 100%;
  margin-top: 10px;
}

/* 底部链接 */
.footer-links {
  width: 100%;
  text-align: center;
  font-size: 14px;
  color: #606266;
}

.footer-links span {
  margin-right: 5px;
}
</style>
