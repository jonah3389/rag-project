import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import * as knowledgeService from '../services/knowledgeService';
import type { KnowledgeBase, SearchResult } from '../services/knowledgeService';

const KnowledgeSearch: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [knowledgeBase, setKnowledgeBase] = useState<KnowledgeBase | null>(null);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
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

  const handleSearch = async () => {
    if (!id || !query.trim()) return;

    try {
      setSearching(true);
      setError(null);
      const results = await knowledgeService.searchKnowledgeBase(parseInt(id), query);
      setResults(results);
      setHasSearched(true);
    } catch (err) {
      console.error('Search failed:', err);
      setError('搜索失败，请稍后重试');
    } finally {
      setSearching(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
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
      {/* 顶部导航和标题 */}
      <div className="mb-6">
        <Link to={`/knowledge/${id}`} className="text-blue-600 hover:text-blue-800 mb-2 inline-block">
          &larr; 返回知识库详情
        </Link>
        <h1 className="text-2xl font-bold">搜索知识库: {knowledgeBase.name}</h1>
      </div>

      {/* 搜索框 */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div className="flex">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入搜索关键词..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSearch}
            disabled={searching || !query.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-r-md hover:bg-blue-700 disabled:bg-blue-400"
          >
            {searching ? '搜索中...' : '搜索'}
          </button>
        </div>
      </div>

      {/* 搜索结果 */}
      {hasSearched && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">
            搜索结果 ({results.length})
          </h2>

          {results.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              没有找到匹配的结果，请尝试其他关键词
            </div>
          ) : (
            <div className="space-y-6">
              {results.map((result, index) => (
                <div
                  key={index}
                  className="border rounded-lg p-4 hover:shadow-sm transition-shadow"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-medium">{result.document.title}</h3>
                    <span className="text-sm bg-green-100 text-green-800 px-2 py-1 rounded">
                      相关度: {(result.score * 100).toFixed(0)}%
                    </span>
                  </div>

                  <div className="p-3 bg-yellow-50 rounded-md">
                    <p className="whitespace-pre-wrap text-sm">{result.content}</p>
                  </div>

                  <div className="mt-2 flex justify-between text-sm">
                    <span className="text-gray-500">
                      文档 ID: {result.document.id}
                    </span>
                    <button
                      onClick={() => {
                        const element = document.getElementById(`result-${index}`);
                        if (element) {
                          element.classList.toggle('max-h-40');
                          element.classList.toggle('max-h-none');
                        }
                      }}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      展开/收起
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default KnowledgeSearch;
