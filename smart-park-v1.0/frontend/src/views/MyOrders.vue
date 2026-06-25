<template>
  <div class="page">
    <h3>我的订单 (M6)</h3>
    <el-tabs v-model="tab" @tab-change="fetch">
      <el-tab-pane label="全部" name="all" />
      <el-tab-pane label="停车中" name="parking" />
      <el-tab-pane label="待支付" name="pending_pay" />
      <el-tab-pane label="已完成" name="paid" />
    </el-tabs>
    <div v-loading="loading">
      <el-card v-for="o in orders" :key="o.id" class="card">
        <div class="card-header">
          <span class="lot-name">{{ o.lot_name }}</span>
          <el-tag :type="statusType(o.status)" size="small">{{ statusText(o.status) }}</el-tag>
        </div>
        <p class="info">车牌：{{ o.plate_number }}</p>
        <p class="info">入场：{{ formatTime(o.entry_time) }} | {{ o.duration_hours ? o.duration_hours + '小时' : '—' }}</p>
        <p class="info">金额：¥{{ o.amount || '—' }}</p>
        <el-button v-if="o.status === 'pending_pay'" type="primary" size="small" @click="pay(o.id)">支付 ¥{{ o.amount }}</el-button>
        <el-tag v-if="o.status === 'paid'" type="success" size="small">已支付 {{ o.paid_at ? formatTime(o.paid_at) : '' }}</el-tag>
      </el-card>
      <el-empty v-if="!loading && orders.length === 0" description="暂无订单" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../utils/api'
import { ElMessage } from 'element-plus'

const orders = ref([])
const loading = ref(false)
const tab = ref('all')

function statusType(s) {
  return { parking: '', pending_pay: 'warning', paid: 'success', exception: 'danger' }[s] || 'info'
}
function statusText(s) {
  return { parking: '停车中', pending_pay: '待支付', paid: '已完成', exception: '异常' }[s] || s
}
function formatTime(t) { return t ? new Date(t).toLocaleString('zh-CN') : '-' }

async function fetch() {
  loading.value = true
  const params = {}
  if (tab.value !== 'all') params.status = tab.value
  const res = await api.get('/orders/my', { params })
  orders.value = res.data || []
  loading.value = false
}

async function pay(id) {
  const res = await api.post(`/orders/${id}/pay`)
  if (res.code === 0) { ElMessage.success(res.msg); fetch() } else ElMessage.error(res.msg)
}

onMounted(fetch)
</script>

<style scoped>
.page { padding-bottom: 20px; }
h3 { margin-bottom: 16px; color: #303133; }
.card { margin-bottom: 12px; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.lot-name { font-weight: 600; font-size: 15px; }
.info { font-size: 12px; color: #606266; margin-bottom: 4px; }
</style>
