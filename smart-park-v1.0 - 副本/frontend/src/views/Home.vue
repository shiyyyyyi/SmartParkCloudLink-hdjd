<template>
  <div class="home-page">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input v-model="keyword" placeholder="搜索停车场名称或地址" size="default" clearable @keyup.enter="searchNearby">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-button type="primary" @click="searchNearby" :icon="Search">搜索</el-button>
    </div>

    <!-- 快速筛选 -->
    <div class="filter-row">
      <el-radio-group v-model="sortBy" @change="updateMapMarkers" size="small">
        <el-radio-button value="distance">距离最近</el-radio-button>
        <el-radio-button value="price">价格最低</el-radio-button>
        <el-radio-button value="available">车位最多</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 地图 + 右侧面板 -->
    <div class="map-row">
      <!-- 高德地图容器 -->
      <div id="amap-container" class="map-container"></div>

      <!-- 右侧模拟面板 -->
      <div class="right-panel">
        <el-card class="sim-card">
          <h4>🔧 车牌识别模拟 (M6)</h4>
          <el-select v-model="simLotId" placeholder="选择车场" size="small" class="sim-select">
            <el-option v-for="l in lots" :key="l.id" :label="l.name" :value="l.id" />
          </el-select>
          <el-input v-model="simPlate" placeholder="车牌号" size="small" class="sim-input" />
          <el-button type="success" size="small" @click="simEntry" class="sim-btn">模拟入场</el-button>
          <el-button type="warning" size="small" @click="simExit" class="sim-btn">模拟出场</el-button>
        </el-card>
      </div>
    </div>

    <!-- 底部停车场列表卡片（半屏） -->
    <div class="bottom-panel" :class="{ expanded: panelExpanded }">
      <div class="panel-handle" @click="panelExpanded = !panelExpanded">
        <span>{{ panelExpanded ? '▼ 收起列表' : '▲ 附近停车场 (' + lots.length + '个)' }}</span>
      </div>
      <div class="panel-list" v-show="panelExpanded">
        <div
          v-for="lot in lots" :key="lot.id"
          class="lot-item"
          :class="{ active: activeLotId === lot.id }"
          @click="focusLot(lot)"
        >
          <div class="lot-item-left">
            <h4 class="lot-name">{{ lot.name }}</h4>
            <p class="lot-addr">{{ lot.address }}</p>
            <div class="lot-tags">
              <span class="tag-price">¥{{ lot.price_per_hour }}/h</span>
              <span v-if="lot.distance" class="tag-dist">{{ lot.distance }}km</span>
              <span class="tag-spots">共{{ lot.total_spots }}车位</span>
            </div>
          </div>
          <div class="lot-item-right">
            <el-tag :type="lot.available_spots > 10 ? 'success' : lot.available_spots > 0 ? 'warning' : 'danger'" size="small">
              {{ lot.available_spots > 0 ? lot.available_spots + '空闲' : '已满' }}
            </el-tag>
            <el-button type="primary" size="small" class="reserve-btn" @click.stop="openReserve(lot)" :disabled="lot.available_spots <= 0">
              预约
            </el-button>
          </div>
        </div>
        <el-empty v-if="!loading && lots.length === 0" description="附近暂无停车场" :image-size="60" />
      </div>
    </div>

    <!-- 停车场信息窗口（地图点击弹出） -->
    <div v-if="infoWindowLot" class="map-info-window" :style="infoWindowStyle">
      <div class="iw-header">
        <strong>{{ infoWindowLot.name }}</strong>
        <el-tag :type="infoWindowLot.available_spots > 10 ? 'success' : infoWindowLot.available_spots > 0 ? 'warning' : 'danger'" size="small">
          {{ infoWindowLot.available_spots > 0 ? infoWindowLot.available_spots + '空闲' : '已满' }}
        </el-tag>
      </div>
      <p class="iw-addr">{{ infoWindowLot.address }}</p>
      <p class="iw-info">¥{{ infoWindowLot.price_per_hour }}/小时 · {{ infoWindowLot.total_spots }}车位</p>
      <div class="iw-actions">
        <el-button size="small" @click="$router.push(`/lots/${infoWindowLot.id}`)">查看详情</el-button>
        <el-button size="small" type="primary" @click="openReserve(infoWindowLot)" :disabled="infoWindowLot.available_spots <= 0">预约车位</el-button>
      </div>
    </div>

    <!-- 预约弹窗 -->
    <el-dialog v-model="showReserve" title="预约车位" width="90%">
      <el-form label-width="80px">
        <el-form-item label="停车场">
          <span>{{ reserveLot?.name }}</span>
        </el-form-item>
        <el-form-item label="车牌号">
          <el-input v-model="reservePlate" placeholder="请输入车牌号" size="large" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReserve = false">取消</el-button>
        <el-button type="primary" @click="doReserve" :loading="reserving">确认预约</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import api from '../utils/api'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const lots = ref([])
const keyword = ref('')
const sortBy = ref('distance')
const loading = ref(false)
const simLotId = ref(null)
const simPlate = ref('浙AT9999')
const panelExpanded = ref(true)
const activeLotId = ref(null)

// 地图相关
let map = null
let markers = []
let currentPosition = [115.8604, 28.7443] // 默认华东交通大学（南昌）

const infoWindowLot = ref(null)
const infoWindowStyle = reactive({ top: '0px', left: '0px', display: 'none' })

// 获取停车场数据
async function fetchLots() {
  loading.value = true
  const params = { page: 1, page_size: 50, sort_by: sortBy.value, lat: currentPosition[1], lng: currentPosition[0] }
  if (keyword.value) params.keyword = keyword.value
  try {
    const res = await api.get('/lots', { params })
    lots.value = (res.data && res.data.data ? res.data.data : (res.data || []))
  } catch {
    lots.value = []
  }
  if (simLotId.value === null && lots.value.length > 0) simLotId.value = lots.value[0].id
  loading.value = false
}

// 初始化高德地图
function initMap() {
  if (!window.AMap) {
    setTimeout(initMap, 500)
    return
  }
  map = new AMap.Map('amap-container', {
    zoom: 13,
    center: currentPosition,
    resizeEnable: true,
    mapStyle: 'amap://styles/light'
  })

  // 添加定位控件
  map.plugin('AMap.Geolocation', () => {
    const geolocation = new AMap.Geolocation({
      enableHighAccuracy: true,
      timeout: 5000,
      showButton: true,
      buttonPosition: 'RB',
      buttonOffset: new AMap.Pixel(10, 100),
      zoomToAccuracy: true
    })
    map.addControl(geolocation)
    geolocation.getCurrentPosition((status, result) => {
      if (status === 'complete' && result.position) {
        currentPosition = [result.position.lng, result.position.lat]
        map.setCenter(currentPosition)
        fetchLots().then(updateMapMarkers)
      } else {
        fetchLots().then(updateMapMarkers)
      }
    })
  })

  // 地图点击空白处关闭信息窗
  map.on('click', () => {
    infoWindowLot.value = null
    infoWindowStyle.display = 'none'
  })

  fetchLots().then(updateMapMarkers)
}

// 更新地图标记点
function updateMapMarkers() {
  if (!map) return
  // 清除旧标记
  markers.forEach(m => map.remove(m))
  markers = []

  // 按排序重新排列
  let sorted = [...lots.value]
  if (sortBy.value === 'distance') {
    sorted.sort((a, b) => (a.distance || 999) - (b.distance || 999))
  } else if (sortBy.value === 'price') {
    sorted.sort((a, b) => a.price_per_hour - b.price_per_hour)
  } else if (sortBy.value === 'available') {
    sorted.sort((a, b) => b.available_spots - a.available_spots)
  }

  sorted.forEach((lot, index) => {
    if (!lot.lat || !lot.lng) return
    const position = [lot.lng, lot.lat]
    const ratio = lot.total_spots > 0 ? lot.available_spots / lot.total_spots : 0
    const color = ratio > 0.3 ? '#52c41a' : ratio > 0.1 ? '#faad14' : '#f5222d'
    const content = `<div style="background:${color};color:#fff;width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:bold;box-shadow:0 2px 6px rgba(0,0,0,0.3);border:2px solid #fff;">${lot.available_spots}</div>`

    const marker = new AMap.Marker({
      position,
      content,
      anchor: 'center',
      offset: new AMap.Pixel(0, 0),
      zIndex: 100 - index,
      extData: lot
    })

    marker.on('click', () => {
      showInfoWindow(lot, position)
    })

    map.add(marker)
    markers.push(marker)
  })

  // 调整视野包含所有标记
  if (markers.length > 0) {
    map.setFitView(null, false, [60, 60, 300, 60])
  }
}

// 显示信息窗口
function showInfoWindow(lot, position) {
  infoWindowLot.value = lot
  activeLotId.value = lot.id

  // 将经纬度转为屏幕坐标
  const pixel = map.lngLatToContainer(position)
  const mapContainer = document.getElementById('amap-container')
  const rect = mapContainer.getBoundingClientRect()

  let top = pixel.y - 170
  let left = pixel.x - 120

  // 边界处理
  if (top < 10) top = 10
  if (left < 10) left = 10
  if (left + 240 > rect.width) left = rect.width - 250
  if (top + 160 > rect.height) top = rect.height - 170

  infoWindowStyle.top = top + 'px'
  infoWindowStyle.left = left + 'px'
  infoWindowStyle.display = 'block'
}

// 聚焦停车场
function focusLot(lot) {
  if (!map || !lot.lat || !lot.lng) return
  const position = [lot.lng, lot.lat]
  map.setZoomAndCenter(16, position)
  showInfoWindow(lot, position)
  // 滚动列表到对应项
  panelExpanded.value = false
}

// 搜索周边
function searchNearby() {
  fetchLots().then(updateMapMarkers)
}

// 预约相关
const showReserve = ref(false)
const reserveLot = ref(null)
const reservePlate = ref('')
const reserving = ref(false)

async function openReserve(lot) {
  reserveLot.value = lot
  // 优先从后端获取个人信息中的车牌号
  try {
    const meRes = await api.get('/auth/me')
    if (meRes.code === 0 && meRes.data && meRes.data.plate_numbers) {
      reservePlate.value = meRes.data.plate_numbers.split(',')[0].trim()
    } else {
      reservePlate.value = simPlate.value || ''
    }
  } catch {
    reservePlate.value = simPlate.value || ''
  }
  showReserve.value = true
}

async function doReserve() {
  if (!reservePlate.value) return ElMessage.warning('请输入车牌号')
  reserving.value = true
  try {
    const res = await api.post('/reservations', { lot_id: reserveLot.value.id, plate_number: reservePlate.value })
    if (res.code === 0 || res.data) {
      ElMessage.success(`预约成功！${reserveLot.value.name}，请15分钟内到场确认`)
      showReserve.value = false
      fetchLots().then(updateMapMarkers)
    } else {
      ElMessage.error(res.msg || '预约失败')
    }
  } catch {
    ElMessage.error('网络请求失败')
  }
  reserving.value = false
}

// 模拟入场出场
async function simEntry() {
  try {
    const res = await api.post('/license-plate/events', { lot_id: simLotId.value, plate_number: simPlate.value, event_type: 'entry' })
    if (res.code === 0 || res.data) {
      ElMessage.success(res.msg || '入场成功')
      fetchLots().then(updateMapMarkers)
    } else ElMessage.error(res.msg || '入场失败')
  } catch { ElMessage.error('网络请求失败') }
}

async function simExit() {
  try {
    const res = await api.post('/license-plate/events', { lot_id: simLotId.value, plate_number: simPlate.value, event_type: 'exit' })
    if (res.code === 0 || res.data) {
      ElMessage.success(res.msg || '出场成功')
      fetchLots().then(updateMapMarkers)
    } else ElMessage.error(res.msg || '出场失败')
  } catch { ElMessage.error('网络请求失败') }
}

onMounted(() => {
  nextTick(initMap)
})

onUnmounted(() => {
  if (map) {
    map.destroy()
    map = null
  }
})
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 100px);
  position: relative;
  overflow: hidden;
}

.search-bar {
  display: flex;
  gap: 8px;
  padding: 8px 12px;
  background: #fff;
  z-index: 10;
  flex-shrink: 0;
}
.search-bar .el-input { flex: 1; }

.filter-row {
  padding: 0 12px 8px;
  background: #fff;
  z-index: 10;
  flex-shrink: 0;
}

.map-row {
  display: flex;
  flex: 1;
  min-height: 0;
  gap: 0;
}

.map-container {
  flex: 1;
  min-height: 300px;
  position: relative;
}

.right-panel {
  width: 170px;
  flex-shrink: 0;
  padding: 8px;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.sim-card {
  height: 100%;
}
.sim-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  gap: 8px;
  height: 100%;
}
.sim-card h4 {
  margin: 0;
  color: #409EFF;
  font-size: 12px;
  text-align: center;
  line-height: 1.3;
}
.sim-select { width: 100%; }
.sim-input { width: 100%; }
.sim-btn { width: 100%; }

/* 信息窗口 */
.map-info-window {
  position: absolute;
  z-index: 1000;
  background: #fff;
  border-radius: 8px;
  padding: 12px;
  width: 240px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  pointer-events: auto;
}
.map-info-window .iw-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.map-info-window .iw-addr {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}
.map-info-window .iw-info {
  font-size: 12px;
  color: #606266;
  margin-bottom: 8px;
}
.map-info-window .iw-actions {
  display: flex;
  gap: 8px;
}

/* 底部面板 */
.bottom-panel {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: #fff;
  border-radius: 16px 16px 0 0;
  box-shadow: 0 -2px 12px rgba(0,0,0,0.1);
  transition: max-height 0.3s ease;
  max-height: 42px;
  overflow: hidden;
}
.bottom-panel.expanded {
  max-height: 50vh;
  overflow-y: auto;
}
.panel-handle {
  padding: 12px 16px;
  text-align: center;
  cursor: pointer;
  font-size: 13px;
  color: #409EFF;
  font-weight: 500;
  border-bottom: 1px solid #f0f0f0;
  user-select: none;
}
.panel-list {
  padding: 0;
}

.lot-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
  transition: background 0.2s;
}
.lot-item:hover, .lot-item.active {
  background: #f0f7ff;
}
.lot-item-left {
  flex: 1;
  min-width: 0;
}
.lot-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.lot-addr {
  font-size: 11px;
  color: #909399;
  margin: 0 0 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.lot-tags {
  display: flex;
  gap: 8px;
  font-size: 11px;
  color: #606266;
}
.tag-price { color: #f5222d; font-weight: 600; }
.tag-dist { color: #409EFF; }
.tag-spots { color: #909399; }

.lot-item-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  flex-shrink: 0;
  margin-left: 12px;
}
.reserve-btn { font-size: 12px; }


</style>
