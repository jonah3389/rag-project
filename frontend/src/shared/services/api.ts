import axios from 'axios';
// 在 axios 1.9.0 中，类型可能已经被移动或重命名
// 我们可以直接使用 axios 实例而不需要显式导入类型

// 创建 axios 实例
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 从本地存储获取令牌
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // 处理 401 未授权错误
      if (error.response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }

      // 处理其他错误
      const errorMessage = error.response.data.detail || '请求失败';
      console.error('API Error:', errorMessage);
    } else if (error.request) {
      console.error('No response received:', error.request);
    } else {
      console.error('Request error:', error.message);
    }

    return Promise.reject(error);
  }
);

export default api;
