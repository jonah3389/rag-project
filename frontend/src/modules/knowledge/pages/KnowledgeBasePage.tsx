import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import KnowledgeBaseList from '../components/KnowledgeBaseList';
import KnowledgeBaseForm from '../components/KnowledgeBaseForm';
import KnowledgeBaseDetail from '../components/KnowledgeBaseDetail';
import KnowledgeSearch from '../components/KnowledgeSearch';
import EditKnowledgeBase from '../components/EditKnowledgeBase';

const KnowledgeBasePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        {/* 知识库列表 */}
        <Route path="/" element={<KnowledgeBaseList />} />

        {/* 创建知识库 */}
        <Route path="/create" element={<KnowledgeBaseForm />} />

        {/* 编辑知识库 */}
        <Route path="/:id/edit" element={<EditKnowledgeBase />} />

        {/* 知识库详情 */}
        <Route path="/:id" element={<KnowledgeBaseDetail />} />

        {/* 搜索知识库 */}
        <Route path="/:id/search" element={<KnowledgeSearch />} />

        {/* 默认重定向到列表 */}
        <Route path="*" element={<Navigate to="/knowledge" replace />} />
      </Routes>
    </div>
  );
};

export default KnowledgeBasePage;
