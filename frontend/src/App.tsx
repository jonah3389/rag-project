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

  // 从本地存储中恢复用户信息
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (error) {
        console.error('Failed to parse stored user:', error);
        localStorage.removeItem('user');
      }
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, setUser, isAuthenticated: !!user }}>
      <Layout>
        <Outlet />
      </Layout>
    </AuthContext.Provider>
  );
}

export default App;
