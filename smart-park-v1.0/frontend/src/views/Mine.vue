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

    <!-- 个人信息 -->
    <el-card class="mt16">
      <template #header>个人信息</template>
      <el-form label-width="70px" label-position="left">
        <el-form-item label="手机号">
          <span v-if="!editingPhone">{{ profile.phone || '未绑定' }}</span>
          <el-input v-else v-model="editPhone" placeholder="请输入手机号" size="small" style="width:180px" />
        </el-form-item>
        <el-form-item label="车牌号">
          <template v-if="!editingPlate">
            <el-tag v-for="(p, i) in plateList" :key="i" type="success" effect="plain" class="plate-tag" size="small">{{ p }}</el-tag>
            <span v-if="plateList.length === 0" class="dim">未绑定车牌</span>
          </template>
          <el-input v-else v-model="editPlate" placeholder="车牌号，多个用逗号分隔" size="small" style="width:220px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="small" @click="saveProfile" :loading="saving">保存</el-button>
          <el-button size="small" @click="toggleEdit">{{ editing ? '取消' : '编辑' }}</el-button>
        </el-form-item>
      </el-form>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../utils/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const auth = useAuthStore()
const showPwd = ref(false)
const oldPwd = ref('')
const newPwd = ref('')
const profile = ref({ phone: '', plate_numbers: '' })
const editing = ref(false)
const editingPhone = ref(false)
const editingPlate = ref(false)
const editPhone = ref('')
const editPlate = ref('')
const saving = ref(false)

const plateList = computed(() => {
  if (!profile.value.plate_numbers) return []
  return profile.value.plate_numbers.split(',').map(p => p.trim()).filter(Boolean)
})

async function fetchProfile() {
  try {
    const res = await api.get('/auth/me')
    if (res.code === 0 && res.data) {
      profile.value = res.data
      editPhone.value = res.data.phone || ''
      editPlate.value = res.data.plate_numbers || ''
    } else if (res.code === 401) {
      ElMessage.error('登录已过期，请重新登录')
      auth.logout()
      router.push('/login')
    }
  } catch {
    ElMessage.error('网络请求失败')
  }
}

function toggleEdit() {
  editing.value = !editing.value
  editingPhone.value = editing.value
  editingPlate.value = editing.value
  if (editing.value) {
    editPhone.value = profile.value.phone || ''
    editPlate.value = profile.value.plate_numbers || ''
  }
}

async function saveProfile() {
  saving.value = true
  try {
    const res = await api.put('/auth/profile', { phone: editPhone.value || null, plate_numbers: editPlate.value || null })
    if (res.code === 0) {
      ElMessage.success('保存成功')
      editing.value = false
      editingPhone.value = false
      editingPlate.value = false
      await fetchProfile()
    } else if (res.code === 401) {
      ElMessage.error('登录已过期，请重新登录')
      auth.logout()
      router.push('/login')
    } else {
      ElMessage.error(res.msg || '保存失败')
    }
  } catch (e) {
    ElMessage.error('网络请求失败，请确认已登录')
  }
  saving.value = false
}

async function changePwd() {
  const res = await api.put('/auth/password', { old_password: oldPwd.value, new_password: newPwd.value })
  if (res.code === 0) { ElMessage.success('密码修改成功'); showPwd.value = false } else ElMessage.error(res.msg)
}

function logout() { auth.logout(); router.push('/login') }

onMounted(fetchProfile)
</script>

<style scoped>
.page { padding-bottom: 20px; }
h3 { margin-bottom: 16px; color: #303133; }
.user-header { display: flex; align-items: center; gap: 16px; }
.uname { font-size: 18px; font-weight: 600; }
.role { font-size: 12px; color: #909399; }
.mt16 { margin-top: 16px; }
.mb16 { margin-bottom: 16px; }
.plate-tag { margin-right: 6px; margin-top: 4px; }
.dim { color: #c0c4cc; font-size: 13px; }
</style>
