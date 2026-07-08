<template>
  <div class="page">
    <div class="page-head">
      <div>
        <h3>反向寻车</h3>
        <p>定位停车中的车辆，查看车场、区域、车位和寻车路线</p>
      </div>
      <el-button size="small" @click="fetchActiveCars" :loading="loadingActive">刷新</el-button>
    </div>

    <el-card>
      <div class="search-card">
        <el-input v-model="plateNumber" placeholder="请输入车牌号，如：浙AT9999" size="large" clearable @keyup.enter="findCar">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button type="primary" size="large" @click="findCar" :loading="loading">查找车辆</el-button>
      </div>
      <div class="quick-row">
        <el-button v-for="car in activeCars" :key="car.order_id" size="small" @click="locateCar(car)">
          {{ car.plate_number }} · {{ car.spot_number }}
        </el-button>
        <span v-if="!loadingActive && activeCars.length === 0" class="dim">暂无停车中车辆，可先在首页模拟入场或在预约页到场确认</span>
      </div>
    </el-card>

    <el-card v-if="result" class="mt16 result-card">
      <div class="result-header">
        <el-icon :size="34" color="#409EFF"><MapLocation /></el-icon>
        <div>
          <h3>车辆已定位</h3>
          <p class="plate">{{ result.plate_number }}</p>
        </div>
        <el-tag :type="result.order_status === 'parking' ? 'success' : 'warning'" size="small">
          {{ result.order_status === 'parking' ? '停车中' : '待支付' }}
        </el-tag>
      </div>

      <div class="location-map">
        <div class="map-node entrance">入口</div>
        <div class="map-line"></div>
        <div class="map-node area">{{ result.area_name }}</div>
        <div class="map-line"></div>
        <div class="map-node car">{{ result.spot_number }}</div>
      </div>

      <div class="info-grid">
        <div class="info-item">
          <span class="label">停车场</span>
          <span class="value">{{ result.lot_name }}</span>
        </div>
        <div class="info-item">
          <span class="label">车位号</span>
          <span class="value highlight">{{ result.spot_number }}</span>
        </div>
        <div class="info-item">
          <span class="label">区域/楼层</span>
          <span class="value">{{ result.area_name }} · {{ result.floor }}</span>
        </div>
        <div class="info-item">
          <span class="label">已停时长</span>
          <span class="value">{{ durationText }}</span>
        </div>
        <div class="info-item wide">
          <span class="label">入场时间</span>
          <span class="value">{{ formatTime(result.entry_time) }}</span>
        </div>
        <div class="info-item wide">
          <span class="label">车场地址</span>
          <span class="value">{{ result.lot_address }}</span>
        </div>
      </div>

      <el-divider />
      <div class="guide-title">寻车路线</div>
      <el-timeline class="guide-list">
        <el-timeline-item v-for="(step, index) in result.guide_steps" :key="index" :timestamp="`步骤 ${index + 1}`">
          {{ step }}
        </el-timeline-item>
      </el-timeline>

      <div class="actions">
        <el-button type="primary" @click="openNavigation">
          <el-icon><Position /></el-icon>
          打开导航
        </el-button>
        <el-button @click="$router.push('/orders')">查看订单</el-button>
      </div>
    </el-card>

    <el-empty v-if="!loading && !result && searched" description="未找到停车中车辆，请确认车牌号或先完成入场" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../utils/api'
import { firstPlateNumber } from '../utils/plates'
import { Search, MapLocation, Position } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const plateNumber = ref('')
const loading = ref(false)
const loadingActive = ref(false)
const searched = ref(false)
const result = ref(null)
const activeCars = ref([])

const durationText = computed(() => {
  const minutes = result.value?.duration_minutes
  if (typeof minutes === 'number') return formatDuration(minutes)
  if (!result.value?.entry_time) return ''
  const entry = new Date(result.value.entry_time)
  return formatDuration(Math.max(0, Math.floor((new Date() - entry) / 1000 / 60)))
})

function formatDuration(minutes) {
  if (minutes < 60) return `${minutes} 分钟`
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours} 小时 ${mins} 分钟`
}

async function fetchDefaultPlate() {
  try {
    const res = await api.get('/auth/me')
    if (res.code === 0 && res.data?.plate_numbers && !plateNumber.value) {
      plateNumber.value = firstPlateNumber(res.data.plate_numbers)
    }
  } catch {}
}

async function fetchActiveCars() {
  loadingActive.value = true
  try {
    const res = await api.get('/find-car/active')
    if (res.code === 0) {
      activeCars.value = res.data || []
      if (activeCars.value.length > 0 && !result.value) {
        locateCar(activeCars.value[0])
      }
    }
  } finally {
    loadingActive.value = false
  }
}

function locateCar(car) {
  result.value = car
  plateNumber.value = car.plate_number
  searched.value = true
}

async function findCar() {
  if (!plateNumber.value) return ElMessage.warning('请输入车牌号')
  loading.value = true
  searched.value = true
  result.value = null
  try {
    const res = await api.get('/find-car', { params: { plate_number: plateNumber.value } })
    if (res.code === 0 && res.data) {
      result.value = res.data
      ElMessage.success('车辆定位成功')
    } else {
      ElMessage.warning(res.msg || '未找到该车辆的停车记录')
    }
  } finally {
    loading.value = false
  }
}

function openNavigation() {
  if (!result.value?.lng || !result.value?.lat) return ElMessage.warning('暂无车场坐标')
  const name = encodeURIComponent(`${result.value.lot_name}-${result.value.spot_number}`)
  window.open(`https://uri.amap.com/marker?position=${result.value.lng},${result.value.lat}&name=${name}`, '_blank')
}

function formatTime(t) { return t ? new Date(t).toLocaleString('zh-CN') : '-' }

onMounted(() => {
  fetchDefaultPlate()
  fetchActiveCars()
})
</script>

<style scoped>
.page { padding-bottom: 20px; }
.page-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 16px; }
h3 { margin-bottom: 4px; color: #303133; }
.page-head p { font-size: 13px; color: #909399; }
.mt16 { margin-top: 16px; }
.search-card { display: flex; gap: 10px; }
.search-card .el-input { flex: 1; }
.quick-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
.dim { font-size: 13px; color: #909399; }
.result-card .result-header { display: flex; align-items: center; gap: 14px; }
.result-card .result-header > div { flex: 1; }
.result-card .plate { font-size: 20px; font-weight: 700; color: #409EFF; letter-spacing: 1px; }
.location-map { display: flex; align-items: center; padding: 20px 12px; margin: 16px 0; border-radius: 8px; background: #f5f9ff; border: 1px solid #d9ecff; }
.map-node { width: 76px; height: 44px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; background: #fff; border: 1px solid #c6e2ff; color: #409EFF; }
.map-node.car { background: #ecf5ff; border-color: #409EFF; }
.map-line { flex: 1; height: 2px; background: #a0cfff; min-width: 24px; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 12px 0; }
.info-item { padding: 10px; border-radius: 8px; background: #fafafa; }
.info-item.wide { grid-column: 1 / -1; }
.info-item .label { display: block; font-size: 12px; color: #909399; margin-bottom: 4px; }
.info-item .value { font-size: 15px; color: #303133; font-weight: 500; word-break: break-all; }
.info-item .value.highlight { color: #67C23A; font-size: 18px; font-weight: 700; }
.guide-title { font-weight: 700; margin-bottom: 12px; color: #303133; }
.guide-list { padding-left: 4px; }
.actions { display: flex; gap: 10px; margin-top: 12px; }
@media (max-width: 640px) {
  .search-card { flex-direction: column; }
  .info-grid { grid-template-columns: 1fr; }
  .location-map { padding: 16px 8px; }
  .map-node { width: 66px; font-size: 12px; }
}
</style>
