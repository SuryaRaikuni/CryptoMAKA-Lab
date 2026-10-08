import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Play, CheckCircle2, XCircle, Clock } from 'lucide-react';

export default function ProtocolSimulator() {
  const [protocols, setProtocols] = useState<any[]>([]);
  const [selected, setSelected] = useState('ju_park');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/protocols').then(setProtocols).catch(console.error);
  }, []);

  const runProtocol = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const data = await api.post(`/protocols/${selected}/run`);
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-gray-900">Protocol Simulator</h1>
        <p className="text-gray-500 mt-2">Execute and visualize cryptographic protocols</p>
      </header>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex gap-4 items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">Select Protocol</label>
            <select 
              className="w-full bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5"
              value={selected}
              onChange={e => setSelected(e.target.value)}
            >
              {protocols.map(p => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
          <button
            onClick={runProtocol}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg px-5 py-2.5 flex items-center transition-colors disabled:opacity-50"
          >
            {loading ? <Clock className="animate-spin mr-2" size={20}/> : <Play className="mr-2" size={20}/>}
            Run Simulation
          </button>
        </div>

        {protocols.find(p => p.id === selected) && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg text-sm text-gray-600">
            {protocols.find(p => p.id === selected)?.description}
          </div>
        )}
      </div>

      {error && (
        <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-200 flex items-center">
          <XCircle className="mr-2" /> {error}
        </div>
      )}

      {result && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-6 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
            <h2 className="text-lg font-bold">Execution Result</h2>
            <div className="flex items-center gap-4">
              <span className={`flex items-center ${result.authentication_success ? 'text-green-600' : 'text-red-600'}`}>
                {result.authentication_success ? <CheckCircle2 size={16} className="mr-1"/> : <XCircle size={16} className="mr-1"/>}
                Auth
              </span>
              <span className={`flex items-center ${result.session_key_match ? 'text-green-600' : 'text-red-600'}`}>
                {result.session_key_match ? <CheckCircle2 size={16} className="mr-1"/> : <XCircle size={16} className="mr-1"/>}
                Key Match
              </span>
              <span className="text-gray-500 text-sm">{result.timings.total_ms} ms</span>
            </div>
          </div>
          <div className="p-6">
            <h3 className="font-semibold mb-4 text-gray-700">Message Exchange ({result.message_count} messages)</h3>
            <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent">
              {result.messages.map((m: any, idx: number) => (
                <div key={idx} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                  <div className="flex items-center justify-center w-10 h-10 rounded-full border border-white bg-blue-500 text-slate-100 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                    {idx + 1}
                  </div>
                  <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded border border-slate-200 bg-white shadow-sm">
                    <div className="flex items-center justify-between mb-1">
                      <div className="font-bold text-slate-900">{m.name}</div>
                      <div className="text-xs font-medium text-slate-500">{m.size_bits} bits</div>
                    </div>
                    <div className="text-slate-600 text-sm">{m.direction}</div>
                  </div>
                </div>
              ))}
            </div>
            
            {result.notes && result.notes.length > 0 && (
              <div className="mt-8 pt-6 border-t border-gray-100">
                <h3 className="font-semibold mb-2 text-gray-700">Notes</h3>
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
