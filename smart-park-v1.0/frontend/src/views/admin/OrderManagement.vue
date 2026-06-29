<template>
  <div class="admin-page">
    <el-page-header @back="$router.push('/admin')" title="订单管理" />
    <!-- 搜索栏 -->
    <el-card class="mt16 search-card">
      <el-form :inline="true" size="default">
        <el-form-item label="车牌号">
          <el-input v-model="keyword" placeholder="输入车牌号搜索" clearable @keyup.enter="search" style="width:200px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search" :icon="Search">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    <el-tabs v-model="tab" @tab-change="fetch" class="mt16">
      <el-tab-pane label="全部" name="all" />
      <el-tab-pane label="停车中" name="parking" />
      <el-tab-pane label="待支付" name="pending_pay" />
      <el-tab-pane label="已完成" name="paid" />
    </el-tabs>
    <div v-loading="loading">
      <el-card v-for="o in orders" :key="o.id" class="card">
        <div class="card-header">
          <span class="lot-name">{{ o.lot_name }}</span>
          <el-tag :type="statusType(o.status)" size="small">{{ statusText(o.status) }}</el-tag>
        </div>
        <p class="info">车牌：<span class="plate-highlight">{{ o.plate_number }}</span></p>
        <p class="info">入场：{{ formatTime(o.entry_time) }}</p>
        <p class="info">金额：¥{{ o.amount || '—' }}</p>
      </el-card>
      <el-empty v-if="!loading && orders.length === 0" description="暂无订单" />
      <el-pagination v-if="total > 20" v-model:current-page="page" :page-size="20" :total="total" layout="prev,next" @current-change="fetch" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../utils/api'
import { Search } from '@element-plus/icons-vue'

const orders = ref([])
const loading = ref(false)
const tab = ref('all')
const page = ref(1)
const total = ref(0)
const keyword = ref('')

function statusType(s) { return { parking: '', pending_pay: 'warning', paid: 'success', exception: 'danger' }[s] || 'info' }
function statusText(s) { return { parking: '停车中', pending_pay: '待支付', paid: '已完成', exception: '异常' }[s] || s }
function formatTime(t) { return t ? new Date(t).toLocaleString('zh-CN') : '-' }

async function fetch() {
  loading.value = true
  const params = { page: page.value, page_size: 20 }
  if (tab.value !== 'all') params.status = tab.value
  if (keyword.value) params.keyword = keyword.value
  const res = await api.get('/admin/orders', { params })
  orders.value = res.data || []
  total.value = res.total || 0
  loading.value = false
}

function search() {
  page.value = 1
  fetch()
}

function resetSearch() {
  keyword.value = ''
  page.value = 1
  fetch()
}

onMounted(fetch)
</script>

<style scoped>
.admin-page { padding-bottom: 20px; }
.mt16 { margin-top: 16px; }
.search-card { margin-bottom: 4px; }
.card { margin-bottom: 12px; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.lot-name { font-weight: 600; font-size: 15px; }
.info { font-size: 12px; color: #606266; margin-bottom: 4px; }
.plate-highlight { color: #409EFF; font-weight: 600; }
</style>
