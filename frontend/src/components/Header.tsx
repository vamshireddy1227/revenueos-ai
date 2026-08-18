import React from 'react';
import { Search, Bell, Shield, Building } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export const Header: React.FC = () => {
  const { user } = useAuth();

  return (
    <header className="h-16 border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-20">
      {/* Organization Badge & Search */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs font-semibold text-slate-200">
          <Building className="w-3.5 h-3.5 text-blue-400" />
          <span>Acme Enterprise Inc.</span>
        </div>

        <div className="relative w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search leads, deals, tickets, knowledge..."
            className="w-full bg-slate-950/60 border border-slate-800 text-xs text-white placeholder:text-slate-400 pl-9 pr-4 py-2 rounded-lg focus:outline-none focus:border-blue-500 transition-colors caret-white"
          />
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-4">
        {/* System Health Status */}
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-[11px] font-medium text-emerald-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span>AI Engine Operational</span>
        </div>

        {/* Notifications */}
        <button className="relative p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-blue-500" />
        </button>

        {/* Security Scope */}
        <div className="flex items-center gap-1.5 text-xs text-slate-400 bg-slate-800/40 px-2.5 py-1 rounded-md border border-slate-800">
          <Shield className="w-3.5 h-3.5 text-indigo-400" />
          <span>Tenant Isolated</span>
        </div>
      </div>
    </header>
  );
};
