<template>
  <div class="auth-page">
    <div class="auth-shell">
      <div class="auth-brand">
        <span class="brand-kicker">SmartPark CloudLink</span>
        <h1>智慧停车 V3.0</h1>
        <p>车场搜索、车位预约、无感支付、反向寻车和运营管理的一体化演示系统。</p>
        <div class="brand-metrics">
          <div><strong>5</strong><span>示例车场</span></div>
          <div><strong>15min</strong><span>预约锁位</span></div>
          <div><strong>V3</strong><span>最终版</span></div>
        </div>
      </div>
      <div class="auth-card">
        <h2 class="auth-title">欢迎登录</h2>
        <p class="auth-subtitle">选择演示账号或输入用户名密码</p>
        <el-input v-model="username" placeholder="请输入用户名" size="large" clearable class="mb16" />
        <el-input v-model="password" type="password" placeholder="请输入密码" size="large" show-password class="mb16" @keyup.enter="login" />
        <el-button type="primary" size="large" :loading="loading" @click="login" style="width:100%">登 录</el-button>
        <div class="demo-actions">
          <el-button size="small" @click="fillDemo('user')">普通用户演示</el-button>
          <el-button size="small" type="warning" @click="fillDemo('admin')">管理员演示</el-button>
        </div>
        <p class="auth-link" @click="$router.push('/register')">没有账号？立即注册</p>
        <el-divider />
        <p class="demo-tip">演示账号：admin / admin123 或 user / user123</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../utils/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const auth = useAuthStore()
const username = ref('')
const password = ref('')
const loading = ref(false)

async function login() {
  if (!username.value || !password.value) return ElMessage.warning('请输入用户名和密码')
  loading.value = true
  try {
    const res = await api.post('/auth/login', { username: username.value, password: password.value })
    if (res.code === 0) {
      auth.setAuth(res.data.token, res.data.user)
      ElMessage.success('登录成功')
      router.push('/home')
    } else {
      ElMessage.error(res.msg)
    }
  } catch { }
  loading.value = false
}

function fillDemo(role) {
  if (role === 'admin') {
    username.value = 'admin'
    password.value = 'admin123'
  } else {
    username.value = 'user'
    password.value = 'user123'
  }
}
</script>

<style scoped>
.auth-page { display: flex; align-items: center; justify-content: center; min-height: 100vh; padding: 32px; background: linear-gradient(135deg, #eaf4ff 0%, #f2fbf6 54%, #ffffff 100%); }
.auth-shell { width: min(960px, 100%); display: grid; grid-template-columns: 1.15fr .85fr; gap: 24px; align-items: stretch; }
.auth-brand { border-radius: 12px; padding: 46px; color: #fff; background: linear-gradient(135deg, #1677ff, #16a34a); box-shadow: 0 20px 46px rgba(22,119,255,.24); display: flex; flex-direction: column; justify-content: center; }
.brand-kicker { font-size: 13px; letter-spacing: .5px; opacity: .88; margin-bottom: 16px; }
.auth-brand h1 { font-size: 38px; line-height: 1.15; margin-bottom: 16px; }
.auth-brand p { font-size: 15px; line-height: 1.8; opacity: .92; max-width: 520px; }
.brand-metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 34px; }
.brand-metrics div { border-radius: 8px; padding: 14px; background: rgba(255,255,255,.16); }
.brand-metrics strong { display: block; font-size: 22px; }
.brand-metrics span { font-size: 12px; opacity: .86; }
.auth-card { background: rgba(255,255,255,.96); border: 1px solid #e8eef7; border-radius: 12px; padding: 42px 34px; box-shadow: 0 18px 44px rgba(15,23,42,.12); }
.auth-title { text-align: center; font-size: 28px; font-weight: 800; color: #1f2d3d; margin-bottom: 6px; }
.auth-subtitle { text-align: center; font-size: 14px; color: #8492a6; margin-bottom: 30px; }
.mb16 { margin-bottom: 16px; }
.demo-actions { display: flex; gap: 8px; margin-top: 12px; }
.demo-actions .el-button { flex: 1; }
.auth-link { text-align: center; margin-top: 18px; font-size: 13px; color: #2563eb; cursor: pointer; font-weight: 600; }
.demo-tip { text-align: center; font-size: 12px; color: #C0C4CC; }
@media (max-width: 820px) {
  .auth-page { padding: 18px; }
  .auth-shell { grid-template-columns: 1fr; }
  .auth-brand { padding: 30px; }
  .auth-brand h1 { font-size: 30px; }
}
</style>
