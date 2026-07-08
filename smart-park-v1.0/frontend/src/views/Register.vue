<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2 class="auth-title">注册账号</h2>
      <p class="auth-subtitle">创建车主账号后可直接预约、入场和寻车</p>
      <el-input v-model="username" placeholder="用户名(2-20位)" size="large" clearable class="mb16" />
      <el-input v-model="password" type="password" placeholder="密码(6-18位)" size="large" show-password class="mb16" />
      <el-input v-model="phone" placeholder="手机号(选填)" size="large" clearable class="mb16" />
      <el-input v-model="plateNumber" placeholder="车牌号(选填，如：京A12345)" size="large" clearable class="mb16" />
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
const plateNumber = ref('')
const loading = ref(false)

async function register() {
  if (!username.value || username.value.length < 2) return ElMessage.warning('用户名至少2位')
  if (!password.value || password.value.length < 6) return ElMessage.warning('密码至少6位')
  loading.value = true
  const res = await api.post('/auth/register', {
    username: username.value,
    password: password.value,
    phone: phone.value || null,
    plate_number: plateNumber.value || null
  })
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
.auth-page { display: flex; align-items: center; justify-content: center; min-height: 100vh; padding: 24px; background: linear-gradient(135deg, #eef8f2 0%, #eaf4ff 58%, #fff 100%); }
.auth-card { width: min(420px, 100%); background: rgba(255,255,255,.96); border: 1px solid #e8eef7; border-radius: 12px; padding: 42px 34px; box-shadow: 0 18px 44px rgba(15,23,42,.12); }
.auth-title { text-align: center; font-size: 28px; font-weight: 800; color: #1f2d3d; margin-bottom: 6px; }
.auth-subtitle { text-align: center; font-size: 14px; color: #8492a6; line-height: 1.6; margin-bottom: 28px; }
.mb16 { margin-bottom: 16px; }
.auth-link { text-align: center; margin-top: 18px; font-size: 13px; color: #2563eb; cursor: pointer; font-weight: 600; }
</style>
