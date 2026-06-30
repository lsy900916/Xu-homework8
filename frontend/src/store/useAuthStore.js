/**
 * 认证状态管理
 */
import { create } from "zustand";
import { getUser, saveAuth, clearAuth, isAuthenticated } from "../utils/auth";

export const useAuthStore = create((set) => ({
  user: getUser(),
  isAuthenticated: isAuthenticated(),

  login: (token, expiresIn, user) => {
    saveAuth(token, expiresIn, user);
    set({ user, isAuthenticated: true });
  },

  logout: () => {
    clearAuth();
    set({ user: null, isAuthenticated: false });
  },

  checkAuth: () => {
    const user = getUser();
    const isAuth = isAuthenticated();
    set({ user, isAuthenticated: isAuth });
  },
}));
