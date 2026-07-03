<template>
  <div class="admin-page">
    <el-page-header @back="$router.push('/home')" title="管理后台 (M13)" />
    <div v-loading="loading">
      <!-- 概览卡片 -->
      <el-row :gutter="12" class="mt16">
        <el-col :span="12" v-for="card in cards" :key="card.title" class="mb12">
          <el-card class="stat-card" :style="{ borderTopColor: card.color }">
            <p class="stat-label">{{ card.title }}</p>
            <p class="stat-value" :style="{ color: card.color }">{{ card.value }}</p>
          </el-card>
        </el-col>
      </el-row>

      <!-- 收入趋势图 -->
      <el-card class="mt16">
        <template #header>近7天收入趋势</template>
        <div ref="revenueChart" style="height:220px"></div>
      </el-card>

      <!-- 饱和度分析 -->
      <el-card class="mt16">
        <template #header>停车场饱和度</template>
        <div ref="saturationChart" style="height:280px"></div>
      </el-card>

      <!-- 车场列表 -->
      <el-card class="mt16">
        <template #header>停车场运营</template>
        <div v-for="lot in lots" :key="lot.id" class="lot-row" @click="$router.push(`/admin/lots/${lot.id}`)">
          <div>
            <p class="lot-name">{{ lot.name }}</p>
            <p class="lot-sub">可用 {{ lot.available_spots }}/{{ lot.total_spots }} · ¥{{ lot.price_per_hour }}/h</p>
          </div>
          <el-tag :type="lot.status === 'active' ? 'success' : 'danger'">{{ lot.status === 'active' ? '运行中' : '停用' }}</el-tag>
        </div>
      </el-card>

      <!-- 快捷操作 -->
      <el-card class="mt16">
        <template #header>快捷操作</template>
        <el-space wrap>
          <el-button type="primary" @click="$router.push('/admin/lots')">车场管理</el-button>
          <el-button type="success" @click="$router.push('/admin/orders')">订单管理</el-button>
        </el-space>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import api from '../../utils/api'
import * as echarts from 'echarts'

const stats = ref({})
const lots = ref([])
const loading = ref(false)
const cards = ref([])
const revenueChart = ref(null)
const saturationChart = ref(null)

async function fetch() {
  loading.value = true
  const [dashRes, lotRes, revenueRes, saturationRes] = await Promise.all([
    api.get('/admin/dashboard'),
    api.get('/admin/lots', { params: { page: 1, page_size: 10 } }),
    api.get('/analytics/revenue-trend', { params: { days: 7 } }),
    api.get('/analytics/saturation')
  ])
  const d = dashRes.data
  stats.value = d
  lots.value = lotRes.data || []
  cards.value = [
    { title: '车场总数', value: d.total_lots, color: '#409EFF' },
    { title: '空闲车位', value: d.free_spots, color: '#67C23A' },
    { title: '今日订单', value: d.today_orders, color: '#E6A23C' },
    { title: '今日收入', value: `¥${d.today_revenue}`, color: '#F56C6C' },
  ]
  loading.value = false

  await nextTick()
  renderRevenueChart(revenueRes.data || [])
  renderSaturationChart(saturationRes.data || [])
}

function renderRevenueChart(data) {
  if (!revenueChart.value) return
  const chart = echarts.init(revenueChart.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 10, bottom: 30 },
    xAxis: { type: 'category', data: data.map(d => d.date), axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: '收入(元)' },
    series: [{ data: data.map(d => d.revenue), type: 'bar', itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] } }]
  })
}

function renderSaturationChart(data) {
  if (!saturationChart.value) return
  const chart = echarts.init(saturationChart.value)
  const colors = { high: '#F56C6C', medium: '#E6A23C', low: '#67C23A' }
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 100, right: 60, top: 10, bottom: 20 },
    yAxis: { type: 'category', data: data.map(d => d.lot_name), axisLabel: { fontSize: 11 } },
    xAxis: { type: 'value', name: '饱和度(%)', max: 100 },
    series: [{
      data: data.map(d => ({
        value: d.saturation,
        itemStyle: { color: d.level === 'high' ? '#F56C6C' : d.level === 'medium' ? '#E6A23C' : '#67C23A' }
      })),
      type: 'bar',
      label: { show: true, position: 'right', formatter: '{c}%' }
    }]
  })
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
.lot-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #f0f0f0; cursor: pointer; }
.lot-row:last-child { border-bottom: none; }
.lot-name { font-size: 14px; font-weight: 600; }
.lot-sub { font-size: 12px; color: #909399; margin-top: 2px; }
</style>
