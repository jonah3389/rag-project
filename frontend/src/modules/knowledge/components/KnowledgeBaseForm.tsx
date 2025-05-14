import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import * as knowledgeService from '../services/knowledgeService';
import type { KnowledgeBase } from '../services/knowledgeService';

interface KnowledgeBaseFormProps {
  initialData?: KnowledgeBase;
  isEditing?: boolean;
}

const KnowledgeBaseForm: React.FC<KnowledgeBaseFormProps> = ({
  initialData,
  isEditing = false,
}) => {
  const [name, setName] = useState(initialData?.name || '');
  const [description, setDescription] = useState(initialData?.description || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim()) {
      setError('知识库名称不能为空');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      if (isEditing && initialData) {
        await knowledgeService.updateKnowledgeBase(initialData.id, name, description);
        navigate(`/knowledge/${initialData.id}`);
      } else {
        const newKnowledgeBase = await knowledgeService.createKnowledgeBase(name, description);
        navigate(`/knowledge/${newKnowledgeBase.id}`);
      }
    } catch (err) {
      console.error('Failed to save knowledge base:', err);
      setError('保存知识库失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">
        {isEditing ? '编辑知识库' : '创建知识库'}
      </h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
            知识库名称 <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="输入知识库名称"
            required
          />
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
            知识库描述
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="输入知识库描述（可选）"
            rows={4}
          />
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            onClick={() => navigate('/knowledge')}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            取消
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-blue-400"
          >
            {loading ? '保存中...' : '保存'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default KnowledgeBaseForm;
