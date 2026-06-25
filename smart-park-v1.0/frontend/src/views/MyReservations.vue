<template>
  <div class="page">
    <h3>我的预约 (M5)</h3>
    <div v-loading="loading">
      <el-card v-for="r in reservations" :key="r.id" class="card">
        <div class="card-header">
          <span class="lot-name">{{ r.lot_name }}</span>
          <el-tag :type="statusType(r.status)" size="small">{{ statusText(r.status) }}</el-tag>
        </div>
        <p class="addr">{{ r.lot_address }}</p>
        <p class="info">车牌：{{ r.plate_number }} | 预约时间：{{ formatTime(r.created_at) }}</p>
        <p class="info">过期时间：{{ formatTime(r.expires_at) }}</p>
        <div class="actions">
          <el-button v-if="r.status === 'created'" type="success" size="small" @click="confirm(r.id)">到场确认</el-button>
          <el-button v-if="r.status === 'created' || r.status === 'confirmed'" type="danger" size="small" @click="cancel(r.id)">取消预约</el-button>
        </div>
      </el-card>
      <el-empty v-if="!loading && reservations.length === 0" description="暂无预约记录" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../utils/api'
import { ElMessage } from 'element-plus'

const reservations = ref([])
const loading = ref(false)

function statusType(s) {
  return { created: 'warning', confirmed: 'success', cancelled: 'info', expired: 'danger' }[s] || 'info'
}
function statusText(s) {
  return { created: '待确认', confirmed: '已确认', cancelled: '已取消', expired: '已过期' }[s] || s
}
function formatTime(t) { return t ? new Date(t).toLocaleString('zh-CN') : '-' }

async function fetch() {
  loading.value = true
  const res = await api.get('/reservations/my')
  reservations.value = res.data || []
  loading.value = false
}

async function confirm(id) {
  const res = await api.put(`/reservations/${id}/confirm`)
  if (res.code === 0) { ElMessage.success('确认成功'); fetch() } else ElMessage.error(res.msg)
}

async function cancel(id) {
  const res = await api.put(`/reservations/${id}/cancel`)
  if (res.code === 0) { ElMessage.success('已取消'); fetch() } else ElMessage.error(res.msg)
}

onMounted(fetch)
</script>

<style scoped>
.page { padding-bottom: 20px; }
h3 { margin-bottom: 16px; color: #303133; }
.card { margin-bottom: 12px; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.lot-name { font-weight: 600; font-size: 15px; }
.addr { font-size: 12px; color: #909399; margin-bottom: 4px; }
.info { font-size: 12px; color: #606266; margin-bottom: 8px; }
.actions { display: flex; gap: 8px; }
</style>
