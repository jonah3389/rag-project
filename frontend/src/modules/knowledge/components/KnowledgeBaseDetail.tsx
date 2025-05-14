import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import * as knowledgeService from '../services/knowledgeService';
import type { KnowledgeBase, Document } from '../services/knowledgeService';
import DocumentUpload from './DocumentUpload';
import DocumentList from './DocumentList';

const KnowledgeBaseDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [knowledgeBase, setKnowledgeBase] = useState<KnowledgeBase | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const fetchKnowledgeBase = async () => {
    if (!id) return;

    try {
      setLoading(true);
      setError(null);
      const data = await knowledgeService.getKnowledgeBase(parseInt(id));
      setKnowledgeBase(data);
    } catch (err) {
      console.error('Failed to fetch knowledge base:', err);
      setError('获取知识库详情失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKnowledgeBase();
  }, [id]);

  const handleUploadSuccess = (document: Document) => {
    if (knowledgeBase) {
      setKnowledgeBase({
        ...knowledgeBase,
        documents: [...knowledgeBase.documents, document],
      });
      setUploadSuccess(true);
      setTimeout(() => setUploadSuccess(false), 3000);
    }
  };

  const handleDelete = async () => {
    if (!id || !knowledgeBase) return;

    if (window.confirm(`确定要删除知识库 "${knowledgeBase.name}" 吗？此操作不可撤销，将删除所有相关文档。`)) {
      try {
        await knowledgeService.deleteKnowledgeBase(parseInt(id));
        navigate('/knowledge');
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

  if (error) {
    return (
      <div className="container mx-auto p-4">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
        <Link to="/knowledge" className="text-blue-600 hover:text-blue-800">
          返回知识库列表
        </Link>
      </div>
    );
  }

  if (!knowledgeBase) {
    return (
      <div className="container mx-auto p-4">
        <div className="text-center py-8">
          <p className="text-gray-500 mb-4">知识库不存在或已被删除</p>
          <Link
            to="/knowledge"
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            返回知识库列表
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      {/* 顶部导航和操作 */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <Link to="/knowledge" className="text-blue-600 hover:text-blue-800 mb-2 inline-block">
            &larr; 返回知识库列表
          </Link>
          <h1 className="text-2xl font-bold">{knowledgeBase.name}</h1>
        </div>
        <div className="flex space-x-2">
          <Link
            to={`/knowledge/${id}/search`}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
          >
            搜索知识库
          </Link>
          <Link
            to={`/knowledge/${id}/edit`}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            编辑知识库
          </Link>
          <button
            onClick={handleDelete}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
          >
            删除知识库
          </button>
        </div>
      </div>

      {/* 知识库信息 */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <p className="text-gray-600 mb-2">
          {knowledgeBase.description || '暂无描述'}
        </p>
        <div className="flex text-sm text-gray-500">
          <span className="mr-4">创建时间: {new Date(knowledgeBase.created_at).toLocaleString()}</span>
          <span>更新时间: {new Date(knowledgeBase.updated_at).toLocaleString()}</span>
        </div>
      </div>

      {/* 上传成功提示 */}
      {uploadSuccess && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          文档上传成功！
        </div>
      )}

      {/* 文档上传组件 */}
      <DocumentUpload
        knowledgeBaseId={parseInt(id)}
        onUploadSuccess={handleUploadSuccess}
      />

      {/* 文档列表 */}
      <DocumentList
        documents={knowledgeBase.documents}
        onDocumentDeleted={fetchKnowledgeBase}
      />
    </div>
  );
};

export default KnowledgeBaseDetail;
