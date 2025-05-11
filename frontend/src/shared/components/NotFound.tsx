import { Link } from 'react-router-dom';

const NotFound = () => {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center">
      <h1 className="text-4xl font-bold text-gray-800 mb-4">404</h1>
      <p className="text-xl text-gray-600 mb-8">页面未找到</p>
      <p className="text-gray-500 mb-8">您访问的页面不存在或已被移除。</p>
      <Link to="/" className="btn-primary">
        返回首页
      </Link>
    </div>
  );
};

export default NotFound;
