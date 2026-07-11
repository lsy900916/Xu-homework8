import { useState } from "react";
import {
  Settings as SettingsIcon,
  User,
  Bell,
  Database,
  Shield,
  Save,
  RefreshCw,
} from "lucide-react";
import { Header } from "../components/Layout/Header";

export default function Settings() {
  const [activeSection, setActiveSection] = useState("profile");
  const [email, setEmail] = useState("admin@xu-news.com");
  const [name, setName] = useState("管理员");
  const [smtpHost, setSmtpHost] = useState("smtp.example.com");
  const [smtpPort, setSmtpPort] = useState("587");
  const [smtpUser, setSmtpUser] = useState("noreply@xu-news.com");
  const [smtpPass, setSmtpPass] = useState("********");
  const [ollamaHost, setOllamaHost] = useState("http://localhost:11434");
  const [embeddingModel, setEmbeddingModel] = useState("all-MiniLM-L6-v2");
  const [llmModel, setLlmModel] = useState("qwen2.5:3b");

  const sections = [
    { id: "profile", label: "个人信息", icon: User },
    { id: "notification", label: "通知设置", icon: Bell },
    { id: "system", label: "系统配置", icon: Database },
    { id: "security", label: "安全设置", icon: Shield },
  ];

  const handleSave = () => {
    alert("设置已保存！");
  };

  return (
    <div className="flex-1 flex flex-col">
      <Header title="系统设置" subtitle="管理系统配置和个人信息" />

      <main className="flex-1 p-6 overflow-auto">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-1">
            <div className="card">
              <div className="p-4">
                <h3 className="text-sm font-semibold text-gray-500 uppercase mb-4">
                  设置菜单
                </h3>
                <nav className="space-y-1">
                  {sections.map((section) => {
                    const Icon = section.icon;
                    return (
                      <button
                        key={section.id}
                        onClick={() => setActiveSection(section.id)}
                        className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                          activeSection === section.id
                            ? "bg-primary-50 text-primary-600 font-medium"
                            : "text-gray-600 hover:bg-gray-50"
                        }`}
                      >
                        <Icon className="w-5 h-5" />
                        <span>{section.label}</span>
                      </button>
                    );
                  })}
                </nav>
              </div>
            </div>
          </div>

          <div className="lg:col-span-3">
            <div className="card">
              <div className="card-header flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {sections.find((s) => s.id === activeSection) &&
                    (() => {
                      const Icon = sections.find(
                        (s) => s.id === activeSection,
                      )!.icon;
                      return <Icon className="w-5 h-5 text-gray-500" />;
                    })()}
                  <h3 className="font-semibold text-gray-800">
                    {sections.find((s) => s.id === activeSection)?.label}
                  </h3>
                </div>
                <div className="flex items-center gap-2">
                  <button className="btn-secondary flex items-center gap-2">
                    <RefreshCw className="w-4 h-4" />
                    重置
                  </button>
                  <button
                    onClick={handleSave}
                    className="btn-primary flex items-center gap-2"
                  >
                    <Save className="w-4 h-4" />
                    保存设置
                  </button>
                </div>
              </div>
              <div className="card-body">
                {activeSection === "profile" && (
                  <div className="space-y-6">
                    <div className="flex items-center gap-6">
                      <div className="w-20 h-20 bg-gradient-to-br from-primary-400 to-secondary-400 rounded-full flex items-center justify-center">
                        <User className="w-10 h-10 text-white" />
                      </div>
                      <div>
                        <p className="text-lg font-semibold text-gray-800">
                          {name}
                        </p>
                        <p className="text-gray-500">{email}</p>
                        <button className="mt-2 text-sm text-primary-500 hover:text-primary-600">
                          更换头像
                        </button>
                      </div>
                    </div>
                    <div className="border-t border-gray-100 pt-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            用户名
                          </label>
                          <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            className="input-field"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            邮箱地址
                          </label>
                          <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="input-field"
                          />
                        </div>
                      </div>
                      <div className="mt-6">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          修改密码
                        </label>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <input
                            type="password"
                            placeholder="当前密码"
                            className="input-field"
                          />
                          <input
                            type="password"
                            placeholder="新密码"
                            className="input-field"
                          />
                          <input
                            type="password"
                            placeholder="确认新密码"
                            className="input-field"
                          />
                        </div>
                        <button className="mt-3 text-sm text-primary-500 hover:text-primary-600">
                          忘记密码?
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {activeSection === "notification" && (
                  <div className="space-y-6">
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                      <div>
                        <p className="font-medium text-gray-800">邮件通知</p>
                        <p className="text-sm text-gray-500">
                          接收系统通知和报告邮件
                        </p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          defaultChecked
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-500"></div>
                      </label>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                      <div>
                        <p className="font-medium text-gray-800">入库通知</p>
                        <p className="text-sm text-gray-500">
                          新闻入库成功时发送通知
                        </p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          defaultChecked
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-500"></div>
                      </label>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                      <div>
                        <p className="font-medium text-gray-800">异常告警</p>
                        <p className="text-sm text-gray-500">
                          系统异常时发送告警邮件
                        </p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          defaultChecked
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-500"></div>
                      </label>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                      <div>
                        <p className="font-medium text-gray-800">日报推送</p>
                        <p className="text-sm text-gray-500">
                          每日发送新闻分析日报
                        </p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" className="sr-only peer" />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-500"></div>
                      </label>
                    </div>
                  </div>
                )}

                {activeSection === "system" && (
                  <div className="space-y-6">
                    <div>
                      <h4 className="text-sm font-semibold text-gray-700 mb-4">
                        LLM 配置
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Ollama 地址
                          </label>
                          <input
                            type="text"
                            value={ollamaHost}
                            onChange={(e) => setOllamaHost(e.target.value)}
                            className="input-field"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            LLM 模型
                          </label>
                          <select
                            value={llmModel}
                            onChange={(e) => setLlmModel(e.target.value)}
                            className="input-field"
                          >
                            <option value="qwen2.5:3b">qwen2.5:3b</option>
                            <option value="qwen3.5:0.8b">qwen3.5:0.8b</option>
                            <option value="llama3.1:8b">llama3.1:8b</option>
                          </select>
                        </div>
                      </div>
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-gray-700 mb-4">
                        Embedding 配置
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Embedding 模型
                          </label>
                          <select
                            value={embeddingModel}
                            onChange={(e) => setEmbeddingModel(e.target.value)}
                            className="input-field"
                          >
                            <option value="all-MiniLM-L6-v2">
                              all-MiniLM-L6-v2 (384维)
                            </option>
                            <option value="mxbai-embed-large">
                              mxbai-embed-large (1024维)
                            </option>
                            <option value="bge-large-zh">
                              bge-large-zh (1024维)
                            </option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            向量维度
                          </label>
                          <input
                            type="text"
                            value="384"
                            disabled
                            className="input-field bg-gray-100"
                          />
                        </div>
                      </div>
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-gray-700 mb-4">
                        邮件服务配置
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            SMTP 主机
                          </label>
                          <input
                            type="text"
                            value={smtpHost}
                            onChange={(e) => setSmtpHost(e.target.value)}
                            className="input-field"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            SMTP 端口
                          </label>
                          <input
                            type="text"
                            value={smtpPort}
                            onChange={(e) => setSmtpPort(e.target.value)}
                            className="input-field"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            SMTP 用户
                          </label>
                          <input
                            type="text"
                            value={smtpUser}
                            onChange={(e) => setSmtpUser(e.target.value)}
                            className="input-field"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            SMTP 密码
                          </label>
                          <input
                            type="password"
                            value={smtpPass}
                            onChange={(e) => setSmtpPass(e.target.value)}
                            className="input-field"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {activeSection === "security" && (
                  <div className="space-y-6">
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                      <div>
                        <p className="font-medium text-gray-800">账户锁定</p>
                        <p className="text-sm text-gray-500">
                          登录失败5次后锁定账户15分钟
                        </p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          defaultChecked
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-500"></div>
                      </label>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                      <div>
                        <p className="font-medium text-gray-800">密码过期</p>
                        <p className="text-sm text-gray-500">
                          密码每90天自动过期
                        </p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          defaultChecked
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-500"></div>
                      </label>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                      <div>
                        <p className="font-medium text-gray-800">API 限流</p>
                        <p className="text-sm text-gray-500">
                          限制每个用户每分钟100次请求
                        </p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          defaultChecked
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-500"></div>
                      </label>
                    </div>
                    <div className="p-4 bg-blue-50 rounded-xl">
                      <div className="flex items-start gap-3">
                        <Shield className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="font-medium text-blue-800">安全提示</p>
                          <p className="text-sm text-blue-600 mt-1">
                            建议定期更换密码，并启用双因素认证以提高账户安全性。
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
