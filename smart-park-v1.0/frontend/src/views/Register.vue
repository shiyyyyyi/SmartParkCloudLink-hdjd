<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2 class="auth-title">注册账号</h2>
      <el-input v-model="username" placeholder="用户名(2-20位)" size="large" clearable class="mb16" />
      <el-input v-model="password" type="password" placeholder="密码(6-18位)" size="large" show-password class="mb16" />
      <el-input v-model="phone" placeholder="手机号(选填)" size="large" clearable class="mb16" />
      <el-button type="primary" size="large" :loading="loading" @click="register" style="width:100%">注 册</el-button>
      <p class="auth-link" @click="$router.push('/login')">已有账号？去登录</p>
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
const phone = ref('')
const loading = ref(false)

async function register() {
  if (!username.value || username.value.length < 2) return ElMessage.warning('用户名至少2位')
  if (!password.value || password.value.length < 6) return ElMessage.warning('密码至少6位')
  loading.value = true
  const res = await api.post('/auth/register', { username: username.value, password: password.value, phone: phone.value || null })
  if (res.code === 0) {
    auth.setAuth(res.data.token, res.data.user)
    ElMessage.success('注册成功')
    router.push('/home')
  } else {
    ElMessage.error(res.msg)
  }
  loading.value = false
}
</script>

<style scoped>
.auth-page { display: flex; align-items: center; justify-content: center; min-height: 100vh; background: linear-gradient(135deg, #67C23A, #409EFF); }
.auth-card { width: 360px; background: #fff; border-radius: 16px; padding: 40px 32px; box-shadow: 0 8px 24px rgba(0,0,0,.15); }
.auth-title { text-align: center; font-size: 28px; font-weight: 700; color: #67C23A; margin-bottom: 32px; }
.mb16 { margin-bottom: 16px; }
.auth-link { text-align: center; margin-top: 16px; font-size: 13px; color: #409EFF; cursor: pointer; }
</style>
