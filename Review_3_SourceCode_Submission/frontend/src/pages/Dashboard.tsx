import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Shield, Activity, Award, Download, FileText } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    api.get('/health').then(setHealth).catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-2">Platform status and quick access</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center space-x-4">
          <div className="p-3 bg-green-100 text-green-600 rounded-lg">
            <Activity size={24} />
          </div>
          <div>
            <p className="text-sm text-gray-500 font-medium">API Status</p>
            <p className="text-xl font-bold">{health?.status === 'healthy' ? 'Online' : 'Offline'}</p>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center space-x-4">
          <div className="p-3 bg-blue-100 text-blue-600 rounded-lg">
            <Activity size={24} />
          </div>
          <div>
            <p className="text-sm text-gray-500 font-medium">Database</p>
            <p className="text-xl font-bold">{health?.database === 'connected' ? 'Connected' : 'Error'}</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center space-x-4">
          <div className="p-3 bg-purple-100 text-purple-600 rounded-lg">
            <Activity size={24} />
          </div>
          <div>
            <p className="text-sm text-gray-500 font-medium">Version</p>
            <p className="text-xl font-bold">{health?.version || 'Unknown'}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h2 className="text-xl font-bold mb-4 flex items-center">
            <Activity className="mr-2 text-blue-500" />
            Protocol Simulation
          </h2>
          <p className="text-gray-600 mb-4">
            Run the original Ju-Park protocol alongside ECC counterpart and the proposed reduced-round-trip extension.
          </p>
          <Link to="/simulator" className="text-blue-600 font-medium hover:underline">Go to Simulator &rarr;</Link>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h2 className="text-xl font-bold mb-4 flex items-center">
            <Shield className="mr-2 text-red-500" />
            Security Lab
          </h2>
          <p className="text-gray-600 mb-4">
            Execute automated attack simulations (replay, tampering, impersonation) to verify protocol resilience.
          </p>
          <Link to="/security" className="text-blue-600 font-medium hover:underline">Go to Security Lab &rarr;</Link>
        </div>
      </div>

      {/* Camera-Ready Academic Manuscript Card */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 rounded-2xl shadow-md border border-indigo-900/40 relative overflow-hidden">
        <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="space-y-2 max-w-2xl">
            <div className="flex items-center gap-2">
              <span className="p-1.5 bg-indigo-500/20 rounded-lg text-indigo-400">
                <Award size={18} />
              </span>
              <span className="text-xs uppercase tracking-wider font-bold text-indigo-300">
                Peer-Review Publication Ready
              </span>
            </div>
            <h3 className="text-xl font-bold text-white">
              CryptoMAKA Academic Research Manuscript
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Camera-ready IEEE / ACM format manuscript incorporating live ProVerif 2.05 formal verification theorems, automated adversary test vectors, and cyber-physical LPWAN/Cellular IoT energy projections.
            </p>
          </div>

          <div className="flex flex-wrap gap-2.5 shrink-0">
            <a
              href="/api/v1/research/paper/download?format=pdf"
              download="CryptoMAKA_Academic_Manuscript.pdf"
              className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs px-4 py-2.5 rounded-xl shadow-sm transition-all flex items-center gap-2"
            >
              <Download size={15} />
              Download PDF Manuscript
            </a>
            <a
              href="/api/v1/research/paper/download?format=tex"
              download="CryptoMAKA_Academic_Manuscript.tex"
              className="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold text-xs px-4 py-2.5 rounded-xl transition-all flex items-center gap-2"
            >
              <FileText size={15} />
              LaTeX Source (.tex)
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
