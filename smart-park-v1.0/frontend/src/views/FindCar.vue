<template>
  <div class="page">
    <h3>反向寻车</h3>
    <el-card>
      <el-input v-model="plateNumber" placeholder="请输入您的车牌号" size="large" clearable @keyup.enter="findCar">
        <template #prefix><el-icon><Search /></el-icon></template>
        <template #append>
          <el-button type="primary" @click="findCar" :loading="loading">查找</el-button>
        </template>
      </el-input>
    </el-card>

    <el-card v-if="result" class="mt16 result-card">
      <div class="result-header">
        <el-icon :size="32" color="#409EFF"><MapLocation /></el-icon>
        <div>
          <h3>车辆已定位</h3>
          <p class="plate">{{ result.plate_number }}</p>
        </div>
      </div>
      <el-divider />
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
          <span class="label">入场时间</span>
          <span class="value">{{ result.entry_time }}</span>
        </div>
        <div class="info-item">
          <span class="label">已停时长</span>
          <span class="value">{{ durationText }}</span>
        </div>
      </div>
      <div class="location-hint">
        <el-icon><Location /></el-icon>
        <span>{{ result.lot_address }}</span>
      </div>
    </el-card>

    <el-empty v-if="!loading && !result && searched" description="未找到停车记录，请确认车牌号" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '../utils/api'
import { Search, MapLocation, Location } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const plateNumber = ref('')
const loading = ref(false)
const searched = ref(false)
const result = ref(null)

const durationText = computed(() => {
  if (!result.value?.entry_time) return ''
  const entry = new Date(result.value.entry_time)
  const now = new Date()
  const diff = Math.floor((now - entry) / 1000 / 60)
  if (diff < 60) return `${diff} 分钟`
  const hours = Math.floor(diff / 60)
  const mins = diff % 60
  return `${hours} 小时 ${mins} 分钟`
})

async function findCar() {
  if (!plateNumber.value) return ElMessage.warning('请输入车牌号')
  loading.value = true
  searched.value = true
  result.value = null
  const res = await api.get('/find-car', { params: { plate_number: plateNumber.value } })
  loading.value = false
  if (res.code === 0 && res.data) {
    result.value = res.data
  } else {
    ElMessage.warning(res.msg || '未找到该车辆的停车记录')
  }
}
</script>

<style scoped>
.page { padding-bottom: 20px; }
h3 { margin-bottom: 16px; color: #303133; }
.mt16 { margin-top: 16px; }
.result-card .result-header { display: flex; align-items: center; gap: 16px; }
.result-card .plate { font-size: 20px; font-weight: 700; color: #409EFF; letter-spacing: 2px; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 12px 0; }
.info-item .label { display: block; font-size: 12px; color: #909399; margin-bottom: 4px; }
.info-item .value { font-size: 15px; color: #303133; font-weight: 500; }
.info-item .value.highlight { color: #67C23A; font-size: 18px; font-weight: 700; }
.location-hint { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #909399; margin-top: 12px; }
</style>
