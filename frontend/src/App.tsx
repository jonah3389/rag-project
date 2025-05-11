import { Outlet } from 'react-router-dom';
import { useState, createContext } from 'react';
import Layout from './shared/components/Layout';
import { User } from './modules/auth/types/user';

// 创建认证上下文
interface AuthContextType {
  user: User | null;
  setUser: (user: User | null) => void;
  isAuthenticated: boolean;
}

export const AuthContext = createContext<AuthContextType>({
  user: null,
  setUser: () => {},
  isAuthenticated: false,
});

function App() {
  const [user, setUser] = useState<User | null>(null);

  // 从本地存储中恢复用户信息
  useState(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (error) {
        console.error('Failed to parse stored user:', error);
        localStorage.removeItem('user');
      }
    }
  });

  return (
    <AuthContext.Provider value={{ user, setUser, isAuthenticated: !!user }}>
      <Layout>
        <Outlet />
      </Layout>
    </AuthContext.Provider>
  );
}

export default App;
