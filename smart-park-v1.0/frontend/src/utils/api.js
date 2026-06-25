import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({ baseURL: '/api', timeout: 10000 })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.params = { ...config.params, token }
  return config
})

api.interceptors.response.use(
  res => res.data,
  err => { ElMessage.error('网络请求失败'); return Promise.reject(err) }
)

export default api
