import api from './api';

export interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  is_superuser: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// 登录
export const login = async (username: string, password: string): Promise<LoginResponse> => {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);

  const response = await api.post<LoginResponse>('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });

  // 保存令牌和用户信息
  localStorage.setItem('token', response.data.access_token);
  localStorage.setItem('user', JSON.stringify(response.data.user));

  return response.data;
};

// 注册
export const register = async (
  email: string,
  username: string,
  password: string
): Promise<User> => {
  const response = await api.post<User>('/auth/register', {
    email,
    username,
    password,
  });
  return response.data;
};

// 登出
export const logout = (): void => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.location.href = '/login';
};

// 获取当前用户
export const getCurrentUser = (): User | null => {
  const userStr = localStorage.getItem('user');
  if (!userStr) return null;
  try {
    return JSON.parse(userStr) as User;
  } catch (e) {
    return null;
  }
};

// 检查是否已登录
export const isAuthenticated = (): boolean => {
  return !!localStorage.getItem('token');
};

// 自动登录（使用默认管理员账户）
export const autoLogin = async (): Promise<LoginResponse> => {
  try {
    return await login('admin', 'admin123');
  } catch (error) {
    console.error('自动登录失败:', error);
    throw error;
  }
};
