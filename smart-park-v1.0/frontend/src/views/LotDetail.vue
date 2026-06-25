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

      <el-button type="primary" size="large" @click="reserve" :disabled="lot.available_spots <= 0" class="mt16" style="width:100%">
        {{ lot.available_spots > 0 ? '预约车位 (锁定15分钟)' : '车位已满' }}
      </el-button>
    </el-card>

    <!-- 车位列表 -->
    <el-card class="mt16">
      <template #header>车位状态</template>
      <div class="spot-grid">
        <el-tag v-for="s in spots" :key="s.id" :type="s.status === 'free' ? 'success' : s.status === 'reserved' ? 'warning' : 'info'"
          size="small" class="spot-tag">
          {{ s.spot_number }}
        </el-tag>
      </div>
      <el-empty v-if="spots.length === 0" description="暂无车位数据" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../utils/api'
import { Location } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const lot = ref(null)
const spots = ref([])
const loading = ref(false)
const plateNumbers = JSON.parse(localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')).plate_numbers || '["浙AT9999"]' : '["浙AT9999"]')

async function fetchDetail() {
  loading.value = true
  const id = route.params.id
  const [lotRes, spotRes] = await Promise.all([api.get(`/lots/${id}`), api.get(`/lots/${id}/spots`)])
  lot.value = lotRes.data
  spots.value = spotRes.data || []
  loading.value = false
}

async function reserve() {
  const res = await api.post('/reservations', { lot_id: lot.value.id, plate_number: JSON.parse(plateNumbers)[0] || '浙AT9999' })
  if (res.code === 0) {
    ElMessage.success('预约成功！请15分钟内到场确认')
    fetchDetail()
  } else {
    ElMessage.error(res.msg)
  }
}

onMounted(fetchDetail)
</script>

<style scoped>
.detail-page { padding-bottom: 20px; }
.info-card { margin-top: 16px; }
.addr { font-size: 13px; color: #909399; margin-top: 8px; }
.mt16 { margin-top: 16px; }
.spot-grid { display: flex; flex-wrap: wrap; gap: 6px; }
.spot-tag { margin: 2px; cursor: default; }
</style>
