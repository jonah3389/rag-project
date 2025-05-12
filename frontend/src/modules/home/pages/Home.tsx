import React from 'react';
import FeatureCard from '../components/FeatureCard';

const Home: React.FC = () => {
  const features = [
    {
      title: '智能对话',
      description: '基于大语言模型的智能对话系统，支持多轮对话、上下文理解和流式响应，为您提供自然流畅的交互体验。',
      icon: (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-8 w-8"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
          />
        </svg>
      ),
      linkTo: '/chat',
      color: 'bg-blue-600 hover:bg-blue-700',
    },
    {
      title: '知识库管理',
      description: '强大的知识库管理系统，支持文档上传、处理、搜索和检索，为智能对话提供知识支持，让AI回答更加准确。',
      icon: (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-8 w-8"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
          />
        </svg>
      ),
      linkTo: '/knowledge',
      color: 'bg-green-600 hover:bg-green-700',
    },
    {
      title: '文档处理',
      description: '支持多种格式文档的处理和转换，包括PDF、Word、TXT等，自动提取文本内容，构建知识索引，让文档管理更加高效。',
      icon: (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-8 w-8"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
      ),
      linkTo: '/document',
      color: 'bg-yellow-600 hover:bg-yellow-700',
    },
    {
      title: 'LLM 配置',
      description: '灵活的大语言模型配置管理，支持多种LLM提供商，用户可自定义配置参数，选择最适合自己需求的模型。',
      icon: (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-8 w-8"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
      ),
      linkTo: '/llm-config',
      color: 'bg-purple-600 hover:bg-purple-700',
    },
  ];

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="text-center mb-16">
        <h1 className="text-4xl font-bold mb-4">智能体综合应用平台</h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          基于大语言模型的综合性应用平台，集成多种智能功能，为您提供一站式的 AI 解决方案
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
        {features.map((feature, index) => (
          <FeatureCard
            key={index}
            title={feature.title}
            description={feature.description}
            icon={feature.icon}
            linkTo={feature.linkTo}
            color={feature.color}
          />
        ))}
      </div>

      <div className="bg-gray-100 rounded-lg p-8 mb-16">
        <h2 className="text-2xl font-bold mb-4">技术架构</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded shadow">
            <h3 className="font-bold mb-2">前端</h3>
            <p>React + TypeScript + Vite</p>
          </div>
          <div className="bg-white p-4 rounded shadow">
            <h3 className="font-bold mb-2">后端</h3>
            <p>FastAPI + SQLAlchemy + Celery</p>
          </div>
          <div className="bg-white p-4 rounded shadow">
            <h3 className="font-bold mb-2">数据存储</h3>
            <p>MySQL + MinIO + Redis</p>
          </div>
          <div className="bg-white p-4 rounded shadow">
            <h3 className="font-bold mb-2">AI 引擎</h3>
            <p>AutoGen + 多种 LLM 提供商</p>
          </div>
        </div>
      </div>

      <div className="text-center">
        <h2 className="text-2xl font-bold mb-4">开始使用</h2>
        <p className="text-gray-600 mb-6">
          立即注册并体验我们的智能体综合应用平台，提升您的工作效率
        </p>
        <div className="flex justify-center gap-4">
          <a
            href="/register"
            className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            注册账号
          </a>
          <a
            href="/login"
            className="px-6 py-3 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
          >
            登录
          </a>
        </div>
      </div>
    </div>
  );
};

export default Home;
