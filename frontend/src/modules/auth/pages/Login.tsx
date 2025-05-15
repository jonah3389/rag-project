import { useState, useContext, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../../../App';
import { login } from '../services/authService';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const { setUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();

  // 获取重定向路径
  const from = location.state?.from?.pathname || sessionStorage.getItem('redirectPath') || '/dashboard';

  // 检查是否有来自注册页面的消息
  useEffect(() => {
    const message = location.state?.message;
    if (message) {
      setSuccess(message);
      // 清除 location state 中的消息，防止刷新后再次显示
      window.history.replaceState({}, document.title);
    }

    // 获取完成后清除会话存储中的重定向路径
    if (sessionStorage.getItem('redirectPath')) {
      console.log('从会话存储获取重定向路径:', sessionStorage.getItem('redirectPath'));
      sessionStorage.removeItem('redirectPath');
    }
  }, [location.state]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!username || !password) {
      setError('请输入用户名和密码');
      setSuccess('');
      return;
    }

    try {
      setLoading(true);
      setError('');
      setSuccess('');

      const { user, token } = await login({ username, password });

      // 保存令牌和用户信息
      localStorage.setItem('token', token.access_token);
      localStorage.setItem('user', JSON.stringify(user));

      // 更新认证状态
      setUser(user);

      // 显示成功消息
      setSuccess('登录成功，正在跳转...');

      // 延迟跳转，让用户看到成功消息
      setTimeout(() => {
        // 重定向到之前的页面或仪表盘
        navigate(from, { replace: true });
      }, 1000);
    } catch (err: any) {
      setError(err.response?.data?.detail || '登录失败，请检查您的凭据');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">登录您的账户</h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            或{' '}
            <Link to="/register" className="font-medium text-blue-600 hover:text-blue-500">
              注册新账户
            </Link>
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}
          {success && (
            <div className="bg-green-50 border-l-4 border-green-500 p-4">
              <p className="text-sm text-green-700">{success}</p>
            </div>
          )}

          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="username" className="sr-only">
                用户名
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="用户名"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                密码
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="密码"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-blue-400"
            >
              {loading ? '登录中...' : '登录'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;
