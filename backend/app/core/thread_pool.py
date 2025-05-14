"""
线程池工具，用于执行CPU密集型任务
"""

import concurrent.futures
import logging
import threading
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

T = TypeVar('T')

logger = logging.getLogger(__name__)


class ThreadPoolManager:
    """
    线程池管理器，用于执行CPU密集型任务
    
    使用单例模式，确保整个应用程序只有一个线程池
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ThreadPoolManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, max_workers: int = None):
        """
        初始化线程池管理器
        
        Args:
            max_workers: 最大工作线程数，默认为 None（使用 CPU 核心数 * 5）
        """
        if self._initialized:
            return
            
        self._initialized = True
        self._max_workers = max_workers
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self._futures: Dict[str, concurrent.futures.Future] = {}
        self._lock = threading.Lock()
        
        logger.info(f"线程池初始化完成，最大工作线程数: {max_workers or '默认'}")
    
    def submit(self, task_id: str, fn: Callable[..., T], *args, **kwargs) -> concurrent.futures.Future:
        """
        提交任务到线程池
        
        Args:
            task_id: 任务ID，用于标识任务
            fn: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            Future 对象
        """
        logger.info(f"提交任务到线程池: {task_id}")
        
        # 如果任务已存在，先取消
        self.cancel_task(task_id)
        
        # 提交新任务
        future = self._executor.submit(fn, *args, **kwargs)
        
        # 添加回调，在任务完成时自动清理
        future.add_done_callback(lambda f: self._cleanup_task(task_id, f))
        
        # 保存 Future
        with self._lock:
            self._futures[task_id] = future
            
        return future
    
    def _cleanup_task(self, task_id: str, future: concurrent.futures.Future) -> None:
        """
        清理已完成的任务
        
        Args:
            task_id: 任务ID
            future: Future 对象
        """
        with self._lock:
            if task_id in self._futures and self._futures[task_id] == future:
                logger.info(f"任务完成，从线程池中移除: {task_id}")
                self._futures.pop(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功取消
        """
        with self._lock:
            if task_id in self._futures:
                future = self._futures[task_id]
                cancelled = future.cancel()
                if cancelled:
                    logger.info(f"成功取消任务: {task_id}")
                    self._futures.pop(task_id)
                else:
                    logger.warning(f"无法取消任务，可能已经在执行: {task_id}")
                return cancelled
        return False
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态信息，如果任务不存在则返回 None
        """
        with self._lock:
            if task_id in self._futures:
                future = self._futures[task_id]
                return {
                    'task_id': task_id,
                    'running': future.running(),
                    'done': future.done(),
                    'cancelled': future.cancelled(),
                }
        return None
    
    def shutdown(self, wait: bool = True) -> None:
        """
        关闭线程池
        
        Args:
            wait: 是否等待所有任务完成
        """
        logger.info(f"关闭线程池，等待任务完成: {wait}")
        self._executor.shutdown(wait=wait)
        self._futures.clear()


# 创建全局线程池实例
thread_pool = ThreadPoolManager()
