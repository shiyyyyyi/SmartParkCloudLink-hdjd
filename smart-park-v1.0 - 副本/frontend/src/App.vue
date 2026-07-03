<template>
  <div id="app-root">
    <!-- 管理员页面：完全独立的布局，AdminLayout 自带侧边栏 -->
    <template v-if="isAdminRoute">
      <router-view />
    </template>
    <!-- 普通用户页面：带顶部栏和底部导航 -->
    <template v-else>
      <el-container>
        <el-header v-if="auth.user" class="app-header">
          <div class="header-left">
            <el-icon :size="28" color="#409EFF"><MapLocation /></el-icon>
            <span class="app-title">智慧停车 V1.0</span>
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
        <el-main>
          <router-view />
        </el-main>
        <el-footer v-if="auth.user" class="app-footer">
          <el-tabs v-model="activeTab" @tab-change="onTabChange" class="footer-tabs">
            <el-tab-pane name="home" label="">
              <template #label><el-icon :size="22"><HomeFilled /></el-icon><br/>首页</template>
            </el-tab-pane>
            <el-tab-pane name="orders" label="">
              <template #label><el-icon :size="22"><Document /></el-icon><br/>订单</template>
            </el-tab-pane>
            <el-tab-pane name="reservations" label="">
              <template #label><el-icon :size="22"><Clock /></el-icon><br/>预约</template>
            </el-tab-pane>
            <el-tab-pane name="records" label="">
              <template #label><el-icon :size="22"><List /></el-icon><br/>记录</template>
            </el-tab-pane>
            <el-tab-pane name="find-car" label="">
              <template #label><el-icon :size="22"><MapLocation /></el-icon><br/>寻车</template>
            </el-tab-pane>
            <el-tab-pane name="mine" label="">
              <template #label><el-icon :size="22"><User /></el-icon><br/>我的</template>
            </el-tab-pane>
          </el-tabs>
        </el-footer>
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

const isAdminRoute = computed(() => route.path.startsWith('/admin'))

const tabMap = { '/home': 'home', '/orders': 'orders', '/reservations': 'reservations', '/records': 'records', '/find-car': 'find-car', '/mine': 'mine' }
watch(() => route.path, (p) => {
  for (const [k, v] of Object.entries(tabMap)) { if (p.startsWith(k)) { activeTab.value = v; break } }
}, { immediate: true })

function onTabChange(tab) {
  const paths = { home: '/home', orders: '/orders', reservations: '/reservations', records: '/records', 'find-car': '/find-car', mine: '/mine' }
  router.push(paths[tab] || '/home')
}

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; }
.app-header { background: #fff; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
.header-left { display: flex; align-items: center; gap: 8px; }
.app-title { font-size: 18px; font-weight: 700; color: #303133; }
.header-right { display: flex; align-items: center; gap: 12px; }
.user-info { cursor: pointer; color: #409EFF; }
.app-footer { background: #fff; padding: 5px 0 0 0; border-top: 1px solid #ebeef5; }
.footer-tabs .el-tabs__header { margin: 0; }
.footer-tabs .el-tab-pane { text-align: center; }
#app-root { margin: 0 auto; min-height: 100vh; background: #fff; }
.el-main { padding: 16px; }
</style>
