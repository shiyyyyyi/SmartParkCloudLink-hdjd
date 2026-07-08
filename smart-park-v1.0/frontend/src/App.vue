<template>
  <div id="app-root">
    <!-- 管理员页面：完全独立的布局，AdminLayout 自带侧边栏 -->
    <template v-if="isAdminRoute">
      <router-view />
    </template>
    <!-- 普通用户页面：带顶部栏和顶部功能导航 -->
    <template v-else>
      <el-container>
        <el-header v-if="auth.user" class="app-header">
          <div class="header-left">
            <div class="brand-mark">
              <el-icon :size="22"><MapLocation /></el-icon>
            </div>
            <div>
              <span class="app-title">智慧停车 V3.0</span>
              <span class="app-subtitle">SmartPark CloudLink</span>
            </div>
          </div>
          <div class="header-right">
            <template v-if="auth.user.role === 'admin'">
              <el-button @click="$router.push('/admin')" type="warning" size="small">管理后台</el-button>
            </template>
            <el-dropdown>
              <span class="user-info">{{ auth.user.username }}</span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        <div v-if="auth.user" class="app-nav">
          <button
            v-for="item in navItems"
            :key="item.name"
            class="nav-item"
            :class="{ active: activeTab === item.name }"
            @click="goTab(item.name)"
          >
            <el-icon :size="18"><component :is="item.icon" /></el-icon>
            <span>{{ item.label }}</span>
          </button>
        </div>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </template>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { MapLocation, HomeFilled, Document, Clock, List, User } from '@element-plus/icons-vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const activeTab = ref('home')
const paths = { home: '/home', orders: '/orders', reservations: '/reservations', records: '/records', 'find-car': '/find-car', mine: '/mine' }
const navItems = [
  { name: 'home', label: '首页', icon: HomeFilled },
  { name: 'orders', label: '订单', icon: Document },
  { name: 'reservations', label: '预约', icon: Clock },
  { name: 'records', label: '记录', icon: List },
  { name: 'find-car', label: '寻车', icon: MapLocation },
  { name: 'mine', label: '我的', icon: User },
]

const isAdminRoute = computed(() => route.path.startsWith('/admin'))

const tabMap = { '/home': 'home', '/orders': 'orders', '/reservations': 'reservations', '/records': 'records', '/find-car': 'find-car', '/mine': 'mine' }
watch(() => route.path, (p) => {
  for (const [k, v] of Object.entries(tabMap)) { if (p.startsWith(k)) { activeTab.value = v; break } }
}, { immediate: true })

function goTab(tab) {
  router.push(paths[tab] || '/home')
}

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #eef4fb; color: #303133; }
.app-header { position: sticky; top: 0; z-index: 50; height: 64px; background: rgba(255,255,255,.96); backdrop-filter: blur(12px); display: flex; align-items: center; justify-content: space-between; padding: 0 24px; border-bottom: 1px solid rgba(64,158,255,.12); box-shadow: 0 8px 24px rgba(30,64,175,.08); }
.header-left { display: flex; align-items: center; gap: 10px; }
.brand-mark { width: 38px; height: 38px; border-radius: 8px; background: linear-gradient(135deg, #1677ff, #22c55e); color: #fff; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 18px rgba(64,158,255,.28); }
.app-title { display: block; font-size: 18px; font-weight: 800; color: #1f2d3d; line-height: 1.1; }
.app-subtitle { display: block; margin-top: 3px; font-size: 11px; color: #8a97a8; letter-spacing: .2px; }
.header-right { display: flex; align-items: center; gap: 12px; }
.user-info { cursor: pointer; color: #2563eb; font-weight: 600; }
.app-nav { position: sticky; top: 64px; z-index: 45; background: rgba(246,250,255,.94); backdrop-filter: blur(10px); display: flex; gap: 10px; padding: 10px 18px; border-bottom: 1px solid rgba(64,158,255,.12); overflow-x: auto; }
.app-nav::-webkit-scrollbar { display: none; }
.nav-item { min-width: 84px; border: 1px solid transparent; border-radius: 8px; background: #fff; color: #64748b; padding: 10px 14px; display: inline-flex; align-items: center; justify-content: center; gap: 6px; cursor: pointer; font-size: 14px; white-space: nowrap; box-shadow: 0 4px 14px rgba(15,23,42,.05); transition: all .18s ease; }
.nav-item.active { background: #1677ff; border-color: #1677ff; color: #fff; font-weight: 700; box-shadow: 0 8px 20px rgba(22,119,255,.22); }
.nav-item:hover { transform: translateY(-1px); color: #1677ff; border-color: #bfdbfe; }
.nav-item.active:hover { color: #fff; }
#app-root { margin: 0 auto; min-height: 100vh; background: linear-gradient(180deg, #eef4fb 0%, #f8fbff 46%, #fff 100%); }
.el-main { padding: 18px; }
.el-card { border-radius: 8px; border: 1px solid #e8eef7; box-shadow: 0 8px 24px rgba(15,23,42,.06); }
.el-button { border-radius: 8px; }
.el-input__wrapper, .el-select__wrapper { border-radius: 8px; }
@media (max-width: 640px) {
  .app-header { height: 60px; padding: 0 12px; }
  .app-title { font-size: 16px; }
  .app-subtitle { display: none; }
  .app-nav { top: 60px; padding: 8px 12px; }
  .nav-item { min-width: 70px; padding: 8px 10px; font-size: 13px; }
  .el-main { padding: 12px; }
}
</style>
