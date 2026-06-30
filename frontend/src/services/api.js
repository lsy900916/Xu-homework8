/**
 * API 服务层 - 封装所有后端 API 调用
 */
import axios from "axios";
import { getToken, clearAuth } from "../utils/auth";
import toast from "react-hot-toast";

// API 基础配置
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 60000, // RAG 查询可能较慢
  headers: {
    "Content-Type": "application/json",
  },
});

// 请求拦截器 - 自动添加 JWT Token
apiClient.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// 响应拦截器 - 统一错误处理
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // Token 过期或无效
    if (error.response?.status === 401) {
      clearAuth();
      toast.error("登录已过期，请重新登录");
      window.location.href = "/login";
    }
    // 其他错误
    else {
      const message =
        error.response?.data?.message || error.message || "请求失败";
      toast.error(message);
    }
    return Promise.reject(error);
  },
);

// ==================== API 方法 ====================

/**
 * 认证 API
 */
export const authAPI = {
  /**
   * 用户登录
   */
  login: (data) => apiClient.post("/auth/login", data),

  /**
   * 用户注册
   */
  register: (data) => apiClient.post("/auth/register", data),

  /**
   * 获取当前用户信息
   */
  getCurrentUser: () => apiClient.get("/auth/me"),
};

/**
 * 新闻 API
 */
export const newsAPI = {
  /**
   * 获取新闻列表
   */
  getNewsList: (params) => apiClient.get("/news", { params }),

  /**
   * 获取新闻详情
   */
  getNewsDetail: (newsId) => apiClient.get(`/news/${newsId}`),
};

/**
 * RAG API
 */
export const ragAPI = {
  /**
   * RAG 问答
   */
  query: (data) => apiClient.post("/ask", data),
};

/**
 * 入库 API
 */
export const ingestAPI = {
  /**
   * 结构化数据入库
   */
  ingestStructured: (data) => apiClient.post("/ingest/structured", data),

  /**
   * 非结构化数据入库
   */
  ingestUnstructured: (data) => apiClient.post("/ingest/unstructured", data),
};

/**
 * 报告 API
 */
export const reportAPI = {
  /**
   * 聚类分析
   */
  getClusters: (params) => apiClient.get("/report/clusters", { params }),

  /**
   * 关键词 Top10
   */
  getTopKeywords: (params) => apiClient.get("/report/topkeywords", { params }),
};

/**
 * 系统 API
 */
export const systemAPI = {
  /**
   * 健康检查
   */
  getHealth: () => apiClient.get("/health"),
};

export default apiClient;
