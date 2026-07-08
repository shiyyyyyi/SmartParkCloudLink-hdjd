<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <el-aside :width="collapsed ? '64px' : '200px'" class="admin-sidebar">
      <div class="sidebar-header">
        <el-icon :size="24" color="#fff" v-if="collapsed"><Setting /></el-icon>
        <span v-else class="sidebar-title">SmartPark 管理台</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="collapsed"
        :collapse-transition="false"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
      >
        <el-menu-item index="/admin">
          <el-icon><DataAnalysis /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/admin/lots">
          <el-icon><Location /></el-icon>
          <span>停车场管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/orders">
          <el-icon><Tickets /></el-icon>
          <span>订单管理</span>
        </el-menu-item>
      </el-menu>
      <div class="sidebar-footer">
        <el-button text bg @click="toggleCollapse" class="collapse-btn">
          <el-icon :size="18" color="#bfcbd9"><Fold v-if="!collapsed" /><Expand v-else /></el-icon>
        </el-button>
      </div>
    </el-aside>

    <!-- 主内容区 -->
    <el-container class="admin-main">
      <el-header class="admin-header">
        <div class="header-breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/admin' }">管理后台</el-breadcrumb-item>
            <el-breadcrumb-item>{{ pageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-actions">
          <el-tag type="warning" size="small">管理员: {{ adminName }}</el-tag>
          <el-button size="small" @click="goHome">返回首页</el-button>
          <el-button size="small" type="danger" @click="logout">退出</el-button>
        </div>
      </el-header>
      <el-main class="admin-content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { Setting, DataAnalysis, Location, Tickets, Fold, Expand } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const collapsed = ref(false)

const activeMenu = computed(() => route.path)
const adminName = computed(() => {
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    return user.username || '管理员'
  } catch { return '管理员' }
})

const pageTitles = {
  '/admin': '仪表盘',
  '/admin/lots': '停车场管理',
  '/admin/orders': '订单管理'
}
const pageTitle = computed(() => {
  // 车场详情页
  if (route.path.startsWith('/admin/lots/')) return '车场详情'
  return pageTitles[route.path] || '管理后台'
})

function toggleCollapse() {
  collapsed.value = !collapsed.value
}

function goHome() {
  router.push('/home')
}

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.admin-layout { display: flex; min-height: 100vh; background: #eef4fb; }

.admin-sidebar {
  background: linear-gradient(180deg, #1f2d3d 0%, #27384d 100%);
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 8px 0 24px rgba(15,23,42,.14);
}

.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.sidebar-title {
  color: #fff;
  font-size: 16px;
  font-weight: 800;
  white-space: nowrap;
}

.el-menu {
  border-right: none;
  flex: 1;
}

.el-menu-item {
  height: 48px;
  line-height: 48px;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid rgba(255,255,255,0.1);
  display: flex;
  justify-content: center;
}

.collapse-btn {
  width: 100%;
  color: #bfcbd9;
}

.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.admin-header {
  background: rgba(255,255,255,.96);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 64px;
  border-bottom: 1px solid rgba(64,158,255,.12);
  box-shadow: 0 8px 24px rgba(30,64,175,.08);
  flex-shrink: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.admin-content {
  padding: 22px;
  flex: 1;
  overflow-y: auto;
}
</style>
