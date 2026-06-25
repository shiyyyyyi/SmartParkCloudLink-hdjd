<template>
  <div class="admin-page">
    <el-page-header @back="$router.push('/admin/lots')" :title="overview.lot_name || '车场详情'" />
    <div v-loading="loading" class="mt16">
      <!-- 概览 -->
      <el-row :gutter="12">
        <el-col :span="12" v-for="c in cards" :key="c.title" class="mb12">
          <el-card class="stat-card" :style="{ borderTopColor: c.color }">
            <p class="stat-label">{{ c.title }}</p>
            <p class="stat-value" :style="{ color: c.color }">{{ c.value }}</p>
          </el-card>
        </el-col>
      </el-row>

      <!-- 收入趋势 -->
      <el-card class="mt16">
        <template #header>近7天收入趋势</template>
        <div v-for="r in revenue" :key="r.date" class="trend-row">
          <span>{{ r.date.slice(5) }}</span>
          <span>¥{{ r.revenue }}</span>
        </div>
      </el-card>

      <!-- 进出场流量 -->
      <el-card class="mt16">
        <template #header>今日流量</template>
        <p>进场：{{ flow.entries || 0 }} 辆</p>
        <p>出场：{{ flow.exits || 0 }} 辆</p>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../utils/api'

const route = useRoute()
const overview = ref({})
const revenue = ref([])
const flow = ref({})
const loading = ref(false)
const cards = ref([])

async function fetch() {
  loading.value = true
  const id = route.params.id
  const [ov, rev, fl] = await Promise.all([
    api.get(`/admin/lots/${id}/overview`),
    api.get(`/admin/lots/${id}/revenue`),
    api.get(`/admin/lots/${id}/flow`)
  ])
  overview.value = ov.data || {}
  revenue.value = rev.data || []
  flow.value = fl.data || {}
  cards.value = [
    { title: '总车位', value: overview.value.total_spots, color: '#409EFF' },
    { title: '空闲车位', value: overview.value.available_spots, color: '#67C23A' },
    { title: '今日订单', value: overview.value.today_orders, color: '#E6A23C' },
    { title: '今日收入', value: `¥${overview.value.today_revenue}`, color: '#F56C6C' },
  ]
  loading.value = false
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
.trend-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #f5f5f5; font-size: 13px; }
</style>
