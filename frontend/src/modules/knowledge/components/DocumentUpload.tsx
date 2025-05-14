import React, { useState, useRef, useEffect } from 'react';
import * as knowledgeService from '../services/knowledgeService';
import { TaskStatus } from '../services/knowledgeService';
import type { Document, DocumentProcessTask } from '../services/knowledgeService';

interface DocumentUploadProps {
  knowledgeBaseId: number;
  onUploadSuccess: (document: Document) => void;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({
  knowledgeBaseId,
  onUploadSuccess
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [processingStatus, setProcessingStatus] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [currentTask, setCurrentTask] = useState<DocumentProcessTask | null>(null);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
      setError(null);
    }
  };

  const validateFile = (file: File): boolean => {
    const allowedTypes = [
      'application/pdf',
      'text/plain',
      'text/markdown',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];

    if (!allowedTypes.includes(file.type)) {
      setError('不支持的文件类型，请上传 PDF、TXT、Markdown 或 Word 文档');
      return false;
    }

    // 限制文件大小为 20MB
    const maxSize = 20 * 1024 * 1024;
    if (file.size > maxSize) {
      setError('文件大小不能超过 20MB');
      return false;
    }

    return true;
  };

  // 记录轮询错误次数
  const [pollErrorCount, setPollErrorCount] = useState(0);
  const MAX_POLL_ERRORS = 3; // 最大允许的连续错误次数

  // 轮询任务状态
  const pollTaskStatus = async (taskId: number) => {
    try {
      console.log('轮询任务状态，任务ID:', taskId);

      // 使用 Promise.race 和超时处理，确保请求不会无限阻塞
      const taskPromise = knowledgeService.getDocumentTask(taskId);
      const timeoutPromise = new Promise<never>((_, reject) => {
        setTimeout(() => reject(new Error('任务状态查询超时')), 5000);
      });

      const task = await Promise.race([taskPromise, timeoutPromise]);

      // 重置错误计数
      if (pollErrorCount > 0) {
        setPollErrorCount(0);
      }

      console.log('任务状态响应:', task);
      setCurrentTask(task);

      // 根据任务状态更新处理状态
      switch (task.status) {
        case TaskStatus.PENDING:
          console.log('任务等待处理中');
          setProcessingStatus('等待处理');
          // 继续轮询
          return false; // 返回 false 表示轮询应该继续

        case TaskStatus.PROCESSING:
          console.log('任务处理中');
          setProcessingStatus('处理中');
          // 继续轮询
          return false; // 返回 false 表示轮询应该继续

        case TaskStatus.COMPLETED:
          console.log('任务已完成');
          setProcessingStatus('处理完成');

          // 如果任务完成且有关联文档，通知父组件
          if (task.document) {
            console.log('任务关联的文档:', task.document);
            onUploadSuccess(task.document);
          } else {
            console.warn('任务已完成但没有关联文档，尝试获取最新文档列表');

            // 尝试获取最新的文档列表
            try {
              const documents = await knowledgeService.getDocuments(task.knowledge_base_id);
              // 查找可能匹配的文档（基于文件名）
              const possibleDocument = documents.find(d =>
                d.title === task.file_name &&
                new Date(d.created_at).getTime() > new Date(task.created_at).getTime()
              );

              if (possibleDocument) {
                console.log('找到可能匹配的文档:', possibleDocument);
                onUploadSuccess(possibleDocument);
              } else {
                console.error('未找到匹配的文档');
                setError('文档处理完成，但无法获取文档信息');
              }
            } catch (e) {
              console.error('获取文档列表失败:', e);
            }
          }

          // 停止轮询
          return true; // 返回 true 表示轮询应该停止

        case TaskStatus.FAILED:
          console.error('任务失败:', task.error_message);
          setProcessingStatus(null);
          setError(`处理失败: ${task.error_message || '未知错误'}`);

          // 停止轮询
          return true; // 返回 true 表示轮询应该停止

        default:
          console.warn('未知任务状态:', task.status);
          setProcessingStatus(`未知状态(${task.status})`);
          // 继续轮询
          return false; // 返回 false 表示轮询应该继续
      }
    } catch (err: any) {
      console.error('轮询任务状态失败:', err);
      console.log('错误详情:', {
        message: err.message,
        stack: err.stack,
        response: err.response?.data,
        status: err.response?.status
      });

      // 增加错误计数
      const newErrorCount = pollErrorCount + 1;
      setPollErrorCount(newErrorCount);

      // 如果连续错误次数超过阈值，停止轮询
      if (newErrorCount >= MAX_POLL_ERRORS) {
        console.error(`连续 ${MAX_POLL_ERRORS} 次轮询失败，停止轮询`);
        setProcessingStatus('查询状态失败，请刷新页面查看最新状态');
        return true; // 停止轮询
      }

      // 如果是404错误（任务不存在），可能是任务还未创建完成
      if (err.response && err.response.status === 404) {
        console.log('任务可能还未创建完成，继续轮询');
        return false; // 继续轮询
      } else if (err.message && err.message.includes('超时')) {
        console.warn('任务状态查询超时，将在下次轮询中重试');
        return false; // 继续轮询，但不立即重试
      } else {
        // 其他错误，记录但继续轮询
        console.warn('轮询遇到错误，但将继续尝试');
        return false; // 继续轮询
      }
    }
  };

  // 清理轮询
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        // 检查是 setTimeout 还是 setInterval
        clearTimeout(pollingInterval as unknown as number);
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);

  // 记录轮询次数，用于计算指数退避
  const [pollCount, setPollCount] = useState(0);

  // 使用递归函数代替 setInterval，实现指数退避
  const startPolling = async (taskId: number) => {
    // 清除之前的轮询
    if (pollingInterval) {
      clearInterval(pollingInterval);
      setPollingInterval(null);
    }

    // 重置轮询计数
    setPollCount(0);
    setPollErrorCount(0);

    // 开始轮询
    await pollWithBackoff(taskId);
  };

  // 带指数退避的轮询函数
  const pollWithBackoff = async (taskId: number) => {
    // 立即执行一次轮询
    const shouldStop = await pollTaskStatus(taskId);

    // 如果应该停止轮询，则直接返回
    if (shouldStop) {
      console.log('轮询结果表明应该停止轮询');
      return;
    }

    // 增加轮询次数
    const newPollCount = pollCount + 1;
    setPollCount(newPollCount);

    // 计算下次轮询间隔（指数退避）
    // 初始间隔为2秒，每次轮询后增加1秒，最大间隔为10秒
    const baseInterval = 2000; // 基础间隔2秒
    const maxInterval = 10000; // 最大间隔10秒
    const interval = Math.min(baseInterval + (newPollCount - 1) * 1000, maxInterval);

    console.log(`安排下次轮询，间隔: ${interval}ms`);

    // 设置下次轮询的定时器
    const timeoutId = setTimeout(async () => {
      // 检查是否已经超过最大轮询时间（5分钟）
      if (newPollCount * interval > 5 * 60 * 1000) {
        console.log('达到最大轮询时间，停止轮询');
        setProcessingStatus('处理超时，请刷新页面查看最新状态');
        return;
      }

      // 递归调用自身，继续轮询
      await pollWithBackoff(taskId);
    }, interval);

    // 保存定时器ID，以便在需要时清除
    setPollingInterval(timeoutId as unknown as NodeJS.Timeout);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('请选择要上传的文件');
      return;
    }

    if (!validateFile(selectedFile)) {
      return;
    }

    try {
      setUploading(true);
      setUploadSuccess(false);
      setProcessingStatus(null);
      setProgress(0); // 重置进度
      setError(null);

      console.log('开始上传文件:', selectedFile.name);

      // 上传文件，获取任务信息，并监控上传进度
      const task = await knowledgeService.uploadDocument(
        knowledgeBaseId,
        selectedFile,
        (uploadProgress) => {
          // 显示上传进度
          setProgress(uploadProgress);
        }
      );

      console.log('文件上传成功，获取任务信息:', task);

      // 文件上传成功，立即显示成功提示
      setUploadSuccess(true);
      setProgress(100); // 上传完成，进度设为100%
      setCurrentTask(task);

      // 清空文件输入框
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      setSelectedFile(null);

      // 2秒后隐藏进度条
      setTimeout(() => {
        setProgress(0);
      }, 2000);

      // 开始轮询任务状态
      startPolling(task.id);

    } catch (uploadError: any) {
      console.error('Failed to upload document:', uploadError);

      // 记录更详细的错误信息用于调试
      console.log('Error details:', {
        message: uploadError.message,
        stack: uploadError.stack,
        response: uploadError.response?.data,
        status: uploadError.response?.status,
        headers: uploadError.response?.headers,
        request: uploadError.request,
        config: uploadError.config
      });

      // 检查是否是超时错误
      const isTimeoutError = uploadError.code === 'ECONNABORTED' ||
        (uploadError.message && uploadError.message.includes('timeout'));

      if (isTimeoutError) {
        console.log('检测到上传超时，但文件可能已上传成功，尝试验证...');

        // 显示临时消息
        setError('上传超时，正在验证文件是否已上传成功...');

        // 立即尝试验证文件是否已上传成功
        try {
          // 先等待一小段时间，让服务器有时间处理
          await new Promise(resolve => setTimeout(resolve, 2000));

          console.log('尝试获取最新的任务列表...');
          const tasks = await knowledgeService.getKnowledgeBaseDocumentTasks(knowledgeBaseId);

          // 查找可能匹配的任务（基于文件名和时间）
          const possibleTask = tasks.find(t =>
            t.file_name === selectedFile.name &&
            new Date(t.created_at).getTime() > Date.now() - 10 * 60 * 1000 // 10分钟内创建的
          );

          if (possibleTask) {
            console.log('找到可能的上传任务:', possibleTask);

            // 更新状态为上传成功
            setCurrentTask(possibleTask);
            setUploadSuccess(true);
            setError(null);

            // 清空文件输入框
            if (fileInputRef.current) {
              fileInputRef.current.value = '';
            }
            setSelectedFile(null);

            // 开始轮询任务状态
            startPolling(possibleTask.id);
            return;
          } else {
            // 没有找到匹配的任务，可能真的上传失败了
            setError('上传超时且未找到已处理的任务，请重试或使用较小的文件');
          }
        } catch (e) {
          console.error('验证上传失败:', e);
          setError('上传超时，无法验证文件是否已上传成功，请刷新页面查看最新状态');
        }
      } else if (uploadError.response) {
        // 服务器返回了错误响应
        const errorMessage = uploadError.response.data?.detail || '文档上传失败，服务器返回错误';
        setError(`上传失败: ${errorMessage} (状态码: ${uploadError.response.status})`);
      } else if (uploadError.request) {
        // 请求已发送但没有收到响应
        setError('上传失败: 服务器没有响应，请检查网络连接或稍后重试');

        // 尝试验证文件是否已上传成功
        setTimeout(async () => {
          try {
            console.log('尝试获取最新的任务列表...');
            const tasks = await knowledgeService.getKnowledgeBaseDocumentTasks(knowledgeBaseId);

            // 查找可能匹配的任务（基于文件名和时间）
            const possibleTask = tasks.find(t =>
              t.file_name === selectedFile.name &&
              new Date(t.created_at).getTime() > Date.now() - 10 * 60 * 1000 // 10分钟内创建的
            );

            if (possibleTask) {
              console.log('找到可能的上传任务:', possibleTask);
              setCurrentTask(possibleTask);
              setUploadSuccess(true);
              setError(null);
              // 开始轮询任务状态
              startPolling(possibleTask.id);
              return;
            }
          } catch (e) {
            console.error('验证上传失败:', e);
          }
        }, 3000); // 等待3秒后尝试验证
      } else {
        // 请求设置时出错
        setError(`上传失败: ${uploadError.message || '未知错误'}`);
      }

      // 清除轮询
      if (pollingInterval) {
        clearTimeout(pollingInterval as unknown as number);
        clearInterval(pollingInterval);
        setPollingInterval(null);
      }

      setUploading(false);
      setUploadSuccess(false);
      setProcessingStatus(null);
      setProgress(0);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
      <h2 className="text-xl font-semibold mb-4">上传文档</h2>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          选择文件
        </label>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-500
            file:mr-4 file:py-2 file:px-4
            file:rounded-md file:border-0
            file:text-sm file:font-semibold
            file:bg-blue-50 file:text-blue-700
            hover:file:bg-blue-100"
          accept=".pdf,.txt,.md,.doc,.docx"
          disabled={uploading}
        />
        <p className="mt-1 text-sm text-gray-500">
          支持的文件格式: PDF, TXT, Markdown, Word (最大 20MB)
        </p>
      </div>

      {selectedFile && (
        <div className="mb-4 p-3 bg-gray-50 rounded-md">
          <div className="flex justify-between items-center">
            <div>
              <p className="font-medium">{selectedFile.name}</p>
              <p className="text-sm text-gray-500">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
            <button
              type="button"
              onClick={() => setSelectedFile(null)}
              className="text-red-600 hover:text-red-800"
              disabled={uploading}
            >
              移除
            </button>
          </div>
        </div>
      )}

      {/* 上传进度条 */}
      {progress > 0 && (
        <div className="mb-4">
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <div className="flex justify-between items-center mt-1">
            <p className="text-sm text-gray-500">上传中</p>
            <p className="text-sm text-gray-500">{progress}%</p>
          </div>
        </div>
      )}

      {/* 上传成功提示 */}
      {uploadSuccess && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded">
          <div className="flex items-center">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
            </svg>
            <span className="font-medium">文件上传成功！</span>
          </div>
          {processingStatus && (
            <div className="mt-2 flex items-center">
              <div className="mr-2">
                {processingStatus === '处理完成' ? (
                  <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                ) : (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-green-700"></div>
                )}
              </div>
              <p className="text-sm">文件处理状态: {processingStatus}</p>
            </div>
          )}
        </div>
      )}

      <div className="flex space-x-2">
        {uploadSuccess ? (
          <button
            type="button"
            onClick={() => {
              // 重置状态，允许用户上传新文件
              setUploadSuccess(false);
              setProcessingStatus(null);
              setCurrentTask(null);
              setError(null);
              setProgress(0);
              // 清除轮询
              if (pollingInterval) {
                clearTimeout(pollingInterval as unknown as number);
                clearInterval(pollingInterval);
                setPollingInterval(null);
              }
            }}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            上传新文件
          </button>
        ) : (
          <button
            type="button"
            onClick={handleUpload}
            disabled={!selectedFile || uploading}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {uploading ? '上传中...' : '上传文档'}
          </button>
        )}

        {error && (
          <button
            type="button"
            onClick={handleUpload}
            disabled={!selectedFile || uploading}
            className="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            重试
          </button>
        )}
      </div>
    </div>
  );
};

export default DocumentUpload;
