import axios from 'axios';
// 在 axios 1.9.0 中，类型可能已经被移动或重命名
// 我们可以直接使用 axios 实例而不需要显式导入类型

// 创建 axios 实例
const api = axios.create({
  // 使用相对路径，通过 Vite 代理转发到后端
  baseURL: '/api/v1',
  timeout: 120000, // 增加超时时间到 120 秒 (2分钟)
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // 允许跨域请求携带 cookies
});

// 添加一个标志，防止多次跳转登录页面
let isRedirecting = false;

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
        // 防止重复跳转到登录页面
        if (!isRedirecting) {
          isRedirecting = true;
          console.log('收到401未授权响应，正在清除认证状态');

          // 清除认证状态
          localStorage.removeItem('token');
          localStorage.removeItem('user');

          // 如果不是登录页面，则重定向到登录页面
          const currentPath = window.location.pathname;
          if (currentPath !== '/login' && currentPath !== '/register') {
            console.log('重定向到登录页面');
            // 使用会话存储保存当前路径，以便登录后返回
            sessionStorage.setItem('redirectPath', currentPath);
            window.location.href = '/login';
          } else {
            // 重置重定向标志
            setTimeout(() => {
              isRedirecting = false;
            }, 1000);
          }
        }
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
