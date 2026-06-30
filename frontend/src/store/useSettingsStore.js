/**
 * 设置状态管理
 */
import { create } from "zustand";
import { persist } from "zustand/middleware";

const defaultSettings = {
  ollamaHost: "http://127.0.0.1:11434",
  enableFallback: true,
  smtpEnabled: false,
  smtpHost: "smtp.example.com",
  smtpPort: 587,
  smtpUser: "",
};

export const useSettingsStore = create(
  persist(
    (set) => ({
      ...defaultSettings,

      updateSettings: (settings) => set((state) => ({ ...state, ...settings })),

      resetSettings: () => set(defaultSettings),
    }),
    {
      name: "xu-news-settings",
    },
  ),
);
