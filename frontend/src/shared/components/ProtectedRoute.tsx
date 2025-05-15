import { useContext } from 'react';
import { useLocation, Navigate } from 'react-router-dom';
import { AuthContext } from '../../App';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { isAuthenticated } = useContext(AuthContext);
  const location = useLocation();

  // 如果未认证，重定向到登录页面
  if (!isAuthenticated) {
    console.log('未认证，重定向到登录页面，当前路径:', location.pathname);

    // 将当前路径保存到会话存储，以便登录后可以重定向回来
    if (location.pathname !== '/login') {
      sessionStorage.setItem('redirectPath', location.pathname);
    }

    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
