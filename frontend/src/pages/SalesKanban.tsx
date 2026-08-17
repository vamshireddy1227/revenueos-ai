import React, { useEffect, useState } from 'react';
import { ApiService } from '../services/api';
import { Plus, RefreshCw, Sparkles, Filter, Search, ChevronRight } from 'lucide-react';

const STAGES = ["New Lead", "Qualified", "Discovery", "Proposal", "Negotiation", "Won"];

export const SalesKanban: React.FC = () => {
  const [leads, setLeads] = useState<any[]>([]);
  const [deals, setDeals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState<'kanban' | 'leads'>('leads');
  const [showAddModal, setShowAddModal] = useState(false);
  const [newLead, setNewLead] = useState({ name: '', email: '', company_name: '', deal_value: 25000, industry: 'Technology', company_size: '51-200' });

  const loadData = async () => {
    try {
      const [lData, dData] = await Promise.all([
        ApiService.getLeads(),
        ApiService.getDeals()
      ]);
      setLeads(lData);
      setDeals(dData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRescore = async (leadId: string) => {
    try {
      await ApiService.rescoreLead(leadId);
      loadData();
    } catch (err) {
      alert('Rescore failed');
    }
  };

  const handleCreateLead = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await ApiService.createLead(newLead);
      setShowAddModal(false);
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to create lead');
    }
  };

  if (loading) return <div className="p-8 text-slate-400">Loading Sales Intelligence...</div>;

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Header & Controls */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">AI Sales Intelligence & Pipeline</h1>
          <p className="text-xs text-slate-400 mt-1">Lead scoring engine, conversion predictions, and interactive deal pipeline</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex bg-slate-900 p-1 rounded-xl border border-slate-800 text-xs">
            <button
              onClick={() => setActiveView('leads')}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                activeView === 'leads' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Lead Scoring Table ({leads.length})
            </button>
            <button
              onClick={() => setActiveView('kanban')}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                activeView === 'kanban' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Deal Kanban ({deals.length})
            </button>
          </div>

          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-blue-500/20"
          >
            <Plus className="w-4 h-4" /> Add Lead
          </button>
        </div>
      </div>

      {/* View Switcher: Lead Table vs Kanban */}
      {activeView === 'leads' ? (
        <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/40">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-blue-400" /> AI Scored Prospect Pipeline
            </h2>
            <span className="text-xs text-slate-400">Scored dynamically via company size, industry & engagement history</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900/80 text-slate-400 uppercase text-[10px] font-bold tracking-wider border-b border-slate-800">
                <tr>
                  <th className="p-4">Prospect / Company</th>
                  <th className="p-4">AI Score</th>
                  <th className="p-4">Conv. Prob.</th>
                  <th className="p-4">Est. Deal Value</th>
                  <th className="p-4">AI Recommended Action</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {leads.map((lead) => (
                  <tr key={lead.id} className="hover:bg-slate-900/50 transition-colors">
                    <td className="p-4">
                      <p className="font-semibold text-white">{lead.name}</p>
                      <p className="text-[11px] text-slate-400">{lead.company_name} • {lead.industry}</p>
                    </td>
                    <td className="p-4">
                      <span className={`px-2.5 py-1 rounded-full font-bold text-[11px] border ${
                        lead.score >= 75
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                          : lead.score >= 50
                          ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                          : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                      }`}>
                        {lead.score} / 100
                      </span>
                    </td>
                    <td className="p-4 font-semibold text-slate-200">
                      {(lead.conversion_prob * 100).toFixed(0)}%
                    </td>
                    <td className="p-4 font-semibold text-white">
                      ${lead.deal_value?.toLocaleString()}
                    </td>
                    <td className="p-4 max-w-xs text-[11px] text-slate-300">
                      {lead.recommended_action || 'No recommendation'}
                    </td>
                    <td className="p-4 text-right">
                      <button
                        onClick={() => handleRescore(lead.id)}
                        className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-blue-400 text-[11px] font-medium flex items-center gap-1 ml-auto"
                      >
                        <RefreshCw className="w-3 h-3" /> Rescore
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        /* Kanban Board */
        <div className="flex gap-4 overflow-x-auto pb-6">
          {STAGES.map((stage) => {
            const stageDeals = deals.filter((d) => d.stage === stage);
            const stageTotal = stageDeals.reduce((sum, d) => sum + d.value, 0);

            return (
              <div key={stage} className="kanban-col p-4 flex flex-col justify-between shrink-0 w-72">
                <div>
                  <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800">
                    <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">{stage}</h3>
                    <span className="px-2 py-0.5 rounded-full bg-slate-800 text-[10px] font-bold text-slate-300">
                      {stageDeals.length}
                    </span>
                  </div>
                  <p className="text-xs font-semibold text-blue-400 mb-3">${stageTotal.toLocaleString()}</p>

                  <div className="space-y-3">
                    {stageDeals.map((deal) => (
                      <div key={deal.id} className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-slate-700 transition-all shadow-md">
                        <h4 className="text-xs font-bold text-white mb-1">{deal.name}</h4>
                        <p className="text-sm font-extrabold text-emerald-400 mb-2">${deal.value?.toLocaleString()}</p>
                        <div className="flex items-center justify-between text-[10px] text-slate-400 pt-2 border-t border-slate-800/80">
                          <span>Prob: {(deal.probability * 100).toFixed(0)}%</span>
                          <span className={`px-1.5 py-0.5 rounded font-bold ${
                            deal.risk_level === 'High' ? 'bg-rose-500/20 text-rose-400' : 'bg-emerald-500/20 text-emerald-400'
                          }`}>
                            {deal.risk_level} Risk
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Add Lead Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-panel p-6 rounded-2xl max-w-md w-full border border-slate-800 space-y-4">
            <h2 className="text-lg font-bold text-white">Add New Prospect Lead</h2>
            <form onSubmit={handleCreateLead} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Contact Name</label>
                <input
                  type="text"
                  required
                  value={newLead.name}
                  onChange={(e) => setNewLead({ ...newLead, name: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white"
                />
              </div>
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Work Email</label>
                <input
                  type="email"
                  required
                  value={newLead.email}
                  onChange={(e) => setNewLead({ ...newLead, email: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white"
                />
              </div>
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Company Name</label>
                <input
                  type="text"
                  required
                  value={newLead.company_name}
                  onChange={(e) => setNewLead({ ...newLead, company_name: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Est. Deal Value ($)</label>
                  <input
                    type="number"
                    value={newLead.deal_value}
                    onChange={(e) => setNewLead({ ...newLead, deal_value: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Company Size</label>
                  <select
                    value={newLead.company_size}
                    onChange={(e) => setNewLead({ ...newLead, company_size: e.target.value })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white"
                  >
                    <option value="11-50">11-50</option>
                    <option value="51-200">51-200</option>
                    <option value="201-1000">201-1000</option>
                    <option value="1000+">1000+</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold shadow-lg shadow-blue-500/20"
                >
                  Save & Score Lead
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
