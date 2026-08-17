import React, { useEffect, useState } from 'react';
import { ApiService } from '../services/api';
import { DollarSign, TrendingUp, Users, AlertTriangle, Sparkles, Activity, CheckCircle } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const [insights, setInsights] = useState<any>(null);
  const [forecast, setForecast] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [insData, fcData] = await Promise.all([
          ApiService.getExecutiveInsights(),
          ApiService.getDealForecast()
        ]);
        setInsights(insData);
        setForecast(fcData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return <div className="p-8 text-slate-400 text-sm">Loading Executive Intelligence...</div>;
  }

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Top Welcome Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Executive Revenue Intelligence</h1>
          <p className="text-xs text-slate-400 mt-1">Real-time revenue metrics, forecasting, and AI executive insights</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-500/10 border border-blue-500/20 text-xs font-semibold text-blue-400">
          <Sparkles className="w-4 h-4" />
          <span>Generative AI Engine Active</span>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="glass-panel p-5 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Pipeline</span>
            <DollarSign className="w-4 h-4 text-blue-400" />
          </div>
          <p className="text-2xl font-bold text-white">${forecast?.total_pipeline_value?.toLocaleString() || '0'}</p>
          <p className="text-xs text-slate-400 mt-1">Weighted: <span className="text-blue-400 font-semibold">${forecast?.weighted_pipeline_value?.toLocaleString() || '0'}</span></p>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Won Revenue</span>
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold text-white">${forecast?.won_revenue?.toLocaleString() || '0'}</p>
          <p className="text-xs text-emerald-400 mt-1 font-medium">Conversion Rate: {forecast?.conversion_rate}%</p>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Average Deal Size</span>
            <Activity className="w-4 h-4 text-purple-400" />
          </div>
          <p className="text-2xl font-bold text-white">${forecast?.avg_deal_size?.toLocaleString() || '0'}</p>
          <p className="text-xs text-slate-400 mt-1">Active Deals: <span className="text-white font-semibold">{forecast?.active_deals_count}</span></p>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Customer Health</span>
            <Users className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold text-emerald-400">82.4 <span className="text-xs font-normal text-slate-400">/ 100</span></p>
          <p className="text-xs text-slate-400 mt-1">2 Accounts flagged at risk</p>
        </div>
      </div>

      {/* AI Executive Insights Card */}
      <div className="glass-panel p-6 rounded-2xl border border-indigo-500/30 bg-gradient-to-br from-slate-900 via-indigo-950/20 to-slate-900 shadow-xl">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 rounded-lg bg-indigo-500/20 border border-indigo-500/40 text-indigo-400">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">AI Executive Intelligence Summary</h2>
            <p className="text-xs text-slate-400">Computed live from current database sales, support, and churn metrics</p>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 text-sm text-slate-200 leading-relaxed mb-6">
          {insights?.summary}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* Highlights */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
              <CheckCircle className="w-3.5 h-3.5" /> Performance Highlights
            </h3>
            <ul className="space-y-1.5 text-xs text-slate-300">
              {insights?.highlights?.map((h: string, idx: number) => (
                <li key={idx} className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80">• {h}</li>
              ))}
            </ul>
          </div>

          {/* Operational Risks */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5" /> Key Risks
            </h3>
            <ul className="space-y-1.5 text-xs text-slate-300">
              {insights?.risks?.map((r: string, idx: number) => (
                <li key={idx} className="p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-200">• {r}</li>
              ))}
            </ul>
          </div>

          {/* Action Items */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold text-blue-400 uppercase tracking-wider flex items-center gap-1.5">
              <TrendingUp className="w-3.5 h-3.5" /> Recommended Priorities
            </h3>
            <ul className="space-y-1.5 text-xs text-slate-300">
              {insights?.action_items?.map((a: string, idx: number) => (
                <li key={idx} className="p-2.5 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-200">• {a}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
