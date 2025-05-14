import React, { useState } from 'react';
import type { Document } from '../services/knowledgeService';

interface DocumentListProps {
  documents: Document[];
  onDocumentDeleted: () => void;
}

const DocumentList: React.FC<DocumentListProps> = ({ documents, onDocumentDeleted }) => {
  const [expandedDocId, setExpandedDocId] = useState<number | null>(null);

  const toggleExpand = (id: number) => {
    setExpandedDocId(expandedDocId === id ? null : id);
  };

  const getFileTypeIcon = (fileType?: string) => {
    switch (fileType?.toLowerCase()) {
      case 'pdf':
        return '📄';
      case 'txt':
        return '📝';
      case 'md':
        return '📑';
      case 'doc':
      case 'docx':
        return '📃';
      default:
        return '📄';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const truncateContent = (content?: string, maxLength: number = 200) => {
    if (!content) return '无内容';
    return content.length > maxLength
      ? content.substring(0, maxLength) + '...'
      : content;
  };

  if (documents.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-4">文档列表</h2>
        <div className="text-center py-8 text-gray-500">
          暂无文档，请上传文档
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-xl font-semibold mb-4">文档列表 ({documents.length})</h2>

      <div className="space-y-4">
        {documents.map((doc) => (
          <div
            key={doc.id}
            className="border rounded-lg p-4 hover:shadow-sm transition-shadow"
          >
            <div className="flex justify-between items-start">
              <div className="flex items-start">
                <span className="text-2xl mr-3">{getFileTypeIcon(doc.file_type)}</span>
                <div>
                  <h3 className="font-medium">{doc.title}</h3>
                  <p className="text-sm text-gray-500">
                    上传时间: {formatDate(doc.created_at)}
                  </p>
                </div>
              </div>
              <button
                onClick={() => toggleExpand(doc.id)}
                className="text-blue-600 hover:text-blue-800"
              >
                {expandedDocId === doc.id ? '收起' : '查看内容'}
              </button>
            </div>

            {expandedDocId === doc.id && doc.content && (
              <div className="mt-4 p-3 bg-gray-50 rounded-md max-h-96 overflow-y-auto">
                <pre className="whitespace-pre-wrap font-sans text-sm">
                  {doc.content}
                </pre>
              </div>
            )}

            {expandedDocId !== doc.id && doc.content && (
              <div className="mt-2 text-sm text-gray-600">
                {truncateContent(doc.content)}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default DocumentList;
