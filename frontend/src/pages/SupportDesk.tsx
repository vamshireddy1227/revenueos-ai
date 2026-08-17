import React, { useEffect, useState } from 'react';
import { ApiService } from '../services/api';
import { LifeBuoy, Sparkles, BookOpen, AlertCircle, Plus, CheckCircle, Search } from 'lucide-react';

export const SupportDesk: React.FC = () => {
  const [tickets, setTickets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showRagModal, setShowRagModal] = useState(false);
  const [ragQuestion, setRagQuestion] = useState('');
  const [ragResult, setRagResult] = useState<any>(null);
  const [ragSearching, setRagSearching] = useState(false);

  const loadTickets = async () => {
    try {
      const data = await ApiService.getTickets();
      setTickets(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTickets();
  }, []);

  const handleRagSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ragQuestion.trim()) return;
    setRagSearching(true);
    try {
      const res = await ApiService.queryKnowledgeBase(ragQuestion);
      setRagResult(res);
    } catch (err: any) {
      alert(err.message || 'RAG search failed');
    } finally {
      setRagSearching(false);
    }
  };

  if (loading) return <div className="p-8 text-slate-400">Loading Support Desk...</div>;

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">AI Support Desk & Ticket Operations</h1>
          <p className="text-xs text-slate-400 mt-1">Automatic ticket intent detection, sentiment scoring, and RAG assistant</p>
        </div>
        <button
          onClick={() => setShowRagModal(true)}
          className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-purple-500/20"
        >
          <BookOpen className="w-4 h-4" /> Search Knowledge Base (RAG)
        </button>
      </div>

      {/* Ticket Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="p-4 border-b border-slate-800 bg-slate-900/40 flex items-center justify-between">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <LifeBuoy className="w-4 h-4 text-blue-400" /> Active Support Queue
          </h2>
          <span className="text-xs text-slate-400">Tickets are classified by AI upon intake</span>
        </div>

        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-900/80 text-slate-400 uppercase text-[10px] font-bold tracking-wider border-b border-slate-800">
            <tr>
              <th className="p-4">Ticket Code / Subject</th>
              <th className="p-4">AI Intent</th>
              <th className="p-4">Sentiment</th>
              <th className="p-4">Priority</th>
              <th className="p-4">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {tickets.map((t) => (
              <tr key={t.id} className="hover:bg-slate-900/50 transition-colors">
                <td className="p-4">
                  <span className="font-bold text-blue-400 mr-2">{t.ticket_code}</span>
                  <span className="font-semibold text-white">{t.subject}</span>
                  <p className="text-[11px] text-slate-400 mt-0.5 truncate max-w-md">{t.description}</p>
                </td>
                <td className="p-4">
                  <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-medium text-[10px]">
                    {t.intent}
                  </span>
                </td>
                <td className="p-4">
                  <span className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                    t.sentiment === 'Angry' ? 'bg-rose-500/20 text-rose-400' :
                    t.sentiment === 'Negative' ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'
                  }`}>
                    {t.sentiment}
                  </span>
                </td>
                <td className="p-4 font-semibold text-slate-200">
                  {t.priority}
                </td>
                <td className="p-4">
                  <span className="px-2.5 py-1 rounded-full bg-blue-500/10 text-blue-400 font-bold text-[10px]">
                    {t.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* RAG Knowledge Search Modal */}
      {showRagModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-panel p-6 rounded-2xl max-w-xl w-full border border-slate-800 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-purple-400" /> RAG Support Knowledge Search
              </h2>
              <button onClick={() => setShowRagModal(false)} className="text-slate-400 hover:text-white text-xs font-bold">Close</button>
            </div>

            <form onSubmit={handleRagSearch} className="flex gap-2">
              <input
                type="text"
                value={ragQuestion}
                onChange={(e) => setRagQuestion(e.target.value)}
                placeholder="Ask support policy or technical question..."
                className="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-4 py-2 text-xs text-white focus:outline-none focus:border-purple-500"
              />
              <button
                type="submit"
                disabled={ragSearching}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-xs font-semibold"
              >
                {ragSearching ? 'Searching...' : 'Search'}
              </button>
            </form>

            {ragResult && (
              <div className="p-4 rounded-xl bg-slate-950/80 border border-purple-500/30 space-y-3 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-purple-400">Grounded Answer:</span>
                  <span className="text-[10px] text-slate-400">Confidence: {(ragResult.confidence * 100).toFixed(0)}%</span>
                </div>
                <p className="text-slate-200 leading-relaxed whitespace-pre-line">{ragResult.answer}</p>
                {ragResult.sources?.length > 0 && (
                  <div className="pt-2 border-t border-slate-800 text-[10px] text-slate-400">
                    <span className="font-semibold text-slate-300">Cited Knowledge Sources:</span> {ragResult.sources.map((s: any) => s.doc_title).join(', ')}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
