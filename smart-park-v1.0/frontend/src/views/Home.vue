<template>
  <div class="home-page">
    <!-- 搜索栏 (M3 城市停车一张图) -->
    <div class="search-bar">
      <el-input v-model="keyword" placeholder="搜索停车场名称或地址" size="large" clearable @keyup.enter="search">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-button type="primary" size="large" @click="search" :icon="Search">搜索</el-button>
    </div>

    <!-- 快速筛选 -->
    <div class="filter-row">
      <el-radio-group v-model="sortBy" @change="fetchLots" size="small">
        <el-radio-button value="distance">距离最近</el-radio-button>
        <el-radio-button value="price">价格最低</el-radio-button>
        <el-radio-button value="available">车位最多</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 停车场列表 (M3) -->
    <div v-loading="loading" class="lot-list">
      <el-card v-for="lot in lots" :key="lot.id" class="lot-card" shadow="hover" @click="$router.push(`/lots/${lot.id}`)">
        <div class="lot-card-header">
          <h3 class="lot-name">{{ lot.name }}</h3>
          <el-tag :type="lot.available_spots > 10 ? 'success' : lot.available_spots > 0 ? 'warning' : 'danger'" size="small">
            {{ lot.available_spots > 0 ? `空闲 ${lot.available_spots}` : '已满' }}
          </el-tag>
        </div>
        <p class="lot-address"><el-icon><Location /></el-icon> {{ lot.address }}</p>
        <div class="lot-meta">
          <span><el-icon><Money /></el-icon> ¥{{ lot.price_per_hour }}/小时</span>
          <span v-if="lot.distance"><el-icon><Position /></el-icon> {{ lot.distance }}km</span>
          <span><el-icon><Van /></el-icon> 共{{ lot.total_spots }}车位</span>
        </div>
        <!-- 预约按钮 (M5) -->
        <el-button type="primary" size="small" @click.stop="quickReserve(lot)" :disabled="lot.available_spots <= 0">
          立即预约
        </el-button>
      </el-card>
      <el-empty v-if="!loading && lots.length === 0" description="暂无停车场数据" />
    </div>

    <!-- 模拟入场 (M6) -->
    <el-card class="sim-card">
      <h4>🔧 车牌识别模拟 (M6)</h4>
      <div class="sim-row">
        <el-select v-model="simLotId" placeholder="选择车场" size="small" style="width:160px">
          <el-option v-for="l in lots" :key="l.id" :label="l.name" :value="l.id" />
        </el-select>
        <el-input v-model="simPlate" placeholder="车牌号" size="small" style="width:130px" />
        <el-button type="success" size="small" @click="simEntry">模拟入场</el-button>
        <el-button type="warning" size="small" @click="simExit">模拟出场</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../utils/api'
import { Search, Location, Money, Position, Van } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const lots = ref([])
const keyword = ref('')
const sortBy = ref('distance')
const loading = ref(false)
const simLotId = ref(null)
const simPlate = ref('浙AT9999')

async function fetchLots() {
  loading.value = true
  const params = { page: 1, page_size: 50, sort_by: sortBy.value, lat: 30.28, lng: 120.15 }
  if (keyword.value) params.keyword = keyword.value
  const res = await api.get('/lots', { params })
  lots.value = res.data || []
  if (simLotId.value === null && lots.value.length > 0) simLotId.value = lots.value[0].id
  loading.value = false
}

function search() { fetchLots() }

async function quickReserve(lot) {
  const res = await api.post('/reservations', { lot_id: lot.id, plate_number: '浙AT9999' })
  if (res.code === 0) {
    ElMessage.success(`预约成功！${lot.name}，请15分钟内到场确认`)
  } else {
    ElMessage.error(res.msg)
  }
}

async function simEntry() {
  const res = await api.post('/license-plate/events', { lot_id: simLotId.value, plate_number: simPlate.value, event_type: 'entry' })
  if (res.code === 0) {
    ElMessage.success(res.msg)
    fetchLots()
  } else ElMessage.error(res.msg)
}

async function simExit() {
  const res = await api.post('/license-plate/events', { lot_id: simLotId.value, plate_number: simPlate.value, event_type: 'exit' })
  if (res.code === 0) {
    ElMessage.success(res.msg)
    fetchLots()
  } else ElMessage.error(res.msg)
}

onMounted(fetchLots)
</script>

<style scoped>
.search-bar { display: flex; gap: 8px; margin-bottom: 12px; }
.search-bar .el-input { flex: 1; }
.filter-row { margin-bottom: 12px; }
.lot-card { margin-bottom: 12px; cursor: pointer; }
.lot-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.lot-name { font-size: 16px; font-weight: 600; color: #303133; }
.lot-address { font-size: 12px; color: #909399; margin-bottom: 8px; }
.lot-meta { display: flex; gap: 12px; font-size: 12px; color: #606266; margin-bottom: 12px; flex-wrap: wrap; }
.sim-card { margin-top: 16px; }
.sim-card h4 { margin-bottom: 12px; color: #409EFF; }
.sim-row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
</style>
