import { ReactNode, useContext } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { AuthContext } from '../../App';

interface LayoutProps {
  children: ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const { isAuthenticated, user, setUser } = useContext(AuthContext);
  const location = useLocation();
  const navigate = useNavigate();

  // 检查当前路径是否为登录或注册页面
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register';

  // 处理登出
  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 导航栏 */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <Link to="/" className="text-xl font-bold text-blue-600">
                  智能体综合应用平台
                </Link>
              </div>
              {isAuthenticated && (
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                  <Link
                    to="/dashboard"
                    className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${location.pathname === '/dashboard'
                        ? 'border-blue-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                      }`}
                  >
                    仪表盘
                  </Link>
                  <Link
                    to="/chat"
                    className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${location.pathname === '/chat'
                        ? 'border-blue-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                      }`}
                  >
                    智能客服
                  </Link>
                  <Link
                    to="/knowledge"
                    className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${location.pathname.startsWith('/knowledge')
                        ? 'border-blue-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                      }`}
                  >
                    知识库
                  </Link>
                  <Link
                    to="/document"
                    className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${location.pathname === '/document'
                        ? 'border-blue-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                      }`}
                  >
                    文档处理
                  </Link>
                  <Link
                    to="/llm-config"
                    className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${location.pathname === '/llm-config'
                        ? 'border-blue-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                      }`}
                  >
                    LLM 配置
                  </Link>
                </div>
              )}
            </div>
            <div className="flex items-center">
              {isAuthenticated ? (
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-700">欢迎，{user?.username}</span>
                  <button
                    onClick={handleLogout}
                    className="text-sm text-gray-700 hover:text-blue-600"
                  >
                    登出
                  </button>
                </div>
              ) : (
                !isAuthPage && (
                  <div className="flex items-center space-x-4">
                    <Link to="/login" className="text-sm text-gray-700 hover:text-blue-600">
                      登录
                    </Link>
                    <Link
                      to="/register"
                      className="text-sm bg-blue-600 text-white px-3 py-1 rounded-md hover:bg-blue-700"
                    >
                      注册
                    </Link>
                  </div>
                )
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* 主要内容 */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">{children}</div>
      </main>

      {/* 页脚 */}
      <footer className="bg-white border-t border-gray-200 py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            &copy; {new Date().getFullYear()} 智能体综合应用平台. 保留所有权利.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
