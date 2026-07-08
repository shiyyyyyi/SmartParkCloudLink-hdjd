<template>
  <div class="admin-page">
    <el-page-header @back="$router.push('/admin/lots')" :title="overview.lot_name || '车场详情'" />
    <div v-loading="loading" class="mt16">
      <el-row :gutter="12">
        <el-col :span="12" v-for="c in cards" :key="c.title" class="mb12">
          <el-card class="stat-card" :style="{ borderTopColor: c.color }">
            <p class="stat-label">{{ c.title }}</p>
            <p class="stat-value" :style="{ color: c.color }">{{ c.value }}</p>
          </el-card>
        </el-col>
      </el-row>

      <el-card class="mt16">
        <template #header>
          <div class="section-header">
            <span>车位状态管理</span>
            <el-button size="small" type="primary" @click="syncLot">同步数据</el-button>
          </div>
        </template>
        <div class="spot-toolbar">
          <el-tag type="success" effect="plain">空闲 {{ spotCount.free }}</el-tag>
          <el-tag type="warning" effect="plain">预约 {{ spotCount.reserved }}</el-tag>
          <el-tag type="info" effect="plain">占用 {{ spotCount.occupied }}</el-tag>
        </div>
        <div class="spot-grid">
          <button
            v-for="s in spots"
            :key="s.id"
            class="spot-cell"
            :class="'spot-' + s.status"
            @click="openStatusDialog(s)"
          >
            <span class="spot-no">{{ s.spot_number }}</span>
            <span>{{ statusText(s.status) }}</span>
          </button>
        </div>
        <el-empty v-if="spots.length === 0" description="暂无车位数据" />
      </el-card>

      <el-card class="mt16">
        <template #header>近7天收入趋势</template>
        <div v-for="r in revenue" :key="r.date" class="trend-row">
          <span>{{ r.date.slice(5) }}</span>
          <span>¥{{ r.revenue }}</span>
        </div>
      </el-card>

      <el-card class="mt16">
        <template #header>今日流量</template>
        <p>进场：{{ flow.entries || 0 }} 辆</p>
        <p>出场：{{ flow.exits || 0 }} 辆</p>
      </el-card>

      <el-card class="mt16">
        <template #header>最近同步日志</template>
        <div v-for="log in syncLogs" :key="log.id" class="log-row">
          <el-tag :type="log.status === 'success' ? 'success' : 'danger'" size="small">{{ log.status }}</el-tag>
          <span>{{ log.message }}</span>
          <span class="log-time">{{ formatTime(log.created_at) }}</span>
        </div>
        <el-empty v-if="syncLogs.length === 0" description="暂无同步日志" :image-size="60" />
      </el-card>
    </div>

    <el-dialog v-model="statusDialog" title="调整车位状态" width="90%">
      <p class="dialog-title">{{ editingSpot?.spot_number }}</p>
      <el-radio-group v-model="nextStatus">
        <el-radio-button value="free">空闲</el-radio-button>
        <el-radio-button value="reserved">预约</el-radio-button>
        <el-radio-button value="occupied">占用</el-radio-button>
      </el-radio-group>
      <template #footer>
        <el-button @click="statusDialog = false">取消</el-button>
        <el-button type="primary" @click="saveSpotStatus">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../utils/api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const overview = ref({})
const revenue = ref([])
const flow = ref({})
const spots = ref([])
const syncLogs = ref([])
const loading = ref(false)
const cards = ref([])
const statusDialog = ref(false)
const editingSpot = ref(null)
const nextStatus = ref('free')

const spotCount = computed(() => ({
  free: spots.value.filter(s => s.status === 'free').length,
  reserved: spots.value.filter(s => s.status === 'reserved').length,
  occupied: spots.value.filter(s => s.status === 'occupied').length
}))

function statusText(s) {
  return { free: '空闲', reserved: '预约', occupied: '占用' }[s] || s
}

function formatTime(t) {
  return t ? new Date(t).toLocaleString('zh-CN') : '-'
}

async function fetch() {
  loading.value = true
  const id = route.params.id
  try {
    const [ov, rev, fl, sp, logs] = await Promise.all([
      api.get(`/admin/lots/${id}/overview`),
      api.get(`/admin/lots/${id}/revenue`),
      api.get(`/admin/lots/${id}/flow`),
      api.get(`/lots/${id}/spots`),
      api.get(`/lots/${id}/sync-logs`)
    ])
    overview.value = ov.data || {}
    revenue.value = rev.data || []
    flow.value = fl.data || {}
    spots.value = sp.data || []
    syncLogs.value = logs.data || []
    cards.value = [
      { title: '总车位', value: overview.value.total_spots, color: '#409EFF' },
      { title: '空闲车位', value: overview.value.available_spots, color: '#67C23A' },
      { title: '今日订单', value: overview.value.today_orders, color: '#E6A23C' },
      { title: '今日收入', value: `¥${overview.value.today_revenue}`, color: '#F56C6C' },
    ]
  } finally {
    loading.value = false
  }
}

function openStatusDialog(spot) {
  editingSpot.value = spot
  nextStatus.value = spot.status
  statusDialog.value = true
}

async function saveSpotStatus() {
  if (!editingSpot.value) return
  const res = await api.put(`/spots/${editingSpot.value.id}/status`, { status: nextStatus.value })
  if (res.code === 0) {
    ElMessage.success(res.msg || '车位状态已更新')
    statusDialog.value = false
    fetch()
  } else {
    ElMessage.error(res.msg || '车位状态更新失败')
  }
}

async function syncLot() {
  const id = route.params.id
  const res = await api.post(`/lots/${id}/sync`)
  if (res.code === 0) {
    ElMessage.success(res.msg || '同步成功')
    fetch()
  } else {
    ElMessage.error(res.msg || '同步失败')
  }
}

onMounted(fetch)
</script>

<style scoped>
.admin-page { padding-bottom: 20px; }
.mt16 { margin-top: 16px; }
.mb12 { margin-bottom: 12px; }
.stat-card { border-top: 3px solid; }
.stat-label { font-size: 12px; color: #909399; }
.stat-value { font-size: 24px; font-weight: 700; margin-top: 4px; }
.section-header { display: flex; justify-content: space-between; align-items: center; }
.spot-toolbar { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.spot-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.spot-cell { border: 1px solid #dcdfe6; border-radius: 8px; padding: 10px 4px; background: #fff; cursor: pointer; font-size: 12px; color: #606266; }
.spot-cell:hover { border-color: #409EFF; }
.spot-no { display: block; font-weight: 700; margin-bottom: 4px; color: #303133; }
.spot-free { background: #f0f9eb; border-color: #c2e7b0; }
.spot-reserved { background: #fdf6ec; border-color: #f5dab1; }
.spot-occupied { background: #f4f4f5; border-color: #d4d4d5; }
.trend-row, .log-row { display: flex; justify-content: space-between; align-items: center; gap: 8px; padding: 6px 0; border-bottom: 1px solid #f5f5f5; font-size: 13px; }
.trend-row:last-child, .log-row:last-child { border-bottom: none; }
.log-row span:nth-child(2) { flex: 1; }
.log-time { color: #909399; font-size: 12px; text-align: right; }
.dialog-title { font-weight: 700; margin-bottom: 12px; }
</style>
