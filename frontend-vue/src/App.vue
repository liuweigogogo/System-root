<!--
  应用根组件
  
  职责：
  - 定义应用的整体布局结构
  - 提供路由视图容器
-->

<template>
  <div id="app">
    <!-- 路由视图：显示当前路由对应的组件 -->
    <router-view />
  </div>
</template>

<script setup lang="ts">
/**
 * 使用Vue 3的Composition API和setup语法糖
 * 
 * 这个组件作为应用的根组件，不需要额外的逻辑
 * 只提供一个路由视图容器，让路由系统渲染对应的页面组件
 */
</script>

<style>
/**
 * 全局样式
 * 
 * 这里定义的样式会应用到整个应用
 */

/* 重置默认样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* 设置全局字体 */
body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 
               'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 应用容器占满整个视口 */
#app {
  width: 100%;
  min-height: 100vh;
}
</style>
