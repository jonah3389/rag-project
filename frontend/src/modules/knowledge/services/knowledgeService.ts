import api from '../../../shared/services/api';

// 知识库类型定义
export interface KnowledgeBase {
  id: number;
  name: string;
  description?: string;
  user_id: number;
  created_at: string;
  updated_at: string;
  documents: Document[];
}

export interface Document {
  id: number;
  title: string;
  content?: string;
  file_path?: string;
  file_type?: string;
  knowledge_base_id: number;
  created_at: string;
  updated_at: string;
}

export interface SearchResult {
  content: string;
  score: number;
  document: Document;
  metadata: Record<string, any>;
}

export enum TaskStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed"
}

export interface DocumentProcessTask {
  id: number;
  file_name: string;
  file_path: string;
  file_type: string;
  status: TaskStatus;
  error_message?: string;
  knowledge_base_id: number;
  document_id?: number;
  document?: Document;
  created_at: string;
  updated_at: string;
}

// 创建知识库
export const createKnowledgeBase = async (
  name: string,
  description?: string
): Promise<KnowledgeBase> => {
  const response = await api.post<KnowledgeBase>('/knowledge/knowledge-bases', {
    name,
    description,
  });
  return response.data;
};

// 获取所有知识库
export const getKnowledgeBases = async (): Promise<KnowledgeBase[]> => {
  const response = await api.get<KnowledgeBase[]>('/knowledge/knowledge-bases');
  return response.data;
};

// 获取知识库详情
export const getKnowledgeBase = async (id: number): Promise<KnowledgeBase> => {
  const response = await api.get<KnowledgeBase>(`/knowledge/knowledge-bases/${id}`);
  return response.data;
};

// 更新知识库
export const updateKnowledgeBase = async (
  id: number,
  name?: string,
  description?: string
): Promise<KnowledgeBase> => {
  const response = await api.put<KnowledgeBase>(`/knowledge/knowledge-bases/${id}`, {
    name,
    description,
  });
  return response.data;
};

// 删除知识库
export const deleteKnowledgeBase = async (id: number): Promise<KnowledgeBase> => {
  const response = await api.delete<KnowledgeBase>(`/knowledge/knowledge-bases/${id}`);
  return response.data;
};

// 获取知识库中的文档
export const getDocuments = async (knowledgeBaseId: number): Promise<Document[]> => {
  const response = await api.get<Document[]>(`/knowledge/knowledge-bases/${knowledgeBaseId}/documents`);
  return response.data;
};

// 上传文档（异步处理）
export const uploadDocument = async (
  knowledgeBaseId: number,
  file: File,
  onProgress?: (progress: number) => void
): Promise<DocumentProcessTask> => {
  const formData = new FormData();
  formData.append('file', file);

  // 计算合适的超时时间：每MB至少给30秒，最少5分钟，最多30分钟
  const fileSizeMB = file.size / (1024 * 1024);
  const timeoutMs = Math.max(
    5 * 60 * 1000, // 最少5分钟
    Math.min(
      30 * 60 * 1000, // 最多30分钟
      Math.ceil(fileSizeMB * 30 * 1000) // 每MB 30秒
    )
  );

  console.log(`文件大小: ${fileSizeMB.toFixed(2)}MB, 设置超时时间: ${(timeoutMs / 1000 / 60).toFixed(1)}分钟`);

  const response = await api.post<DocumentProcessTask>(
    `/knowledge/knowledge-bases/${knowledgeBaseId}/upload`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: timeoutMs,
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / (progressEvent.total || 100)
        );
        console.log(`上传进度: ${percentCompleted}%`);
        onProgress?.(percentCompleted);
      },
    }
  );
  return response.data;
};

// 获取文档处理任务
export const getDocumentTask = async (taskId: number): Promise<DocumentProcessTask> => {
  const response = await api.get<DocumentProcessTask>(`/knowledge/document-tasks/${taskId}`, {
    timeout: 5000, // 5秒超时，确保查询任务状态的请求不会阻塞太久
  });
  return response.data;
};

// 获取知识库的所有文档处理任务
export const getKnowledgeBaseDocumentTasks = async (
  knowledgeBaseId: number
): Promise<DocumentProcessTask[]> => {
  const response = await api.get<DocumentProcessTask[]>(
    `/knowledge/knowledge-bases/${knowledgeBaseId}/document-tasks`
  );
  return response.data;
};

// 搜索知识库
export const searchKnowledgeBase = async (
  knowledgeBaseId: number,
  query: string,
  limit: number = 5
): Promise<SearchResult[]> => {
  const response = await api.post<SearchResult[]>(`/knowledge/knowledge-bases/${knowledgeBaseId}/search`, {
    query,
    limit,
  });
  return response.data;
};
