import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    const adminKey = localStorage.getItem('admin_key')
    if (adminKey) {
      config.headers['X-Admin-Key'] = adminKey
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response) {
      // 401 未授权
      if (error.response.status === 401) {
        localStorage.removeItem('token')
        window.location.href = '/login'
        return Promise.reject(error)
      }
      // 返回错误信息
      const message = error.response.data.detail || '请求失败'
      ElMessage.error(message)
    } else {
      ElMessage.error('网络连接失败')
    }
    return Promise.reject(error)
  }
)

export default request
