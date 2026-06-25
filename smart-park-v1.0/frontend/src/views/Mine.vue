<template>
  <div class="page">
    <h3>我的</h3>
    <el-card>
      <div class="user-header">
        <el-avatar :size="60" icon="UserFilled" />
        <div class="user-detail">
          <p class="uname">{{ auth.user?.username }}</p>
          <p class="role">{{ auth.user?.role === 'admin' ? '管理员' : '普通用户' }}</p>
        </div>
      </div>
    </el-card>

    <el-card class="mt16">
      <el-cell-group>
        <el-cell title="修改密码" is-link @click="showPwd = true" />
        <el-cell title="退出登录" is-link @click="logout" />
      </el-cell-group>
    </el-card>

    <el-dialog v-model="showPwd" title="修改密码" width="90%">
      <el-input v-model="oldPwd" type="password" placeholder="原密码" class="mb16" />
      <el-input v-model="newPwd" type="password" placeholder="新密码(6-18位)" class="mb16" />
      <template #footer>
        <el-button @click="showPwd = false">取消</el-button>
        <el-button type="primary" @click="changePwd">确认</el-button>
      </template>
    </el-dialog>
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
const showPwd = ref(false)
const oldPwd = ref('')
const newPwd = ref('')

async function changePwd() {
  const res = await api.put('/auth/password', { old_password: oldPwd.value, new_password: newPwd.value })
  if (res.code === 0) { ElMessage.success('密码修改成功'); showPwd.value = false } else ElMessage.error(res.msg)
}

function logout() { auth.logout(); router.push('/login') }
</script>

<style scoped>
.page { padding-bottom: 20px; }
h3 { margin-bottom: 16px; color: #303133; }
.user-header { display: flex; align-items: center; gap: 16px; }
.uname { font-size: 18px; font-weight: 600; }
.role { font-size: 12px; color: #909399; }
.mt16 { margin-top: 16px; }
.mb16 { margin-bottom: 16px; }
</style>
