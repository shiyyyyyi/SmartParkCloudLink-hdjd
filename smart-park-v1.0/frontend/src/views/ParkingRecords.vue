<template>
  <div class="page">
    <h3>停车记录</h3>
    <div v-loading="loading">
      <el-card v-for="r in records" :key="r.id" class="card">
        <p class="lot-name">{{ r.lot_name }}</p>
        <p class="info">车牌：{{ r.plate_number }} | 车位：{{ r.spot_number || '未分配' }}</p>
        <p class="info">入场：{{ formatTime(r.entry_time) }} | 出场：{{ formatTime(r.exit_time) }}</p>
        <p class="info">费用：¥{{ r.amount || '—' }} | {{ statusText(r.status) }}</p>
      </el-card>
      <el-empty v-if="!loading && records.length === 0" description="暂无停车记录" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../utils/api'

const records = ref([])
const loading = ref(false)

function formatTime(t) { return t ? new Date(t).toLocaleString('zh-CN') : '-' }
function statusText(s) { return { parking: '停车中', pending_pay: '待支付', paid: '已完成', exception: '异常' }[s] || s }

async function fetch() {
  loading.value = true
  const res = await api.get('/records/my')
  records.value = res.data || []
  loading.value = false
}

onMounted(fetch)
</script>

<style scoped>
.page { padding-bottom: 20px; }
h3 { margin-bottom: 16px; color: #303133; }
.card { margin-bottom: 12px; }
.lot-name { font-weight: 600; font-size: 15px; margin-bottom: 6px; }
.info { font-size: 12px; color: #606266; margin-bottom: 4px; }
</style>
