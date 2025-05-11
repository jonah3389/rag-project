/**
 * API 工具函数
 */

import { AxiosError } from 'axios';

/**
 * 处理 API 错误
 * @param error Axios 错误对象
 * @returns 格式化的错误消息
 */
export const handleApiError = (error: unknown): string => {
  if (error instanceof AxiosError) {
    // 处理 Axios 错误
    if (error.response) {
      // 服务器返回错误
      const { status, data } = error.response;
      
      if (status === 401) {
        return '未授权，请重新登录';
      }
      
      if (status === 403) {
        return '没有权限执行此操作';
      }
      
      if (status === 404) {
        return '请求的资源不存在';
      }
      
      if (status === 422) {
        // 处理验证错误
        if (data.detail && Array.isArray(data.detail)) {
          return data.detail.map((err: any) => `${err.loc.join('.')}：${err.msg}`).join('\n');
        }
      }
      
      // 其他错误
      return data.detail || `请求失败 (${status})`;
    } else if (error.request) {
      // 请求已发送但未收到响应
      return '服务器无响应，请稍后再试';
    } else {
      // 请求配置错误
      return `请求错误：${error.message}`;
    }
  }
  
  // 其他错误
  return error instanceof Error ? error.message : '发生未知错误';
};

/**
 * 格式化日期
 * @param dateString 日期字符串
 * @returns 格式化后的日期字符串
 */
export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * 截断文本
 * @param text 文本
 * @param maxLength 最大长度
 * @returns 截断后的文本
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) {
    return text;
  }
  return `${text.substring(0, maxLength)}...`;
};
