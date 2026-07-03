<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2 class="auth-title">智慧停车</h2>
      <p class="auth-subtitle">手机号登录</p>
      <el-input v-model="username" placeholder="请输入用户名" size="large" clearable class="mb16" />
      <el-input v-model="password" type="password" placeholder="请输入密码" size="large" show-password class="mb16" @keyup.enter="login" />
      <el-button type="primary" size="large" :loading="loading" @click="login" style="width:100%">登 录</el-button>
      <p class="auth-link" @click="$router.push('/register')">没有账号？立即注册</p>
      <el-divider />
      <p class="demo-tip">演示账号：admin / admin123 或 user / user123</p>
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
</script>

<style scoped>
.auth-page { display: flex; align-items: center; justify-content: center; min-height: 100vh; background: linear-gradient(135deg, #409EFF, #67C23A); }
.auth-card { width: 360px; background: #fff; border-radius: 16px; padding: 40px 32px; box-shadow: 0 8px 24px rgba(0,0,0,.15); }
.auth-title { text-align: center; font-size: 28px; font-weight: 700; color: #409EFF; margin-bottom: 4px; }
.auth-subtitle { text-align: center; font-size: 14px; color: #909399; margin-bottom: 32px; }
.mb16 { margin-bottom: 16px; }
.auth-link { text-align: center; margin-top: 16px; font-size: 13px; color: #409EFF; cursor: pointer; }
.demo-tip { text-align: center; font-size: 12px; color: #C0C4CC; }
</style>
