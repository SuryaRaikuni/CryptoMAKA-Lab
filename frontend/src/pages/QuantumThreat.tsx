import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { AlertTriangle, Info, Play } from 'lucide-react';

export default function QuantumThreat() {
  const [report, setReport] = useState<any>(null);
  const [demoSecret, setDemoSecret] = useState(12345);
  const [demoResult, setDemoResult] = useState<any>(null);
  const [loadingDemo, setLoadingDemo] = useState(false);

  useEffect(() => {
    api.get('/quantum/threat-report').then(setReport).catch(console.error);
  }, []);

  const runDemo = async () => {
    setLoadingDemo(true);
    try {
      const data = await api.get(`/quantum/demo/discrete-log?secret_x=${demoSecret}`);
      setDemoResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingDemo(false);
    }
  };

  if (!report) return <div className="p-8 text-gray-500 animate-pulse">Loading analysis...</div>;

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-gray-900">Quantum Threat Analysis</h1>
        <p className="text-gray-500 mt-2">Conceptual analysis of post-quantum security implications</p>
      </header>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800 flex items-start">
        <AlertTriangle className="mr-3 mt-0.5 shrink-0 text-yellow-600" />
        <div>
          <h4 className="font-bold mb-1">Academic Disclaimer</h4>
          {report.disclaimer}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {Object.entries(report.threat_analysis).map(([key, threat]: [string, any]) => (
          <div key={key} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-bold text-gray-900">{threat.algorithm}</h3>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium uppercase ${
                threat.quantum_threat === 'HIGH' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
              }`}>
                {threat.quantum_threat} THREAT
              </span>
            </div>
            <div className="space-y-3 text-sm">
              <p><strong>Hardness Assumption:</strong> {threat.hardness_assumption}</p>
              <p><strong>Relevant Algorithm:</strong> {threat.relevant_quantum_algorithm}</p>
              <div className="flex items-center gap-4 mt-2 mb-4">
                <div className="bg-gray-100 px-3 py-2 rounded">
                  <span className="block text-xs text-gray-500">Classical Security</span>
                  <span className="font-mono font-medium">{threat.classical_security_bits} bits</span>
                </div>
                <div className="bg-gray-100 px-3 py-2 rounded">
                  <span className="block text-xs text-gray-500">Quantum Security</span>
                  <span className="font-mono font-medium">{threat.quantum_security_bits} bits</span>
                </div>
              </div>
              <p className="text-gray-600 border-l-2 border-gray-200 pl-3 italic">{threat.explanation}</p>
              <div className="mt-4 pt-4 border-t border-gray-100">
                <p className="text-blue-700"><strong>Mitigation:</strong> {threat.mitigation}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h2 className="text-xl font-bold mb-4">Toy Classical Discrete-Log Demo</h2>
        <p className="text-sm text-gray-600 mb-6">
          This is a classical brute-force search on a deliberately small prime group (p ≈ 2³¹). 
          It illustrates why real ECC uses massive groups (P-256 uses p ≈ 2²⁵⁶) which cannot be 
          brute-forced classically, thus requiring Shor's algorithm on a quantum computer.
        </p>
        
        <div className="flex items-end gap-4 mb-6">
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Secret (x)</label>
            <input 
              type="number" 
              value={demoSecret}
              onChange={(e) => setDemoSecret(parseInt(e.target.value) || 1)}
              className="border border-gray-300 rounded px-3 py-2 w-32"
              min="1" max="999999"
            />
          </div>
          <button
            onClick={runDemo}
            disabled={loadingDemo}
            className="bg-slate-800 hover:bg-slate-900 text-white font-medium rounded-lg px-5 py-2 flex items-center transition-colors disabled:opacity-50"
          >
            {loadingDemo ? <span className="animate-pulse">Running...</span> : <><Play size={16} className="mr-2"/> Run Classical Brute-Force</>}
          </button>
        </div>

        {demoResult && (
          <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 font-mono text-sm">
            <div className="text-slate-500 mb-2">// {demoResult.label}</div>
            <div className="text-blue-600">p = {demoResult.parameters.p}</div>
            <div className="text-blue-600">g = {demoResult.parameters.g}</div>
            <div className="text-green-600 mt-2">Target y = {demoResult.parameters.y}</div>
            
            <div className="my-4 border-l-2 border-indigo-300 pl-3 py-1 bg-indigo-50/50">
              <span className="font-bold text-indigo-700">Found x: {demoResult.recovered_x}</span>
              <span className="text-slate-500 ml-4">in {demoResult.elapsed_ms} ms</span>
            </div>
            
            <div className="text-slate-600 flex items-start mt-4 text-xs">
              <Info size={14} className="mr-2 shrink-0 mt-0.5" />
              {demoResult.interpretation}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
