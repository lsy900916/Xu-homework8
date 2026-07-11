import { useState } from 'react';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Query from './pages/Query';
import News from './pages/News';
import Ingest from './pages/Ingest';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import Sidebar from './components/Layout/Sidebar';

type Page = 'login' | 'register' | 'dashboard' | 'query' | 'news' | 'ingest' | 'reports' | 'settings';

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('login');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleLogin = () => {
    setIsAuthenticated(true);
    setCurrentPage('dashboard');
  };

  const handleRegister = () => {
    setIsAuthenticated(true);
    setCurrentPage('dashboard');
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentPage('login');
  };

  const handleMenuChange = (menu: string) => {
    setCurrentPage(menu as Page);
  };

  if (!isAuthenticated) {
    if (currentPage === 'register') {
      return <Register onRegister={handleRegister} onLogin={() => setCurrentPage('login')} />;
    }
    return <Login onLogin={handleLogin} onRegister={() => setCurrentPage('register')} />;
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'query':
        return <Query />;
      case 'news':
        return <News />;
      case 'ingest':
        return <Ingest />;
      case 'reports':
        return <Reports />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar 
        activeMenu={currentPage} 
        onMenuChange={handleMenuChange}
        onLogout={handleLogout}
      />
      <div className="flex-1 flex flex-col min-h-screen">
        {renderPage()}
      </div>
    </div>
  );
}
