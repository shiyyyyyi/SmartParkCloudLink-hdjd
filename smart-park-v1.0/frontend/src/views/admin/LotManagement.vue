<template>
  <div class="admin-page">
    <el-page-header @back="$router.push('/admin')" title="车场管理" />
    <div v-loading="loading" class="mt16">
      <el-card v-for="l in lots" :key="l.id" class="card" @click="$router.push(`/admin/lots/${l.id}`)">
        <div class="card-header">
          <span class="lot-name">{{ l.name }}</span>
          <el-tag :type="l.status === 'active' ? 'success' : 'danger'" size="small">{{ l.status === 'active' ? '运营中' : '停用' }}</el-tag>
        </div>
        <p class="addr">{{ l.address }}</p>
        <p class="info">车位：{{ l.available_spots }}/{{ l.total_spots }} | ¥{{ l.price_per_hour }}/h</p>
        <p class="info">最后同步：{{ formatTime(l.last_sync_at) }}</p>
        <el-button type="primary" size="small" @click.stop="syncLot(l.id)">同步数据 (M2)</el-button>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../utils/api'
import { ElMessage } from 'element-plus'

const lots = ref([])
const loading = ref(false)
function formatTime(t) { return t ? new Date(t).toLocaleString('zh-CN') : '从未同步' }

async function fetch() {
  loading.value = true
  const res = await api.get('/admin/lots', { params: { page: 1, page_size: 50 } })
  lots.value = res.data || []
  loading.value = false
}

async function syncLot(id) {
  const res = await api.post(`/lots/${id}/sync`)
  if (res.code === 0) { ElMessage.success(res.msg); fetch() } else ElMessage.error(res.msg)
}

onMounted(fetch)
</script>

<style scoped>
.admin-page { padding-bottom: 20px; }
.mt16 { margin-top: 16px; }
.card { margin-bottom: 12px; cursor: pointer; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.lot-name { font-weight: 600; font-size: 15px; }
.addr { font-size: 12px; color: #909399; margin-bottom: 4px; }
.info { font-size: 12px; color: #606266; margin-bottom: 8px; }
</style>
