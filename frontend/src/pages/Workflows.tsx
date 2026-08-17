import React, { useEffect, useState } from 'react';
import { ApiService } from '../services/api';
import { GitBranch, Play, CheckCircle } from 'lucide-react';

export const Workflows: React.FC = () => {
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await ApiService.getWorkflows();
        setWorkflows(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) return <div className="p-8 text-slate-400">Loading Workflows...</div>;

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Workflow Automation Engine</h1>
          <p className="text-xs text-slate-400 mt-1">Configurable trigger-action automated business routines</p>
        </div>
      </div>

      <div className="space-y-4">
        {workflows.map((wf) => (
          <div key={wf.id} className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-xl bg-blue-600/20 text-blue-400 border border-blue-500/30">
                <GitBranch className="w-5 h-5" />
              </div>
              <div>
                <h2 className="font-bold text-white text-sm">{wf.name}</h2>
                <p className="text-xs text-slate-400">{wf.description}</p>
                <div className="flex items-center gap-2 mt-2">
                  <span className="px-2 py-0.5 rounded bg-slate-800 text-blue-400 text-[10px] font-bold">
                    Trigger: {wf.trigger_event}
                  </span>
                  <span className="text-[10px] text-slate-500">• {wf.actions_json?.length || 0} Action Steps</span>
                </div>
              </div>
            </div>

            <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-bold border border-emerald-500/20 flex items-center gap-1">
              <CheckCircle className="w-3.5 h-3.5" /> Active
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
