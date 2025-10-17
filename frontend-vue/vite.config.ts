/**
 * Vite配置文件
 * 
 * 职责：
 * - 配置开发服务器
 * - 配置构建选项
 * - 配置路径别名
 * - 配置代理转发（解决跨域问题）
 */

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  // Vue插件配置
  plugins: [vue()],
  
  // 路径别名配置，简化导入路径
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),  // @指向src目录
      '@components': path.resolve(__dirname, './src/components'),  // 组件目录
      '@views': path.resolve(__dirname, './src/views'),  // 视图目录
      '@assets': path.resolve(__dirname, './src/assets'),  // 资源目录
      '@api': path.resolve(__dirname, './src/api'),  // API目录
      '@utils': path.resolve(__dirname, './src/utils'),  // 工具目录
      '@store': path.resolve(__dirname, './src/store'),  // 状态管理目录
    }
  },
  
  // 开发服务器配置
  server: {
    host: '0.0.0.0',  // 监听所有网络接口
    port: 3000,  // 前端开发服务器端口
    open: true,  // 自动打开浏览器
    
    // 配置代理，解决跨域问题
    // 所有以/api开头的请求都会被代理到Flask后端
    proxy: {
      '/api': {
        target: 'http://localhost:5000',  // Flask后端地址
        changeOrigin: true,  // 改变请求源
        // rewrite: (path) => path.replace(/^\/api/, '')  // 如果后端没有/api前缀，取消这行注释
      }
    }
  },
  
  // 构建配置
  build: {
    outDir: 'dist',  // 输出目录
    assetsDir: 'assets',  // 静态资源目录
    sourcemap: false,  // 不生成source map（生产环境）
    
    // 代码分割策略
    rollupOptions: {
      output: {
        // 分包策略：将第三方库单独打包
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],  // Vue核心库
          'element-plus': ['element-plus', '@element-plus/icons-vue'],  // UI组件库
          'axios': ['axios']  // HTTP客户端
        }
      }
    },
    
    // 生产环境移除console
    terserOptions: {
      compress: {
        drop_console: true,  // 移除console.log
        drop_debugger: true  // 移除debugger
      }
    }
  }
})
