import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import * as knowledgeService from '../services/knowledgeService';
import type { KnowledgeBase } from '../services/knowledgeService';
import KnowledgeBaseForm from './KnowledgeBaseForm';

const EditKnowledgeBase: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [knowledgeBase, setKnowledgeBase] = useState<KnowledgeBase | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
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

    fetchKnowledgeBase();
  }, [id]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto p-4">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
        <button
          onClick={() => navigate('/knowledge')}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          返回知识库列表
        </button>
      </div>
    );
  }

  if (!knowledgeBase) {
    return (
      <div className="max-w-2xl mx-auto p-4">
        <div className="text-center py-8">
          <p className="text-gray-500 mb-4">知识库不存在或已被删除</p>
          <button
            onClick={() => navigate('/knowledge')}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            返回知识库列表
          </button>
        </div>
      </div>
    );
  }

  return <KnowledgeBaseForm initialData={knowledgeBase} isEditing={true} />;
};

export default EditKnowledgeBase;
