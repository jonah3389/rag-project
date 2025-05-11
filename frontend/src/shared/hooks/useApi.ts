import { useState, useCallback } from 'react';
import { AxiosError } from 'axios';
import { handleApiError } from '../utils/api';

interface UseApiOptions<T> {
  onSuccess?: (data: T) => void;
  onError?: (error: string) => void;
}

/**
 * API 请求 Hook
 * @param apiFunction API 函数
 * @param options 选项
 * @returns API 状态和处理函数
 */
const useApi = <T, P extends any[]>(
  apiFunction: (...args: P) => Promise<T>,
  options?: UseApiOptions<T>
) => {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const execute = useCallback(
    async (...args: P) => {
      setLoading(true);
      setError(null);
      
      try {
        const result = await apiFunction(...args);
        setData(result);
        options?.onSuccess?.(result);
        return result;
      } catch (err) {
        const errorMessage = handleApiError(err);
        setError(errorMessage);
        options?.onError?.(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [apiFunction, options]
  );

  return {
    data,
    error,
    loading,
    execute,
  };
};

export default useApi;
