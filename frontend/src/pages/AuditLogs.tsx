import React, { useEffect, useState } from 'react';
import { ApiService } from '../services/api';
import { ShieldCheck, Lock } from 'lucide-react';

export const AuditLogs: React.FC = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadLogs() {
      try {
        const data = await ApiService.getAuditLogs();
        setLogs(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadLogs();
  }, []);

  if (loading) return <div className="p-8 text-slate-400">Loading Audit Logs...</div>;

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Audit & Security Compliance Logs</h1>
          <p className="text-xs text-slate-400 mt-1">Immutable security event history and tenant access auditing</p>
        </div>
      </div>

      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-900/80 text-slate-400 uppercase text-[10px] font-bold tracking-wider border-b border-slate-800">
            <tr>
              <th className="p-4">Timestamp</th>
              <th className="p-4">Action Event</th>
              <th className="p-4">User Email</th>
              <th className="p-4">Resource Type</th>
              <th className="p-4">IP Address</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {logs.map((l) => (
              <tr key={l.id} className="hover:bg-slate-900/50">
                <td className="p-4 text-slate-400 font-mono text-[11px]">{new Date(l.created_at).toLocaleString()}</td>
                <td className="p-4 font-bold text-blue-400">{l.action}</td>
                <td className="p-4 text-slate-200">{l.user_email || 'System'}</td>
                <td className="p-4 font-semibold text-slate-300">{l.resource_type}</td>
                <td className="p-4 text-slate-400 font-mono text-[11px]">{l.ip_address}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
