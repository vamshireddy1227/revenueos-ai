import React, { useState } from 'react';
import { ApiService } from '../services/api';
import { Bot, Send, Sparkles, User as UserIcon, ArrowRight } from 'lucide-react';

interface ChatMessage {
  sender: 'user' | 'ai';
  text: string;
  actions?: string[];
  context?: any;
}

export const AICopilot: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      sender: 'ai',
      text: "Hello! I am your Global AI Business Copilot for RevenueOS AI. Ask me about your leads, at-risk deals, churn signals, support tickets, or executive summaries.",
      actions: ["Which leads to contact today?", "Which deals are at risk?", "Show customer churn warnings"]
    }
  ]);

  const handleSend = async (textToSend?: string) => {
    const query = textToSend || prompt;
    if (!query.trim()) return;

    const userMsg: ChatMessage = { sender: 'user', text: query };
    setMessages((prev) => [...prev, userMsg]);
    setPrompt('');
    setLoading(true);

    try {
      const res = await ApiService.queryCopilot(query);
      const aiMsg: ChatMessage = {
        sender: 'ai',
        text: res.answer,
        actions: res.suggested_actions,
        context: res.context_used
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { sender: 'ai', text: `Sorry, I encountered an error: ${err.message}` }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto h-[calc(100vh-5rem)] flex flex-col justify-between">
      {/* Copilot Top Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-purple-600/20 border border-purple-500/40 flex items-center justify-center text-purple-400">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white">Global AI Business Copilot</h1>
            <p className="text-xs text-slate-400">Context-aware conversational assistant scoped to your tenant operations</p>
          </div>
        </div>
      </div>

      {/* Chat Messages Log */}
      <div className="flex-1 overflow-y-auto my-6 space-y-4 pr-2">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.sender === 'ai' && (
              <div className="w-8 h-8 rounded-lg bg-purple-600/20 border border-purple-500/30 flex items-center justify-center text-purple-400 shrink-0">
                <Bot className="w-4 h-4" />
              </div>
            )}

            <div className={`max-w-xl p-4 rounded-2xl text-xs leading-relaxed space-y-3 ${
              msg.sender === 'user'
                ? 'bg-blue-600 text-white font-medium rounded-tr-none'
                : 'glass-panel border border-slate-800 text-slate-200 rounded-tl-none'
            }`}>
              <p className="whitespace-pre-line">{msg.text}</p>

              {/* Action Buttons if AI */}
              {msg.actions && msg.actions.length > 0 && (
                <div className="pt-2 border-t border-slate-800/80 flex flex-wrap gap-2">
                  {msg.actions.map((act, aIdx) => (
                    <button
                      key={aIdx}
                      onClick={() => handleSend(act)}
                      className="px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-blue-400 text-[11px] font-semibold flex items-center gap-1"
                    >
                      {act} <ArrowRight className="w-3 h-3" />
                    </button>
                  ))}
                </div>
              )}
            </div>

            {msg.sender === 'user' && (
              <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shrink-0">
                <UserIcon className="w-4 h-4" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-3 items-center text-slate-400 text-xs italic">
            <Bot className="w-4 h-4 text-purple-400 animate-spin" /> Analyzing operational data...
          </div>
        )}
      </div>

      {/* Input Box */}
      <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex gap-3">
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Ask Copilot anything (e.g. Which deals should I focus on today?)..."
          className="flex-1 bg-slate-900 border border-slate-700/80 rounded-xl px-4 py-3 text-xs text-white focus:outline-none focus:border-purple-500 shadow-inner"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-5 py-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs flex items-center gap-2 shadow-lg shadow-purple-500/20"
        >
          <Send className="w-4 h-4" /> Send
        </button>
      </form>
    </div>
  );
};
