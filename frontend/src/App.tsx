import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { SalesKanban } from './pages/SalesKanban';
import { Customers } from './pages/Customers';
import { SupportDesk } from './pages/SupportDesk';
import { AICopilot } from './pages/AICopilot';
import { KnowledgeBase } from './pages/KnowledgeBase';
import { Workflows } from './pages/Workflows';
import { Integrations } from './pages/Integrations';
import { AuditLogs } from './pages/AuditLogs';
import { Billing } from './pages/Billing';

const MainContent: React.FC = () => {
  const { user, loading } = useAuth();
  const [activeTab, setActiveTab] = useState<string>('dashboard');

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400 text-sm">
        Authenticating RevenueOS AI Session...
      </div>
    );
  }

  if (!user) {
    return <Login />;
  }

  const renderTab = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'sales':
        return <SalesKanban />;
      case 'customers':
        return <Customers />;
      case 'support':
        return <SupportDesk />;
      case 'copilot':
        return <AICopilot />;
      case 'knowledge':
        return <KnowledgeBase />;
      case 'workflows':
        return <Workflows />;
      case 'integrations':
        return <Integrations />;
      case 'audit':
        return <AuditLogs />;
      case 'billing':
        return <Billing />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="flex-1 overflow-y-auto">
          {renderTab()}
        </main>
      </div>
    </div>
  );
};

export function App() {
  return (
    <AuthProvider>
      <MainContent />
    </AuthProvider>
  );
}

export default App;
