import { 
  LayoutDashboard, 
  MessageSquare, 
  Newspaper, 
  Upload, 
  BarChart3, 
  Settings,
  LogOut,
  Sparkles
} from 'lucide-react';

interface SidebarProps {
  activeMenu: string;
  onMenuChange: (menu: string) => void;
  onLogout: () => void;
}

const menuItems = [
  { id: 'dashboard', label: '仪表盘', icon: LayoutDashboard },
  { id: 'query', label: '智能问答', icon: MessageSquare },
  { id: 'news', label: '新闻管理', icon: Newspaper },
  { id: 'ingest', label: '数据入库', icon: Upload },
  { id: 'reports', label: '分析报告', icon: BarChart3 },
  { id: 'settings', label: '系统设置', icon: Settings },
];

export default function Sidebar({ activeMenu, onMenuChange, onLogout }: SidebarProps) {
  return (
    <aside className="w-64 bg-white border-r border-gray-100 min-h-screen flex flex-col">
      <div className="p-6 border-b border-gray-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-800">XU-News</h1>
            <p className="text-xs text-gray-500">AI-RAG 智能知识库</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              onClick={() => onMenuChange(item.id)}
              className={`sidebar-link ${activeMenu === item.id ? 'active' : ''}`}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="p-4 border-t border-gray-100">
        <button
          onClick={onLogout}
          className="sidebar-link hover:text-red-500 hover:bg-red-50"
        >
          <LogOut className="w-5 h-5" />
          <span>退出登录</span>
        </button>
      </div>
    </aside>
  );
}
