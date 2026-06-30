/**
 * 设置页面
 */
import { useSettingsStore } from "../store/useSettingsStore";
import toast from "react-hot-toast";
import { Settings as SettingsIcon, Save } from "lucide-react";

export default function Settings() {
  const settings = useSettingsStore();

  const handleSave = () => {
    toast.success("设置已保存");
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">设置</h1>
        <p className="text-gray-600 mt-2">配置系统参数（仅本地生效）</p>
      </div>

      <div className="bg-white rounded-lg shadow p-6 space-y-6">
        {/* Ollama 配置 */}
        <div>
          <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <SettingsIcon size={20} />
            Ollama 配置
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ollama Host
              </label>
              <input
                type="text"
                value={settings.ollamaHost}
                onChange={(e) =>
                  settings.updateSettings({ ollamaHost: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="http://127.0.0.1:11434"
              />
              <p className="text-xs text-gray-500 mt-1">
                本地 Ollama 服务地址（仅前端展示用）
              </p>
            </div>
          </div>
        </div>

        {/* 搜索配置 */}
        <div className="pt-6 border-t">
          <h2 className="text-lg font-bold text-gray-900 mb-4">搜索配置</h2>
          <div className="space-y-4">
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={settings.enableFallback}
                onChange={(e) =>
                  settings.updateSettings({ enableFallback: e.target.checked })
                }
                className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
              />
              <div>
                <p className="text-sm font-medium text-gray-900">
                  启用回退搜索
                </p>
                <p className="text-xs text-gray-500">
                  当本地检索结果不足时，自动调用百度搜索
                </p>
              </div>
            </label>
          </div>
        </div>

        {/* SMTP 配置 */}
        <div className="pt-6 border-t">
          <h2 className="text-lg font-bold text-gray-900 mb-4">邮件配置</h2>
          <div className="space-y-4">
            <label className="flex items-center gap-3 mb-4">
              <input
                type="checkbox"
                checked={settings.smtpEnabled}
                onChange={(e) =>
                  settings.updateSettings({ smtpEnabled: e.target.checked })
                }
                className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
              />
              <p className="text-sm font-medium text-gray-900">启用邮件通知</p>
            </label>

            {settings.smtpEnabled && (
              <div className="space-y-4 pl-7">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    SMTP 服务器
                  </label>
                  <input
                    type="text"
                    value={settings.smtpHost}
                    onChange={(e) =>
                      settings.updateSettings({ smtpHost: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    placeholder="smtp.example.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    端口
                  </label>
                  <input
                    type="number"
                    value={settings.smtpPort}
                    onChange={(e) =>
                      settings.updateSettings({
                        smtpPort: parseInt(e.target.value),
                      })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    placeholder="587"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    用户名
                  </label>
                  <input
                    type="text"
                    value={settings.smtpUser}
                    onChange={(e) =>
                      settings.updateSettings({ smtpUser: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    placeholder="noreply@xu-news.com"
                  />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 保存按钮 */}
        <div className="pt-6 border-t flex justify-end gap-3">
          <button
            onClick={() => settings.resetSettings()}
            className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            重置默认
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2"
          >
            <Save size={18} />
            保存设置
          </button>
        </div>
      </div>
    </div>
  );
}
