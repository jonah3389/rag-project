import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import * as knowledgeService from '../services/knowledgeService';
import * as authService from '../../../shared/services/authService';
import type { KnowledgeBase } from '../services/knowledgeService';

const KnowledgeBaseList: React.FC = () => {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchKnowledgeBases = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await knowledgeService.getKnowledgeBases();
      setKnowledgeBases(data);
    } catch (err: any) {
      console.error('Failed to fetch knowledge bases:', err);

      // 检查是否是认证错误
      if (err.response && (err.response.status === 401 || err.response.status === 403)) {
        setError('登录已过期，正在尝试自动登录...');
        try {
          // 尝试自动登录
          await authService.autoLogin();
          // 登录成功后重新获取知识库列表
          const data = await knowledgeService.getKnowledgeBases();
          setKnowledgeBases(data);
          setError(null);
        } catch (loginErr) {
          console.error('Auto login failed:', loginErr);
          setError('自动登录失败，请手动登录后重试');
        }
      } else {
        setError('获取知识库列表失败，请稍后重试');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // 检查是否已登录
    if (!authService.isAuthenticated()) {
      setError('未登录，正在尝试自动登录...');
      authService.autoLogin()
        .then(() => fetchKnowledgeBases())
        .catch(err => {
          console.error('Auto login failed:', err);
          setError('自动登录失败，请手动登录后重试');
          setLoading(false);
        });
    } else {
      fetchKnowledgeBases();
    }
  }, []);

  const handleDelete = async (id: number) => {
    if (window.confirm('确定要删除这个知识库吗？此操作不可撤销。')) {
      try {
        await knowledgeService.deleteKnowledgeBase(id);
        setKnowledgeBases(knowledgeBases.filter(kb => kb.id !== id));
      } catch (err) {
        console.error('Failed to delete knowledge base:', err);
        setError('删除知识库失败，请稍后重试');
      }
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">知识库管理</h1>
        <div className="flex space-x-2">
          <button
            onClick={fetchKnowledgeBases}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
          >
            刷新列表
          </button>
          <Link
            to="/knowledge/create"
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            创建知识库
          </Link>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4 flex justify-between items-center">
          <div>{error}</div>
          {error.includes('登录失败') && (
            <button
              onClick={() => authService.autoLogin().then(() => fetchKnowledgeBases())}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              重新登录
            </button>
          )}
        </div>
      )}

      {knowledgeBases.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500 mb-4">您还没有创建任何知识库</p>
          <Link
            to="/knowledge/create"
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            创建第一个知识库
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {knowledgeBases.map((kb) => (
            <div
              key={kb.id}
              className="border rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start">
                <h2 className="text-xl font-semibold mb-2">{kb.name}</h2>
                <div className="flex space-x-2">
                  <Link
                    to={`/knowledge/${kb.id}/edit`}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    编辑
                  </Link>
                  <button
                    onClick={() => handleDelete(kb.id)}
                    className="text-red-600 hover:text-red-800"
                  >
                    删除
                  </button>
                </div>
              </div>
              <p className="text-gray-600 mb-3">
                {kb.description || '暂无描述'}
              </p>
              <div className="flex justify-between items-center text-sm text-gray-500">
                <span>文档数量: {kb.documents.length}</span>
                <span>
                  创建时间: {new Date(kb.created_at).toLocaleDateString()}
                </span>
              </div>
              <div className="mt-4 flex justify-between">
                <Link
                  to={`/knowledge/${kb.id}`}
                  className="text-blue-600 hover:text-blue-800"
                >
                  查看详情
                </Link>
                <Link
                  to={`/knowledge/${kb.id}/search`}
                  className="text-green-600 hover:text-green-800"
                >
                  搜索
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default KnowledgeBaseList;
