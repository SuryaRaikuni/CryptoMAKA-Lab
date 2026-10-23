import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Shield, Zap, Activity, History, FileText } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import ProtocolSimulator from './pages/ProtocolSimulator';
import SecurityLab from './pages/SecurityLab';
import BenchmarkLab from './pages/BenchmarkLab';
import QuantumThreat from './pages/QuantumThreat';
import ExperimentHistory from './pages/ExperimentHistory';

function Sidebar() {
  const location = useLocation();
  
  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/simulator', label: 'Protocol Simulator', icon: Activity },
    { path: '/security', label: 'Security Lab', icon: Shield },
    { path: '/benchmarks', label: 'Benchmark Lab', icon: Zap },
    { path: '/quantum', label: 'Quantum Threat', icon: Shield },
    { path: '/experiments', label: 'Experiment History', icon: History },
  ];

  return (
    <div className="w-64 bg-gray-900 text-white min-h-screen flex flex-col">
      <div className="p-6">
        <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
          CryptoMAKA Lab
        </h1>
        <p className="text-xs text-gray-400 mt-1">Research Platform</p>
      </div>
      <nav className="flex-1 px-4 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                isActive 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Academic Paper Download Card */}
      <div className="p-4 mx-4 mb-4 bg-gray-800/80 rounded-xl border border-gray-700/60 text-xs space-y-2">
        <div className="flex items-center gap-2 text-indigo-400 font-bold">
          <FileText size={15} />
          <span>Academic Paper</span>
        </div>
        <p className="text-[11px] text-gray-400 leading-tight">
          IEEE camera-ready preprint with formal proofs & IoT energy model.
        </p>
        <div className="flex gap-1.5 pt-1">
          <a
            href="/api/v1/research/paper/download?format=pdf"
            download="CryptoMAKA_Academic_Manuscript.pdf"
            className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-1.5 px-2 rounded text-center text-[10px] transition-colors"
          >
            PDF Paper
          </a>
          <a
            href="/api/v1/research/paper/download?format=tex"
            download="CryptoMAKA_Academic_Manuscript.tex"
            className="flex-1 bg-gray-700 hover:bg-gray-600 text-gray-200 font-medium py-1.5 px-2 rounded text-center text-[10px] transition-colors"
          >
            LaTeX (.tex)
          </a>
        </div>
      </div>

      <div className="px-4 pb-4 text-[11px] text-gray-500">
        Ju-Park 2023 MAKA Research
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-gray-50">
        <Sidebar />
        <main className="flex-1 p-8 overflow-auto">
          <div className="max-w-6xl mx-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/simulator" element={<ProtocolSimulator />} />
              <Route path="/security" element={<SecurityLab />} />
              <Route path="/benchmarks" element={<BenchmarkLab />} />
              <Route path="/quantum" element={<QuantumThreat />} />
              <Route path="/experiments" element={<ExperimentHistory />} />
            </Routes>
          </div>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
