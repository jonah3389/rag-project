import api from '../../../shared/services/api';
import { User, UserLogin, UserRegister, Token } from '../types/user';

/**
 * 用户登录
 * @param credentials 登录凭据
 * @returns 用户信息和令牌
 */
export const login = async (credentials: UserLogin): Promise<{ user: User; token: Token }> => {
  // 使用表单数据格式发送请求（OAuth2 要求）
  const formData = new FormData();
  formData.append('username', credentials.username);
  formData.append('password', credentials.password);
  
  const tokenResponse = await api.post<Token>('/auth/login', formData);
  const token = tokenResponse.data;
  
  // 设置令牌后获取用户信息
  api.defaults.headers.common['Authorization'] = `Bearer ${token.access_token}`;
  const userResponse = await api.get<User>('/auth/me');
  
  return {
    user: userResponse.data,
    token,
  };
};

/**
 * 用户注册
 * @param userData 用户注册数据
 * @returns 注册的用户信息
 */
export const register = async (userData: UserRegister): Promise<User> => {
  const response = await api.post<User>('/auth/register', userData);
  return response.data;
};

/**
 * 获取当前用户信息
 * @returns 用户信息
 */
export const getCurrentUser = async (): Promise<User> => {
  const response = await api.get<User>('/auth/me');
  return response.data;
};

/**
 * 更新用户信息
 * @param userData 用户更新数据
 * @returns 更新后的用户信息
 */
export const updateUser = async (userData: Partial<User>): Promise<User> => {
  const response = await api.put<User>('/auth/me', userData);
  return response.data;
};
