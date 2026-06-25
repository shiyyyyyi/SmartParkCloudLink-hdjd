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
import { ref, onMounted } from 'vue'
import api from '../../utils/api'

const stats = ref({})
const lots = ref([])
const loading = ref(false)

const cards = ref([])

async function fetch() {
  loading.value = true
  const [dashRes, lotRes] = await Promise.all([api.get('/admin/dashboard'), api.get('/admin/lots', { params: { page: 1, page_size: 10 } })])
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
