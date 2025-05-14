import { createBrowserRouter, Navigate } from 'react-router-dom';
import App from './App';
import Home from './modules/home/pages/Home';
import Login from './modules/auth/pages/Login';
import Register from './modules/auth/pages/Register';
import AuthTest from './modules/auth/pages/AuthTest';
import Dashboard from './modules/dashboard/pages/Dashboard';
// 暂时注释掉缺失的组件导入，等待后续实现
// import ChatPage from './modules/chat/pages/ChatPage';
import KnowledgeBasePage from './modules/knowledge/pages/KnowledgeBasePage';
// import DocumentPage from './modules/document/pages/DocumentPage';
// import LLMConfigPage from './modules/llm/pages/LLMConfigPage';
import NotFound from './shared/components/NotFound';
import ProtectedRoute from './shared/components/ProtectedRoute';

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true,
        element: <Home />,
      },
      {
        path: 'login',
        element: <Login />,
      },
      {
        path: 'register',
        element: <Register />,
      },
      {
        path: 'auth-test',
        element: <AuthTest />,
      },
      {
        path: 'dashboard',
        element: (
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        ),
      },
      // 暂时注释掉缺失组件的路由，等待后续实现
      // {
      //   path: 'chat',
      //   element: (
      //     <ProtectedRoute>
      //       <ChatPage />
      //     </ProtectedRoute>
      //   ),
      // },
      {
        path: 'knowledge/*',
        element: (
          <ProtectedRoute>
            <KnowledgeBasePage />
          </ProtectedRoute>
        ),
      },
      // {
      //   path: 'document',
      //   element: (
      //     <ProtectedRoute>
      //       <DocumentPage />
      //     </ProtectedRoute>
      //   ),
      // },
      // {
      //   path: 'llm-config',
      //   element: (
      //     <ProtectedRoute>
      //       <LLMConfigPage />
      //     </ProtectedRoute>
      //   ),
      // },
      {
        path: '*',
        element: <NotFound />,
      },
    ],
  },
]);

export default router;
