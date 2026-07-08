<template>
  <div class="home-page">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input v-model="keyword" placeholder="输入目的地，如：南昌西站、华东交通大学、万达广场" size="large" clearable @keyup.enter="searchNearby">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-button type="primary" size="large" @click="searchNearby" :loading="searching" :icon="Search">搜索目的地</el-button>
    </div>

    <!-- 快速筛选 -->
    <div class="filter-row">
      <el-radio-group v-model="sortBy" @change="handleSortChange" size="small">
        <el-radio-button value="distance">距离最近</el-radio-button>
        <el-radio-button value="price">价格最低</el-radio-button>
        <el-radio-button value="available">车位最多</el-radio-button>
      </el-radio-group>
      <div v-if="destination" class="destination-chip">
        当前目标：<strong>{{ destination.name }}</strong>
        <span v-if="destination.address">{{ destination.address }}</span>
      </div>
    </div>

    <div class="summary-row">
      <div class="summary-card">
        <span class="summary-label">运营车场</span>
        <strong>{{ lots.length }}</strong>
      </div>
      <div class="summary-card">
        <span class="summary-label">剩余车位</span>
        <strong>{{ totalAvailable }}</strong>
      </div>
      <div class="summary-card">
        <span class="summary-label">最低价格</span>
        <strong>¥{{ minPrice }}/h</strong>
      </div>
      <div class="summary-card">
        <span class="summary-label">最近距离</span>
        <strong>{{ nearestDistance }}</strong>
      </div>
    </div>

    <!-- 地图 + 右侧面板 -->
    <div class="map-row">
      <!-- 高德地图容器 -->
      <div class="map-shell">
        <div id="amap-container" class="map-container"></div>

        <button class="sim-fab" @click="showSimPanel = !showSimPanel">
          {{ showSimPanel ? '收起模拟' : '车牌识别模拟' }}
        </button>

        <transition name="float">
          <div v-if="showSimPanel" class="sim-float">
            <div class="sim-float-head">
              <div>
                <h4>车牌识别模拟</h4>
                <p>演示入场、出场、计费和寻车闭环</p>
              </div>
              <button class="float-close" @click="showSimPanel = false">×</button>
            </div>
            <el-select v-model="simLotId" placeholder="选择车场" size="large" class="sim-select" :disabled="simLots.length === 0">
              <el-option v-for="l in simLots" :key="l.id" :label="l.name" :value="l.id" />
            </el-select>
            <el-input v-model="simPlate" placeholder="请输入车牌号" size="large" class="sim-input" />
            <div class="sim-actions">
              <el-button type="success" size="large" @click="simEntry">模拟入场</el-button>
              <el-button type="warning" size="large" @click="simExit">模拟出场</el-button>
            </div>
          </div>
        </transition>

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
          <p v-if="infoWindowLot.source === 'amap'" class="iw-note">高德周边停车场，价格和空位为系统估算</p>
          <div class="iw-actions">
            <el-button size="small" @click="infoWindowLot.source === 'amap' ? focusLot(infoWindowLot) : $router.push(`/lots/${infoWindowLot.id}`)">
              {{ infoWindowLot.source === 'amap' ? '查看位置' : '查看详情' }}
            </el-button>
            <el-button
              size="small"
              type="primary"
              @click="primaryLotAction(infoWindowLot)"
              :disabled="infoWindowLot.source !== 'amap' && infoWindowLot.available_spots <= 0"
            >
              {{ infoWindowLot.source === 'amap' ? '导航' : '预约车位' }}
            </el-button>
          </div>
        </div>
      </div>

      <!-- 右侧表单面板 -->
      <div class="right-panel">
        <div class="ai-card">
          <div class="ai-card-head">
            <div>
              <span class="ai-kicker">本地评分推荐</span>
              <h4>推荐停车地</h4>
            </div>
            <el-tag size="small" type="success" effect="plain">{{ aiModeLabel }}</el-tag>
          </div>
          <div v-if="aiRecommendation" class="ai-body">
            <div class="ai-lot-name">{{ aiRecommendation.lot.name }}</div>
            <p class="ai-reason">{{ aiRecommendation.summary }}</p>
            <div class="ai-score-row">
              <span>综合评分</span>
              <strong>{{ aiRecommendation.score }}分</strong>
            </div>
            <div class="ai-metrics">
              <span>{{ aiRecommendation.lot.distance ? aiRecommendation.lot.distance + 'km' : '距离未知' }}</span>
              <span>¥{{ aiRecommendation.lot.price_per_hour }}/h</span>
              <span>{{ aiRecommendation.lot.available_spots }}空闲</span>
            </div>
            <div class="ai-actions">
              <el-button size="small" type="primary" @click="focusLot(aiRecommendation.lot)">查看位置</el-button>
              <el-button
                size="small"
                @click="primaryLotAction(aiRecommendation.lot)"
                :disabled="aiRecommendation.lot.source !== 'amap' && aiRecommendation.lot.available_spots <= 0"
              >
                {{ aiRecommendation.lot.source === 'amap' ? '导航' : '预约' }}
              </el-button>
            </div>
          </div>
          <el-empty v-else description="暂无可推荐车场" :image-size="48" />
        </div>

        <!-- 停车场列表侧栏，不遮挡地图主体 -->
        <div class="bottom-panel" :class="{ expanded: panelExpanded }">
          <div class="panel-handle" @click="panelExpanded = !panelExpanded">
            <span>{{ panelExpanded ? '收起' + panelTitle : '展开' + panelTitle + ' (' + lots.length + '个)' }}</span>
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
                  <span v-if="lot.source === 'amap'" class="tag-source">高德POI</span>
                </div>
              </div>
              <div class="lot-item-right">
                <el-tag :type="lot.available_spots > 10 ? 'success' : lot.available_spots > 0 ? 'warning' : 'danger'" size="small">
                  {{ lot.available_spots > 0 ? lot.available_spots + '空闲' : '已满' }}
                </el-tag>
                <el-button
                  type="primary"
                  size="small"
                  class="reserve-btn"
                  @click.stop="primaryLotAction(lot)"
                  :disabled="lot.source !== 'amap' && lot.available_spots <= 0"
                >
                  {{ lot.source === 'amap' ? '导航' : '预约' }}
                </el-button>
              </div>
            </div>
            <el-empty v-if="!loading && lots.length === 0" description="周边暂无停车场" :image-size="60" />
          </div>
        </div>
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
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import api from '../utils/api'
import { firstPlateNumber } from '../utils/plates'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const lots = ref([])
const keyword = ref('')
const sortBy = ref('distance')
const loading = ref(false)
const searching = ref(false)
const simLotId = ref(null)
const simPlate = ref('浙AT9999')
const showSimPanel = ref(false)
const panelExpanded = ref(true)
const activeLotId = ref(null)
const destination = ref(null)
const aiRecommendation = ref(null)
const aiModeLabel = '本地评分'

// 地图相关
let map = null
let markers = []
let destinationMarker = null
let currentPosition = [115.8604, 28.7443] // 默认华东交通大学（南昌）

const infoWindowLot = ref(null)
const infoWindowStyle = reactive({ top: '0px', left: '0px', display: 'none' })

const totalAvailable = computed(() => lots.value.reduce((sum, lot) => sum + (lot.available_spots || 0), 0))
const minPrice = computed(() => {
  if (lots.value.length === 0) return '-'
  return Math.min(...lots.value.map(lot => lot.price_per_hour || 0))
})
const nearestDistance = computed(() => {
  const distances = lots.value.map(lot => lot.distance).filter(v => typeof v === 'number')
  if (distances.length === 0) return '-'
  return `${Math.min(...distances).toFixed(2)}km`
})

const simLots = computed(() => lots.value.filter(lot => lot.source !== 'amap'))
const panelTitle = computed(() => destination.value ? '目标周边停车场' : '附近停车场')

function buildLocalRecommendation(list) {
  const candidates = list.filter(lot => lot.available_spots > 0)
  if (candidates.length === 0) return null

  const distances = candidates.map(lot => typeof lot.distance === 'number' ? lot.distance : 999)
  const prices = candidates.map(lot => lot.price_per_hour || 0)
  const available = candidates.map(lot => lot.available_spots || 0)
  const maxDistance = Math.max(...distances, 1)
  const minDistance = Math.min(...distances)
  const maxPrice = Math.max(...prices, 1)
  const minPriceValue = Math.min(...prices)
  const maxAvailable = Math.max(...available, 1)

  const scored = candidates.map(lot => {
    const distance = typeof lot.distance === 'number' ? lot.distance : maxDistance
    const distanceScore = maxDistance === minDistance ? 1 : 1 - (distance - minDistance) / (maxDistance - minDistance)
    const priceScore = maxPrice === minPriceValue ? 1 : 1 - ((lot.price_per_hour || 0) - minPriceValue) / (maxPrice - minPriceValue)
    const spotScore = (lot.available_spots || 0) / maxAvailable
    const score = distanceScore * 0.42 + priceScore * 0.28 + spotScore * 0.30
    return { lot, score, distanceScore, priceScore, spotScore }
  }).sort((a, b) => b.score - a.score)

  const best = scored[0]
  const reasons = []
  if (best.distanceScore >= 0.75) reasons.push('距离更近')
  if (best.priceScore >= 0.75) reasons.push('价格更优')
  if (best.spotScore >= 0.65) reasons.push('空位更充足')
  if (reasons.length === 0) reasons.push('距离、价格和空位综合更均衡')

  return {
    lot: best.lot,
    score: Math.round(best.score * 100),
    summary: `${reasons.join('、')}，适合当前优先停车选择。`
  }
}

function refreshLocalRecommendation() {
  aiRecommendation.value = buildLocalRecommendation(lots.value)
}

function sortLots(list) {
  const sorted = [...list]
  if (sortBy.value === 'distance') {
    sorted.sort((a, b) => (a.distance ?? 999) - (b.distance ?? 999) || a.price_per_hour - b.price_per_hour)
  } else if (sortBy.value === 'price') {
    sorted.sort((a, b) => a.price_per_hour - b.price_per_hour || (a.distance ?? 999) - (b.distance ?? 999))
  } else if (sortBy.value === 'available') {
    sorted.sort((a, b) => b.available_spots - a.available_spots || (a.distance ?? 999) - (b.distance ?? 999))
  }
  return sorted
}

function normalizeBackendLot(lot) {
  return { ...lot, source: lot.source || 'backend' }
}

function syncSimLotSelection() {
  const availableLots = simLots.value
  if (availableLots.length === 0) {
    simLotId.value = null
    return
  }
  if (!availableLots.some(lot => lot.id === simLotId.value)) {
    simLotId.value = availableLots[0].id
  }
}

function getPoiLngLat(poi) {
  const lng = Number(poi?.location?.lng)
  const lat = Number(poi?.location?.lat)
  if (!Number.isFinite(lng) || !Number.isFinite(lat)) return null
  return { lng, lat }
}

function hashText(text = '') {
  return String(text).split('').reduce((sum, char) => (sum * 31 + char.charCodeAt(0)) >>> 0, 7)
}

function calcClientDistance(lat1, lng1, lat2, lng2) {
  const toRad = value => value * Math.PI / 180
  const earthRadius = 6371
  const dLat = toRad(lat2 - lat1)
  const dLng = toRad(lng2 - lng1)
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2
  return Number((earthRadius * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))).toFixed(2))
}

function ensurePlaceSearch() {
  return new Promise((resolve, reject) => {
    if (!window.AMap) return reject(new Error('AMap is not ready'))
    if (window.AMap.PlaceSearch) return resolve()
    if (typeof window.AMap.plugin !== 'function') return reject(new Error('AMap plugin loader is not ready'))
    window.AMap.plugin('AMap.PlaceSearch', () => resolve())
  })
}

async function searchDestinationByAmap(text) {
  await ensurePlaceSearch()
  return new Promise((resolve, reject) => {
    const placeSearch = new AMap.PlaceSearch({
      city: '全国',
      pageSize: 1,
      pageIndex: 1,
      extensions: 'base'
    })
    placeSearch.search(text, (status, result) => {
      const pois = result?.poiList?.pois || []
      const poi = pois.find(item => getPoiLngLat(item))
      if (status === 'complete' && poi) {
        const location = getPoiLngLat(poi)
        const address = typeof poi.address === 'string' && poi.address ? poi.address : (poi.district || '')
        resolve({
          id: poi.id || `${location.lng},${location.lat}`,
          name: poi.name || text,
          address,
          lng: location.lng,
          lat: location.lat
        })
      } else {
        reject(new Error('destination not found'))
      }
    })
  })
}

function buildAmapLot(poi, target, index) {
  const location = getPoiLngLat(poi)
  if (!location) return null
  const seed = hashText(poi.id || poi.name || `${location.lng},${location.lat}`)
  const available = 8 + (seed % 48)
  const total = available + 36 + (seed % 84)
  const address = typeof poi.address === 'string' && poi.address ? poi.address : (poi.district || '高德地图周边结果')
  const distance = Number.isFinite(Number(poi.distance))
    ? Number((Number(poi.distance) / 1000).toFixed(2))
    : calcClientDistance(target.lat, target.lng, location.lat, location.lng)

  return {
    id: `amap-${poi.id || `${location.lng}-${location.lat}`}-${index}`,
    source: 'amap',
    name: poi.name || '周边停车场',
    address,
    lat: location.lat,
    lng: location.lng,
    distance,
    price_per_hour: [3, 4, 5, 6, 8][seed % 5],
    available_spots: available,
    total_spots: total,
    status: 'active'
  }
}

async function searchParkingAround(target) {
  await ensurePlaceSearch()
  return new Promise((resolve, reject) => {
    const placeSearch = new AMap.PlaceSearch({
      city: '全国',
      pageSize: 25,
      pageIndex: 1,
      extensions: 'base'
    })
    placeSearch.searchNearBy('停车场', [target.lng, target.lat], 2500, (status, result) => {
      if (status !== 'complete') return reject(new Error('parking search failed'))
      const pois = result?.poiList?.pois || []
      const seen = new Set()
      const mapped = pois
        .map((poi, index) => buildAmapLot(poi, target, index))
        .filter(Boolean)
        .filter(lot => {
          const key = `${lot.name}-${lot.lng}-${lot.lat}`
          if (seen.has(key)) return false
          seen.add(key)
          return true
        })
      resolve(mapped)
    })
  })
}

// 获取停车场数据
async function fetchLots(options = {}) {
  const { includeKeyword = false } = options
  loading.value = true
  const params = { page: 1, page_size: 50, sort_by: sortBy.value, lat: currentPosition[1], lng: currentPosition[0] }
  if (includeKeyword && keyword.value) params.keyword = keyword.value
  try {
    const res = await api.get('/lots', { params })
    const data = Array.isArray(res.data) ? res.data : (Array.isArray(res.data?.data) ? res.data.data : [])
    lots.value = sortLots(data.map(normalizeBackendLot))
  } catch {
    lots.value = []
  }
  syncSimLotSelection()
  refreshLocalRecommendation()
  loading.value = false
}

function handleSortChange() {
  lots.value = sortLots(lots.value)
  refreshLocalRecommendation()
  if (destination.value) {
    updateMapMarkers()
  } else {
    fetchLots().then(updateMapMarkers)
  }
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
      buttonOffset: new AMap.Pixel(12, 20),
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

function clearDestinationMarker() {
  if (destinationMarker && map) {
    map.remove(destinationMarker)
  }
  destinationMarker = null
}

function renderDestinationMarker(target) {
  if (!map || !target) return
  clearDestinationMarker()
  const content = '<div style="position:relative;padding:6px 10px;border-radius:999px;background:#172033;color:#fff;font-size:12px;font-weight:800;box-shadow:0 8px 18px rgba(15,23,42,.28);border:2px solid #fff;">目标</div>'
  destinationMarker = new AMap.Marker({
    position: [target.lng, target.lat],
    content,
    anchor: 'bottom-center',
    zIndex: 300
  })
  destinationMarker.on('click', () => {
    ElMessage.info(`目标地：${target.name}`)
  })
  map.add(destinationMarker)
}

// 更新地图标记点
function updateMapMarkers() {
  if (!map) return
  // 清除旧标记
  markers.forEach(m => map.remove(m))
  markers = []

  const sorted = sortLots(lots.value)

  sorted.forEach((lot, index) => {
    if (!lot.lat || !lot.lng) return
    const position = [lot.lng, lot.lat]
    const ratio = lot.total_spots > 0 ? lot.available_spots / lot.total_spots : 0
    const color = lot.source === 'amap' ? '#1677ff' : ratio > 0.3 ? '#52c41a' : ratio > 0.1 ? '#faad14' : '#f5222d'
    const label = lot.source === 'amap' ? 'P' : lot.available_spots
    const content = `<div style="background:${color};color:#fff;width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:bold;box-shadow:0 3px 10px rgba(0,0,0,0.28);border:2px solid #fff;">${label}</div>`

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
  const fitTargets = destinationMarker ? [...markers, destinationMarker] : markers
  if (fitTargets.length > 0) {
    map.setFitView(fitTargets, false, [74, 74, 74, 74])
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

  let top = pixel.y - 185
  let left = pixel.x - 120

  // 边界处理
  if (top < 10) top = 10
  if (left < 10) left = 10
  if (left + 240 > rect.width) left = rect.width - 250
  if (top + 180 > rect.height) top = rect.height - 190

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
}

// 搜索周边
async function searchNearby() {
  const text = keyword.value.trim()
  searching.value = true
  loading.value = true
  infoWindowLot.value = null
  infoWindowStyle.display = 'none'

  try {
    if (!text) {
      destination.value = null
      clearDestinationMarker()
      await fetchLots()
      updateMapMarkers()
      return
    }

    destination.value = null
    clearDestinationMarker()
    const target = await searchDestinationByAmap(text)
    destination.value = target
    currentPosition = [target.lng, target.lat]
    if (map) {
      map.setZoomAndCenter(15, currentPosition)
      renderDestinationMarker(target)
    }

    const amapLots = await searchParkingAround(target)
    if (amapLots.length > 0) {
      lots.value = sortLots(amapLots)
      syncSimLotSelection()
      updateMapMarkers()
      refreshLocalRecommendation()
      ElMessage.success(`已推荐 ${target.name} 周边停车场`)
    } else {
      await fetchLots()
      updateMapMarkers()
      ElMessage.warning('高德暂未返回周边停车场，已展示系统车场')
    }
  } catch (error) {
    console.warn('Destination parking search failed:', error)
    if (text) ElMessage.warning('未找到目的地或高德周边数据，已展示系统车场')
    await fetchLots()
    updateMapMarkers()
  } finally {
    searching.value = false
    loading.value = false
  }
}

// 预约相关
const showReserve = ref(false)
const reserveLot = ref(null)
const reservePlate = ref('')
const reserving = ref(false)

function primaryLotAction(lot) {
  if (lot.source === 'amap') {
    openNavigationToLot(lot)
  } else {
    openReserve(lot)
  }
}

function openNavigationToLot(lot) {
  if (!lot?.lng || !lot?.lat) return ElMessage.warning('该停车场暂无可导航坐标')
  const name = encodeURIComponent(lot.name || '停车场')
  const url = `https://uri.amap.com/navigation?to=${lot.lng},${lot.lat},${name}&mode=car&policy=1&src=SmartParkCloudLink&coordinate=gaode&callnative=0`
  window.open(url, '_blank')
}

async function openReserve(lot) {
  if (lot.source === 'amap') {
    openNavigationToLot(lot)
    return
  }
  reserveLot.value = lot
  // 优先从后端获取个人信息中的车牌号
  try {
    const meRes = await api.get('/auth/me')
    if (meRes.code === 0 && meRes.data && meRes.data.plate_numbers) {
      reservePlate.value = firstPlateNumber(meRes.data.plate_numbers)
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
  if (!simLotId.value) return ElMessage.warning('当前没有可模拟的系统车场')
  try {
    const res = await api.post('/license-plate/events', { lot_id: simLotId.value, plate_number: simPlate.value, event_type: 'entry' })
    if (res.code === 0 || res.data) {
      ElMessage.success(res.msg || '入场成功')
      fetchLots().then(updateMapMarkers)
    } else ElMessage.error(res.msg || '入场失败')
  } catch { ElMessage.error('网络请求失败') }
}

async function simExit() {
  if (!simLotId.value) return ElMessage.warning('当前没有可模拟的系统车场')
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
  height: calc(100vh - 158px);
  min-height: 680px;
  position: relative;
  overflow: hidden;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 12px 32px rgba(15,23,42,.08);
}

.search-bar {
  display: flex;
  gap: 10px;
  padding: 14px 16px 8px;
  background: linear-gradient(180deg, #fff, #f8fbff);
  z-index: 10;
  flex-shrink: 0;
}
.search-bar .el-input { flex: 1; }

.filter-row {
  padding: 0 16px 10px;
  background: #f8fbff;
  z-index: 10;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}
.destination-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  max-width: 58%;
  border: 1px solid #dbeafe;
  border-radius: 999px;
  padding: 5px 10px;
  background: #eff6ff;
  color: #475569;
  font-size: 12px;
  line-height: 1.4;
}
.destination-chip strong {
  color: #1677ff;
  white-space: nowrap;
}
.destination-chip span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.summary-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  padding: 0 16px 8px;
  background: #f8fbff;
}
.summary-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid #e8eef7;
  border-radius: 8px;
  padding: 7px 10px;
  background: #fff;
  box-shadow: 0 4px 14px rgba(15,23,42,.04);
}
.summary-label {
  color: #8492a6;
  font-size: 12px;
  margin: 0;
}
.summary-card strong {
  color: #1f2d3d;
  font-size: 16px;
}

.map-row {
  display: flex;
  flex: 1;
  min-height: 0;
  gap: 12px;
  padding: 0 16px 16px;
  background: #fff;
}

.map-shell {
  flex: 1;
  min-width: 0;
  min-height: 500px;
  height: 100%;
  position: relative;
}

.map-container {
  width: 100%;
  height: 100%;
  min-height: 470px;
  position: relative;
  overflow: hidden;
  border-radius: 12px;
  border: 1px solid #e8eef7;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,.5);
}

.right-panel {
  width: 400px;
  flex-shrink: 0;
  padding: 0;
  background: transparent;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
}

.ai-card {
  flex-shrink: 0;
  padding: 14px;
  border-radius: 12px;
  border: 1px solid #dbeafe;
  background: linear-gradient(135deg, #f8fbff, #ffffff);
  box-shadow: 0 10px 24px rgba(37,99,235,.08);
}
.ai-card-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 12px;
}
.ai-kicker {
  display: block;
  color: #2563eb;
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 2px;
}
.ai-card h4 {
  margin: 0;
  font-size: 16px;
  color: #1f2d3d;
}
.ai-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.ai-lot-name {
  font-size: 15px;
  font-weight: 800;
  color: #172033;
  line-height: 1.35;
}
.ai-reason {
  color: #64748b;
  font-size: 12px;
  line-height: 1.55;
}
.ai-score-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 8px;
  padding: 9px 10px;
  background: #eff6ff;
  color: #475569;
  font-size: 12px;
}
.ai-score-row strong {
  color: #1677ff;
  font-size: 20px;
}
.ai-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
}
.ai-metrics span {
  border-radius: 8px;
  padding: 7px 6px;
  background: #f8fafc;
  color: #475569;
  text-align: center;
  font-size: 12px;
}
.ai-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.ai-actions .el-button {
  width: 100%;
  margin: 0;
}

.sim-fab {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 800;
  border: none;
  border-radius: 8px;
  padding: 11px 16px;
  background: #1677ff;
  color: #fff;
  font-weight: 700;
  box-shadow: 0 10px 24px rgba(22,119,255,.24);
  cursor: pointer;
}
.sim-float {
  position: absolute;
  top: 64px;
  right: 16px;
  z-index: 900;
  width: 380px;
  padding: 16px;
  border-radius: 12px;
  background: rgba(255,255,255,.98);
  border: 1px solid #e8eef7;
  box-shadow: 0 18px 42px rgba(15,23,42,.18);
}
.sim-float-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 14px;
}
.sim-float h4 { margin: 0 0 4px; color: #1f2d3d; font-size: 16px; }
.sim-float p { color: #8a97a8; font-size: 12px; line-height: 1.5; }
.float-close {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 8px;
  background: #f1f5f9;
  color: #64748b;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
}
.sim-select, .sim-input { width: 100%; margin-bottom: 12px; }
.sim-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.sim-actions .el-button { width: 100%; margin: 0; }
.float-enter-active, .float-leave-active { transition: opacity .18s ease, transform .18s ease; }
.float-enter-from, .float-leave-to { opacity: 0; transform: translateY(-8px); }

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
.map-info-window .iw-note {
  margin: 0 0 8px;
  padding: 6px 8px;
  border-radius: 6px;
  background: #eff6ff;
  color: #2563eb;
  font-size: 12px;
  line-height: 1.45;
}
.map-info-window .iw-actions {
  display: flex;
  gap: 8px;
}

/* 地图版权与 logo 保持在地图底部，不遮挡右侧表单 */
.map-container :deep(.amap-logo) {
  left: 12px !important;
  bottom: 10px !important;
  top: auto !important;
}
.map-container :deep(.amap-copyright) {
  left: 82px !important;
  bottom: 8px !important;
  top: auto !important;
}

/* 右侧车场列表 */
.bottom-panel {
  position: relative;
  z-index: 100;
  background: rgba(255,255,255,.96);
  backdrop-filter: blur(12px);
  border: 1px solid #e8eef7;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(15,23,42,.06);
  transition: max-height 0.3s ease;
  max-height: 44px;
  overflow: hidden;
  flex: 0 0 46px;
  min-height: 0;
}
.bottom-panel.expanded {
  flex: 1;
  max-height: none;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.panel-handle {
  padding: 13px 16px;
  text-align: center;
  cursor: pointer;
  font-size: 13px;
  color: #2563eb;
  font-weight: 700;
  border-bottom: 1px solid #f0f0f0;
  user-select: none;
}
.panel-list {
  padding: 0;
  overflow-y: auto;
  min-height: 0;
}

.lot-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
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
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.lot-addr {
  font-size: 12px;
  color: #909399;
  margin: 0 0 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.lot-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  font-size: 12px;
  color: #606266;
}
.tag-price { color: #f5222d; font-weight: 600; }
.tag-dist { color: #409EFF; }
.tag-spots { color: #909399; }
.tag-source {
  border-radius: 999px;
  padding: 1px 6px;
  background: #eff6ff;
  color: #1677ff;
  font-weight: 700;
}

.lot-item-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  flex-shrink: 0;
  margin-left: 12px;
}
.reserve-btn { font-size: 12px; }

@media (max-width: 900px) {
  .home-page { height: auto; min-height: calc(100vh - 140px); overflow: visible; }
  .summary-row { grid-template-columns: repeat(2, 1fr); }
  .map-row { flex-direction: column; }
  .map-shell { min-height: 420px; }
  .right-panel { width: 100%; }
  .bottom-panel { margin: 0; max-height: 360px; }
  .bottom-panel.expanded { max-height: 360px; }
  .sim-float { width: min(380px, calc(100% - 32px)); }
}

@media (max-width: 560px) {
  .search-bar { flex-direction: column; }
  .destination-chip { max-width: 100%; width: 100%; }
  .summary-row { grid-template-columns: 1fr 1fr; }
  .summary-card { display: block; padding: 8px 10px; }
  .summary-card strong { display: block; margin-top: 2px; font-size: 16px; }
  .sim-fab { top: 12px; right: 12px; padding: 9px 12px; }
  .sim-float { top: 56px; right: 12px; width: calc(100% - 24px); }
  .sim-actions { grid-template-columns: 1fr; }
}

</style>
