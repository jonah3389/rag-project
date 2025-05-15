import { Outlet } from 'react-router-dom';
import { useState, useEffect, createContext } from 'react';
import Layout from './shared/components/Layout';

// 直接在 App.tsx 中定义 User 类型
interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

// 创建认证上下文
interface AuthContextType {
  user: User | null;
  setUser: (user: User | null) => void;
  isAuthenticated: boolean;
}

export const AuthContext = createContext<AuthContextType>({
  user: null,
  setUser: () => { },
  isAuthenticated: false,
});

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // 从本地存储中恢复用户信息
  useEffect(() => {
    const loadUserFromStorage = () => {
      try {
        const token = localStorage.getItem('token');
        const storedUser = localStorage.getItem('user');

        if (token && storedUser) {
          const parsedUser = JSON.parse(storedUser);
          setUser(parsedUser);
          console.log('用户认证状态已从本地存储恢复', parsedUser.username);
        } else {
          console.log('本地存储中没有找到用户信息');
          setUser(null);
        }
      } catch (error) {
        console.error('解析存储的用户信息失败:', error);
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    loadUserFromStorage();
  }, []);

  if (isLoading) {
    return <div className="h-screen flex items-center justify-center">加载中...</div>;
  }

  return (
    <AuthContext.Provider value={{ user, setUser, isAuthenticated: !!user }}>
      <Layout>
        <Outlet />
      </Layout>
    </AuthContext.Provider>
  );
}

export default App;
