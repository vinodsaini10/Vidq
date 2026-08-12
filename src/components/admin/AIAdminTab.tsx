import React, { useState, useEffect } from 'react';
import { Cpu, Zap, Sparkles, Play, CheckCircle2, AlertTriangle, RefreshCw, Layers } from 'lucide-react';
import { useAppState } from '../../store/useStore';
import { GlassCard } from '../common/GlassCard';

export const AIAdminTab: React.FC = () => {
  const { showToast } = useAppState();
  const [providers, setProviders] = useState<any[]>([]);
  const [models, setModels] = useState<any[]>([]);
  const [prompts, setPrompts] = useState<any[]>([]);
  const [activeSubTab, setActiveSubTab] = useState<'providers' | 'models' | 'playground'>('providers');

  // Playground state
  const [selectedModel, setSelectedModel] = useState('gemini-flash');
  const [testPromptInput, setTestPromptInput] = useState('Generate 5 high-CTR YouTube video titles about AI automation.');
  const [testOutput, setTestOutput] = useState<any | null>(null);
  const [testLoading, setTestLoading] = useState(false);

  useEffect(() => {
    fetchAIConfig();
  }, []);

  const fetchAIConfig = async () => {
    try {
      const token = localStorage.getItem('token');
      const [provRes, modRes, prmRes] = await Promise.all([
        fetch('/api/v1/admin/ai/providers', { headers: { Authorization: `Bearer ${token}` } }),
        fetch('/api/v1/admin/ai/models', { headers: { Authorization: `Bearer ${token}` } }),
        fetch('/api/v1/admin/ai/prompts', { headers: { Authorization: `Bearer ${token}` } })
      ]);

      if (provRes.ok) {
        const pData = await provRes.json();
        setProviders(pData.providers || []);
      }
      if (modRes.ok) {
        const mData = await modRes.json();
        setModels(mData.models || []);
      }
      if (prmRes.ok) {
        const prData = await prmRes.json();
        setPrompts(prData || []);
      }
    } catch (e) {
      console.error("Error fetching AI config", e);
    }
  };

  const handleRunTestPrompt = async () => {
    setTestLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/v1/admin/ai/prompts/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ model: selectedModel, user_input: testPromptInput })
      });
      if (res.ok) {
        const data = await res.json();
        setTestOutput(data);
        showToast('Playground test execution complete.');
      }
    } catch (e) {
      showToast('Error running prompt test.');
    } finally {
      setTestLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Sub-tab navigation */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveSubTab('providers')}
          className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
            activeSubTab === 'providers' ? 'bg-purple-600 text-white shadow' : 'text-slate-400 hover:text-white'
          }`}
        >
          AI Providers & Keys
        </button>
        <button
          onClick={() => setActiveSubTab('models')}
          className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
            activeSubTab === 'models' ? 'bg-purple-600 text-white shadow' : 'text-slate-400 hover:text-white'
          }`}
        >
          Model Registry & Costs
        </button>
        <button
          onClick={() => setActiveSubTab('playground')}
          className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
            activeSubTab === 'playground' ? 'bg-purple-600 text-white shadow' : 'text-slate-400 hover:text-white'
          }`}
        >
          Prompt Playground & Testing
        </button>
      </div>

      {/* Providers Subtab */}
      {activeSubTab === 'providers' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {providers.map((p) => (
            <GlassCard key={p.provider_id} className="p-6 space-y-4 border-slate-800">
              <div className="flex items-center justify-between">
                <span className="text-sm font-black text-white">{p.name}</span>
                <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold text-[10px] uppercase">
                  {p.status}
                </span>
              </div>
              <p className="text-xs text-slate-400">{p.description || 'Configured LLM inference backend.'}</p>
              <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-xs">
                <span className="text-slate-500 font-bold">Latency</span>
                <span className="text-cyan-400 font-extrabold">{p.latency_ms || 140}ms</span>
              </div>
            </GlassCard>
          ))}
        </div>
      )}

      {/* Models Subtab */}
      {activeSubTab === 'models' && (
        <GlassCard className="p-6 space-y-4">
          <h3 className="text-base font-extrabold text-white">Configured Model Registry</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase font-black">
                  <th className="pb-3">Model Alias</th>
                  <th className="pb-3">Provider</th>
                  <th className="pb-3">Context Window</th>
                  <th className="pb-3">Input Price / 1M</th>
                  <th className="pb-3">Output Price / 1M</th>
                  <th className="pb-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {models.map((m) => (
                  <tr key={m.model_alias}>
                    <td className="py-3 font-bold text-white">{m.model_alias}</td>
                    <td className="py-3 text-purple-400 font-extrabold">{m.provider}</td>
                    <td className="py-3 text-slate-300">{m.context_window?.toLocaleString()} tokens</td>
                    <td className="py-3 text-amber-400">${m.cost_per_1m_input_usd}</td>
                    <td className="py-3 text-amber-400">${m.cost_per_1m_output_usd}</td>
                    <td className="py-3">
                      <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 text-[10px] font-bold">
                        ACTIVE
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>
      )}

      {/* Playground Subtab */}
      {activeSubTab === 'playground' && (
        <GlassCard className="p-6 space-y-4">
          <h3 className="text-base font-extrabold text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-400" /> Prompt Playground & Token Cost Estimator
          </h3>

          <div className="space-y-3">
            <div className="flex items-center gap-4">
              <label className="text-xs font-bold text-slate-400">Select Model:</label>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-white font-bold"
              >
                <option value="gemini-flash">Gemini 1.5 Flash (Fast & Cheap)</option>
                <option value="gemini-pro">Gemini 1.5 Pro (High Reasoning)</option>
                <option value="gpt-4o">GPT-4o (OpenAI)</option>
                <option value="llama3">Ollama Llama 3 (Local GPU)</option>
              </select>
            </div>

            <textarea
              rows={4}
              value={testPromptInput}
              onChange={(e) => setTestPromptInput(e.target.value)}
              placeholder="Enter test prompt here..."
              className="w-full p-3 text-xs bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-purple-500 font-mono"
            />

            <button
              onClick={handleRunTestPrompt}
              disabled={testLoading}
              className="px-5 py-2.5 rounded-xl bg-purple-600 text-white font-extrabold text-xs hover:bg-purple-500 transition-all flex items-center gap-2"
            >
              {testLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              <span>Execute Prompt Test</span>
            </button>
          </div>

          {testOutput && (
            <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-2 mt-4">
              <div className="flex items-center justify-between text-[11px] text-slate-400 font-bold border-b border-slate-800 pb-2">
                <span>Latency: <strong className="text-cyan-400">{testOutput.latencyMs}ms</strong></span>
                <span>Tokens Used: <strong className="text-amber-400">{testOutput.tokensUsed}</strong></span>
                <span>Est. Cost: <strong className="text-emerald-400">${testOutput.estimatedCostUsd}</strong></span>
              </div>
              <p className="text-xs text-slate-200 font-mono pt-2">{testOutput.output}</p>
            </div>
          )}
        </GlassCard>
      )}
    </div>
  );
};
