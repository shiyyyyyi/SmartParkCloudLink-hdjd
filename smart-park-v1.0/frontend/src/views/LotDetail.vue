<template>
  <div class="detail-page" v-loading="loading">
    <el-page-header @back="$router.back()" :title="lot?.name || '车场详情'" />

    <el-card v-if="lot" class="info-card">
      <h2>{{ lot.name }}</h2>
      <p class="addr"><el-icon><Location /></el-icon> {{ lot.address }}</p>
      <el-descriptions :column="2" border size="small" class="mt16">
        <el-descriptions-item label="总车位">{{ lot.total_spots }}</el-descriptions-item>
        <el-descriptions-item label="空闲车位">
          <el-tag :type="lot.available_spots > 10 ? 'success' : lot.available_spots > 0 ? 'warning' : 'danger'">
            {{ lot.available_spots }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="价格">¥{{ lot.price_per_hour }}/小时</el-descriptions-item>
        <el-descriptions-item label="状态">{{ lot.status === 'active' ? '运营中' : '维护中' }}</el-descriptions-item>
      </el-descriptions>

      <div class="action-row">
        <el-button type="primary" size="large" @click="showReserve = true" :disabled="lot.available_spots <= 0" style="flex:1">
          {{ lot.available_spots > 0 ? '预约车位 (锁定15分钟)' : '车位已满' }}
        </el-button>
        <el-button size="large" @click="openNavigation" style="flex:1">
          <el-icon><Position /></el-icon> 导航到这里
        </el-button>
      </div>
    </el-card>

    <!-- 车位状态可视化 -->
    <el-card class="mt16">
      <template #header>
        <div class="spot-header">
          <span>车位状态</span>
          <div class="spot-legend">
            <span class="legend-item"><span class="dot free"></span>空闲</span>
            <span class="legend-item"><span class="dot reserved"></span>已预约</span>
            <span class="legend-item"><span class="dot occupied"></span>占用</span>
          </div>
        </div>
      </template>
      <div class="spot-grid-visual">
        <div v-for="s in spots" :key="s.id" class="spot-block" :class="'spot-' + s.status">
          <el-icon v-if="s.status === 'free'" color="#67C23A"><CircleCheck /></el-icon>
          <el-icon v-else-if="s.status === 'reserved'" color="#E6A23C"><Clock /></el-icon>
          <el-icon v-else color="#909399"><Remove /></el-icon>
          <span>{{ s.spot_number }}</span>
        </div>
      </div>
      <el-empty v-if="spots.length === 0" description="暂无车位数据" />
    </el-card>

    <!-- 预约弹窗 -->
    <el-dialog v-model="showReserve" title="预约车位" width="90%">
      <el-form label-width="70px">
        <el-form-item label="停车场">{{ lot?.name }}</el-form-item>
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
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../utils/api'
import { firstPlateNumber } from '../utils/plates'
import { Location, Position, CircleCheck, Clock, Remove } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const lot = ref(null)
const spots = ref([])
const loading = ref(false)
const showReserve = ref(false)
const reservePlate = ref('')
const reserving = ref(false)

async function fetchDetail() {
  loading.value = true
  const id = route.params.id
  const [lotRes, spotRes] = await Promise.all([api.get(`/lots/${id}`), api.get(`/lots/${id}/spots`)])
  lot.value = lotRes.data
  spots.value = spotRes.data || []
  // 默认车牌号（从后端获取个人信息中的车牌号）
  try {
    const meRes = await api.get('/auth/me')
    if (meRes.code === 0 && meRes.data && meRes.data.plate_numbers) {
      reservePlate.value = firstPlateNumber(meRes.data.plate_numbers)
    }
  } catch {}
  loading.value = false
}

async function doReserve() {
  if (!reservePlate.value) return ElMessage.warning('请输入车牌号')
  reserving.value = true
  const res = await api.post('/reservations', { lot_id: lot.value.id, plate_number: reservePlate.value })
  reserving.value = false
  if (res.code === 0) {
    ElMessage.success('预约成功！请15分钟内到场确认')
    showReserve.value = false
    fetchDetail()
  } else {
    ElMessage.error(res.msg)
  }
}

function openNavigation() {
  if (lot.value) {
    window.open(`https://uri.amap.com/marker?position=${lot.value.lng},${lot.value.lat}&name=${encodeURIComponent(lot.value.name)}`, '_blank')
  }
}

onMounted(fetchDetail)
</script>

<style scoped>
.detail-page { padding-bottom: 20px; }
.info-card { margin-top: 16px; }
.addr { font-size: 13px; color: #909399; margin-top: 8px; display: flex; align-items: center; gap: 4px; }
.mt16 { margin-top: 16px; }
.action-row { display: flex; gap: 10px; margin-top: 16px; }
.spot-header { display: flex; justify-content: space-between; align-items: center; }
.spot-legend { display: flex; gap: 12px; font-size: 12px; }
.legend-item { display: flex; align-items: center; gap: 4px; }
.dot { width: 10px; height: 10px; border-radius: 2px; display: inline-block; }
.dot.free { background: #67C23A; }
.dot.reserved { background: #E6A23C; }
.dot.occupied { background: #909399; }
.spot-grid-visual { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; }
.spot-block { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 10px 4px; border-radius: 8px; font-size: 11px; gap: 4px; }
.spot-free { background: #f0f9eb; border: 1px solid #c2e7b0; }
.spot-reserved { background: #fdf6ec; border: 1px solid #f5dab1; }
.spot-occupied { background: #f4f4f5; border: 1px solid #d4d4d5; }
</style>
