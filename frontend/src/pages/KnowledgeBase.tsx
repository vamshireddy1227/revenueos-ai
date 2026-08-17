import React, { useEffect, useState } from 'react';
import { ApiService } from '../services/api';
import { BookOpen, Plus, FileText, CheckCircle } from 'lucide-react';

export const KnowledgeBase: React.FC = () => {
  const [docs, setDocs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  const loadDocs = async () => {
    try {
      const data = await ApiService.getDocuments();
      setDocs(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const handleAddDoc = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !content) return;
    try {
      await ApiService.createDocument(title, content);
      setTitle('');
      setContent('');
      loadDocs();
    } catch (err: any) {
      alert(err.message || 'Failed to add document');
    }
  };

  if (loading) return <div className="p-8 text-slate-400">Loading Knowledge Base...</div>;

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Knowledge Base & RAG Indexing</h1>
          <p className="text-xs text-slate-400 mt-1">Tenant-isolated vector search document store</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Document Ingestion Form */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <Plus className="w-4 h-4 text-blue-400" /> Ingest Knowledge Document
          </h2>
          <form onSubmit={handleAddDoc} className="space-y-3 text-xs">
            <div>
              <label className="block text-slate-300 font-semibold mb-1">Document Title</label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Enterprise SLA & Refund Policy"
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-semibold mb-1">Raw Document Content</label>
              <textarea
                required
                rows={6}
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Paste policy or product technical documentation..."
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white"
              />
            </div>
            <button
              type="submit"
              className="w-full py-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg text-xs"
            >
              Process & Index Embeddings
            </button>
          </form>
        </div>

        {/* Documents Directory */}
        <div className="lg:col-span-2 glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-purple-400" /> Indexed Knowledge Documents
          </h2>
          <div className="space-y-3">
            {docs.map((d) => (
              <div key={d.id} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-purple-400" />
                  <div>
                    <h3 className="font-bold text-white text-xs">{d.title}</h3>
                    <p className="text-[11px] text-slate-400">{d.chunk_count} Chunks Indexed • {d.file_type.toUpperCase()}</p>
                  </div>
                </div>
                <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] font-bold border border-emerald-500/20 flex items-center gap-1">
                  <CheckCircle className="w-3 h-3" /> Indexed
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
