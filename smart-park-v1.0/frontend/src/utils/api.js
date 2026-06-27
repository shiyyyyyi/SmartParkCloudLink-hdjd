import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({ baseURL: '/api', timeout: 10000 })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
    // 兼容旧版：同时保留 query 参数传递（过渡期）
    config.params = { ...config.params, token }
  }
  return config
})

api.interceptors.response.use(
  res => res.data,
  err => { ElMessage.error('网络请求失败'); return Promise.reject(err) }
)

export default api
