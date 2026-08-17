import React, { useEffect, useState } from 'react';
import { ApiService } from '../services/api';
import { Users, ShieldAlert, TrendingUp, Heart, CheckCircle2, AlertTriangle, ChevronRight, X } from 'lucide-react';

export const Customers: React.FC = () => {
  const [customers, setCustomers] = useState<any[]>([]);
  const [selectedCust360, setSelectedCust360] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await ApiService.getCustomers();
        setCustomers(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const openCustomer360 = async (id: string) => {
    try {
      const data360 = await ApiService.getCustomer360(id);
      setSelectedCust360(data360);
    } catch (err) {
      alert('Failed to load Customer 360');
    }
  };

  if (loading) return <div className="p-8 text-slate-400">Loading Customer Intelligence...</div>;

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Customer 360 & Churn Intelligence</h1>
          <p className="text-xs text-slate-400 mt-1">Single-pane operational view, health scoring engine, and churn mitigation</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
            <Heart className="w-3.5 h-3.5" />
            <span>Avg Health: 78 / 100</span>
          </div>
        </div>
      </div>

      {/* Customer Directory Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="p-4 border-b border-slate-800 bg-slate-900/40 flex items-center justify-between">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <Users className="w-4 h-4 text-blue-400" /> Active Accounts Directory
          </h2>
          <span className="text-xs text-slate-400">Click any customer row to open Customer 360 View</span>
        </div>

        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-900/80 text-slate-400 uppercase text-[10px] font-bold tracking-wider border-b border-slate-800">
            <tr>
              <th className="p-4">Customer Name</th>
              <th className="p-4">Subscription Plan</th>
              <th className="p-4">MRR / ARR</th>
              <th className="p-4">Health Status</th>
              <th className="p-4">Churn Risk</th>
              <th className="p-4 text-right">Customer 360</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {customers.map((c) => (
              <tr
                key={c.id}
                onClick={() => openCustomer360(c.id)}
                className="hover:bg-slate-900/60 cursor-pointer transition-colors"
              >
                <td className="p-4">
                  <p className="font-semibold text-white">{c.name}</p>
                  <p className="text-[11px] text-slate-400">{c.email} • {c.industry}</p>
                </td>
                <td className="p-4 font-semibold text-slate-200">
                  {c.subscription_plan}
                </td>
                <td className="p-4">
                  <p className="font-bold text-white">${c.mrr?.toLocaleString()} /mo</p>
                  <p className="text-[11px] text-slate-400">${c.arr?.toLocaleString()} /yr</p>
                </td>
                <td className="p-4">
                  <span className={`px-2.5 py-1 rounded-full font-bold text-[11px] border flex items-center gap-1 w-fit ${
                    c.health_status === 'Healthy'
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      : c.health_status === 'At Risk'
                      ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                      : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                  }`}>
                    {c.health_status === 'Healthy' ? <CheckCircle2 className="w-3 h-3" /> : <AlertTriangle className="w-3 h-3" />}
                    {c.health_status} ({c.health_score})
                  </span>
                </td>
                <td className="p-4 font-semibold text-slate-200">
                  {(c.churn_risk_score * 100).toFixed(0)}% Risk
                </td>
                <td className="p-4 text-right text-blue-400 font-semibold flex items-center justify-end gap-1">
                  View 360 <ChevronRight className="w-4 h-4" />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Customer 360 Drawer Modal */}
      {selectedCust360 && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-md z-50 flex justify-end">
          <div className="w-full max-w-2xl bg-slate-900 border-l border-slate-800 h-full overflow-y-auto p-6 space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div>
                <h2 className="text-xl font-bold text-white">{selectedCust360.profile.name}</h2>
                <p className="text-xs text-slate-400">{selectedCust360.profile.email} • {selectedCust360.profile.industry}</p>
              </div>
              <button
                onClick={() => setSelectedCust360(null)}
                className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Commercial Overview */}
            <div className="grid grid-cols-3 gap-4">
              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
                <span className="text-[10px] font-bold uppercase text-slate-400">Plan Tier</span>
                <p className="text-base font-bold text-white mt-1">{selectedCust360.commercial.subscription_plan}</p>
              </div>
              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
                <span className="text-[10px] font-bold uppercase text-slate-400">MRR</span>
                <p className="text-base font-bold text-blue-400 mt-1">${selectedCust360.commercial.mrr?.toLocaleString()}</p>
              </div>
              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
                <span className="text-[10px] font-bold uppercase text-slate-400">ARR</span>
                <p className="text-base font-bold text-emerald-400 mt-1">${selectedCust360.commercial.arr?.toLocaleString()}</p>
              </div>
            </div>

            {/* Health & Churn Risk */}
            <div className="p-5 rounded-2xl glass-panel border border-slate-800 space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">Health & Risk Analysis</h3>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-extrabold text-white">{selectedCust360.intelligence.health_score} <span className="text-xs font-normal text-slate-400">/ 100</span></p>
                  <p className="text-xs text-slate-400">Status: <span className="font-semibold text-amber-400">{selectedCust360.intelligence.health_status}</span></p>
                </div>
                <div className="text-right">
                  <p className="text-xl font-bold text-rose-400">{(selectedCust360.intelligence.churn_risk_score * 100).toFixed(0)}%</p>
                  <p className="text-xs text-slate-400">Churn Probability</p>
                </div>
              </div>

              <div className="pt-2">
                <h4 className="text-[11px] font-semibold text-slate-400 mb-1.5">Identified Risk Factors:</h4>
                <ul className="space-y-1 text-xs text-slate-300">
                  {selectedCust360.intelligence.risk_factors.map((rf: string, idx: number) => (
                    <li key={idx} className="p-2 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-200">• {rf}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Upsell Opportunity */}
            {selectedCust360.intelligence.upsell_opportunity?.has_opportunity && (
              <div className="p-5 rounded-2xl bg-gradient-to-r from-purple-950/40 to-slate-900 border border-purple-500/30 space-y-2">
                <div className="flex items-center gap-2 text-purple-400 text-xs font-bold uppercase">
                  <TrendingUp className="w-4 h-4" /> Upsell Expansion Recommendation
                </div>
                <p className="text-xs text-slate-200">{selectedCust360.intelligence.upsell_opportunity.reasoning}</p>
                <p className="text-xs font-bold text-emerald-400">
                  Est. Expansion MRR: +${selectedCust360.intelligence.upsell_opportunity.estimated_expansion_mrr?.toLocaleString()} /mo
                </p>
              </div>
            )}

            {/* Support Ticket History */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">Recent Support Ticket Events</h3>
              {selectedCust360.support_summary.recent_tickets.map((t: any) => (
                <div key={t.id} className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-xs flex items-center justify-between">
                  <div>
                    <span className="font-bold text-blue-400">{t.code}:</span> <span className="text-slate-200 font-semibold">{t.subject}</span>
                    <p className="text-[11px] text-slate-400 mt-0.5">Priority: {t.priority} • Sentiment: {t.sentiment}</p>
                  </div>
                  <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px] font-semibold">{t.status}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
