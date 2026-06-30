/**
 * 认证工具函数 - JWT Token 管理
 */

const TOKEN_KEY = "xu_news_token";
const USER_KEY = "xu_news_user";
const TOKEN_EXPIRES_KEY = "xu_news_token_expires";

/**
 * 保存认证信息
 */
export const saveAuth = (token, expiresIn, user) => {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));

  // 计算过期时间（当前时间 + expiresIn 秒）
  const expiresAt = Date.now() + expiresIn * 1000;
  localStorage.setItem(TOKEN_EXPIRES_KEY, expiresAt.toString());
};

/**
 * 获取 Token
 */
export const getToken = () => {
  const token = localStorage.getItem(TOKEN_KEY);
  const expiresAt = localStorage.getItem(TOKEN_EXPIRES_KEY);

  // 检查是否过期
  if (token && expiresAt) {
    if (Date.now() > parseInt(expiresAt)) {
      // Token 已过期
      clearAuth();
      return null;
    }
    return token;
  }

  return null;
};

/**
 * 获取用户信息
 */
export const getUser = () => {
  const userStr = localStorage.getItem(USER_KEY);
  if (userStr) {
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }
  return null;
};

/**
 * 清除认证信息
 */
export const clearAuth = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem(TOKEN_EXPIRES_KEY);
};

/**
 * 检查是否已登录
 */
export const isAuthenticated = () => {
  return getToken() !== null;
};

/**
 * 检查 Token 是否即将过期（小于 5 分钟）
 */
export const isTokenExpiringSoon = () => {
  const expiresAt = localStorage.getItem(TOKEN_EXPIRES_KEY);
  if (expiresAt) {
    const timeLeft = parseInt(expiresAt) - Date.now();
    return timeLeft < 5 * 60 * 1000; // 小于 5 分钟
  }
  return false;
};
