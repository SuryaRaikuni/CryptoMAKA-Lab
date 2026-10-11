import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { 
  Play, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  BookmarkPlus, 
  Eye, 
  Code2, 
  BookOpen, 
  Check, 
  ExternalLink 
} from 'lucide-react';
import { ProtocolFlow } from '../components/ProtocolFlow';
import { Link } from 'react-router-dom';

export default function ProtocolSimulator() {
  const [protocols, setProtocols] = useState<any[]>([]);
  const [selected, setSelected] = useState('ju_park');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [activeTab, setActiveTab] = useState<'flow' | 'raw' | 'spec'>('flow');
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);
  const [savingExp, setSavingExp] = useState(false);

  useEffect(() => {
    api.get('/protocols').then(setProtocols).catch(console.error);
  }, []);

  const runProtocol = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    setSaveSuccess(null);
    try {
      const data = await api.post(`/protocols/${selected}/run`);
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const saveAsExperiment = async () => {
    if (!result) return;
    setSavingExp(true);
    try {
      const expName = `Simulation Run - ${protocols.find(p => p.id === selected)?.name || selected} (${new Date().toLocaleTimeString()})`;
      const created = await api.post('/experiments', {
        name: expName,
        protocol: selected,
        configuration: {
          simulated_at: new Date().toISOString(),
          duration_ms: result.timings.total_ms,
          message_count: result.message_count,
          communication_bits: result.communication_bits,
        }
      });
      setSaveSuccess(created.id);
    } catch (err: any) {
      alert(`Failed to save experiment: ${err.message}`);
    } finally {
      setSavingExp(false);
    }
  };

  return (
    <div className="space-y-6">
      <header className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Protocol Simulator</h1>
          <p className="text-gray-500 mt-2">Execute, inspect, and trace cryptographic protocol round-trips</p>
        </div>
      </header>

      {/* Protocol Selection & Run Card */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col md:flex-row gap-4 items-stretch md:items-end">
          <div className="flex-1">
            <label className="block text-sm font-semibold text-gray-700 mb-2">Select Target Protocol</label>
            <select 
              className="w-full bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5 font-medium"
              value={selected}
              onChange={e => { setSelected(e.target.value); setResult(null); setSaveSuccess(null); }}
            >
              {protocols.map(p => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
          <button
            onClick={runProtocol}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg px-6 py-2.5 flex items-center justify-center transition-all shadow-sm hover:shadow disabled:opacity-50"
          >
            {loading ? <Clock className="animate-spin mr-2" size={18}/> : <Play className="mr-2" size={18}/>}
            Run Simulation
          </button>
        </div>

        {protocols.find(p => p.id === selected) && (
          <div className="mt-4 p-4 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700 leading-relaxed">
            <div className="flex items-center gap-2 font-semibold text-slate-900 mb-1">
              <BookOpen size={16} className="text-blue-600" />
              Protocol Architecture Note:
            </div>
            {protocols.find(p => p.id === selected)?.description}
          </div>
        )}
      </div>

      {error && (
        <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-200 flex items-center">
          <XCircle className="mr-2 shrink-0" /> {error}
        </div>
      )}

      {/* Execution Results View */}
      {result && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-6 border-b border-gray-200 bg-gray-50 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <h2 className="text-lg font-bold text-gray-900">Execution Observables</h2>
              <p className="text-xs text-gray-500 mt-0.5 font-mono">Run ID: {result.run_id}</p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${
                result.authentication_success ? 'bg-green-100 text-green-800 border border-green-200' : 'bg-red-100 text-red-800'
              }`}>
                {result.authentication_success ? <CheckCircle2 size={14} className="mr-1.5"/> : <XCircle size={14} className="mr-1.5"/>}
                Mutual Authentication OK
              </span>

              <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${
                result.session_key_match ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' : 'bg-red-100 text-red-800'
              }`}>
                {result.session_key_match ? <CheckCircle2 size={14} className="mr-1.5"/> : <XCircle size={14} className="mr-1.5"/>}
                Session Key Agreement Match
              </span>

              <span className="text-slate-600 text-xs font-mono bg-white px-2.5 py-1 rounded border border-gray-200 shadow-2xs">
                Latency: <strong className="text-slate-900">{result.timings.total_ms} ms</strong>
              </span>

              <span className="text-slate-600 text-xs font-mono bg-white px-2.5 py-1 rounded border border-gray-200 shadow-2xs">
                Bits: <strong className="text-slate-900">{result.communication_bits || 'N/A'}</strong>
              </span>
            </div>
          </div>

          {/* Action Ribbon & Tabs */}
          <div className="px-6 py-3 border-b border-gray-200 bg-white flex flex-col sm:flex-row justify-between items-center gap-3">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setActiveTab('flow')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  activeTab === 'flow'
                    ? 'bg-blue-50 text-blue-700 border border-blue-200 font-bold'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <Eye size={14} /> Sequence Lifelines
              </button>

              <button
                onClick={() => setActiveTab('raw')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  activeTab === 'raw'
                    ? 'bg-blue-50 text-blue-700 border border-blue-200 font-bold'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <Code2 size={14} /> Raw Observables
              </button>
            </div>

            <div className="flex items-center gap-2">
              {saveSuccess ? (
                <div className="flex items-center gap-2 text-xs text-green-700 bg-green-50 px-3 py-1 rounded-lg border border-green-200">
                  <Check size={14} className="text-green-600" />
                  Saved to Experiments
                  <Link to="/experiments" className="text-blue-600 underline font-semibold flex items-center ml-1">
                    View <ExternalLink size={12} className="ml-0.5" />
                  </Link>
                </div>
              ) : (
                <button
                  onClick={saveAsExperiment}
                  disabled={savingExp}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium transition-colors border border-slate-300"
                >
                  <BookmarkPlus size={14} />
                  {savingExp ? 'Saving...' : 'Save Run to Experiment History'}
                </button>
              )}
            </div>
          </div>

          <div className="p-6">
            {activeTab === 'flow' ? (
              <ProtocolFlow protocolId={result.protocol} messages={result.messages} />
            ) : (
              <div className="bg-slate-950 text-slate-200 p-5 rounded-xl font-mono text-xs overflow-x-auto border border-slate-800">
                <div className="text-slate-400 mb-2">// Audit Trace — Zero Private Keys or Session Keys Exposed</div>
                <pre>{JSON.stringify(result, null, 2)}</pre>
              </div>
            )}
            
            {result.notes && result.notes.length > 0 && (
              <div className="mt-6 pt-5 border-t border-gray-100">
                <h4 className="font-semibold text-xs text-gray-500 uppercase tracking-wider mb-2">Academic & Implementation Notes</h4>
                <ul className="list-disc pl-5 text-sm text-gray-600 space-y-1">
                  {result.notes.map((note: string, i: number) => <li key={i}>{note}</li>)}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
