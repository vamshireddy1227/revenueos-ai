import React, { useEffect, useState } from 'react';
import { ApiService } from '../services/api';
import { CreditCard, Check, Zap } from 'lucide-react';

export const Billing: React.FC = () => {
  const [usage, setUsage] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await ApiService.getBillingUsage();
        setUsage(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) return <div className="p-8 text-slate-400">Loading Billing & Usage Metering...</div>;

  const aiPercent = Math.min(100, Math.round((usage.ai_requests_used / usage.ai_requests_limit) * 100));

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">SaaS Subscription & Usage Metering</h1>
          <p className="text-xs text-slate-400 mt-1">Tenant subscription plan management and operational quota tracking</p>
        </div>
      </div>

      {/* Active Plan & Metering Usage */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="glass-panel p-6 rounded-2xl border border-blue-500/30 bg-gradient-to-br from-slate-900 via-blue-950/20 to-slate-900 space-y-4">
          <span className="text-[10px] font-bold uppercase tracking-wider text-blue-400 px-2.5 py-1 rounded bg-blue-500/20 w-fit">Active Organization Plan</span>
          <h2 className="text-3xl font-extrabold text-white">{usage.plan_tier} Plan</h2>
          <p className="text-xl font-bold text-emerald-400">${usage.monthly_price} <span className="text-xs font-normal text-slate-400">/ month</span></p>
          <div className="pt-3 border-t border-slate-800 space-y-2 text-xs text-slate-300">
            <p className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400" /> Full Multi-Tenant Isolation</p>
            <p className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400" /> RAG Support Knowledge Base</p>
            <p className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400" /> ML Lead Scoring & Churn Engine</p>
          </div>
        </div>

        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
          <h3 className="text-sm font-bold text-white">Monthly Usage Quotas</h3>

          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span className="text-slate-300">AI Requests Metering</span>
                <span className="text-blue-400">{usage.ai_requests_used?.toLocaleString()} / {usage.ai_requests_limit?.toLocaleString()} ({aiPercent}%)</span>
              </div>
              <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                <div className="h-full bg-gradient-to-r from-blue-500 to-indigo-500" style={{ width: `${aiPercent}%` }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span className="text-slate-300">Document Storage Quota</span>
                <span className="text-purple-400">4.2 MB / {(usage.storage_bytes_limit / (1024*1024*1024)).toFixed(0)} GB</span>
              </div>
              <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                <div className="h-full bg-gradient-to-r from-purple-500 to-pink-500" style={{ width: '5%' }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span className="text-slate-300">Workflow Executions</span>
                <span className="text-emerald-400">{usage.workflow_runs_used} / {usage.workflow_runs_limit}</span>
              </div>
              <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                <div className="h-full bg-gradient-to-r from-emerald-500 to-teal-500" style={{ width: '8%' }} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
