import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { 
  Download, 
  Database, 
  Clock, 
  Plus, 
  X, 
  CheckCircle2, 
  XCircle, 
  ChevronDown, 
  ChevronUp, 
  Play
} from 'lucide-react';

export default function ExperimentHistory() {
  const [experiments, setExperiments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Expanded item state
  const [selectedExpId, setSelectedExpId] = useState<string | null>(null);
  const [expDetails, setExpDetails] = useState<any>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  // New Experiment Modal
  const [showModal, setShowModal] = useState(false);
  const [newExpName, setNewExpName] = useState('');
  const [newExpProtocol, setNewExpProtocol] = useState('ju_park');
  const [creating, setCreating] = useState(false);

  const fetchExperiments = () => {
    setLoading(true);
    api.get('/experiments')
      .then(data => {
        setExperiments(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchExperiments();
  }, []);

  const handleSelectExp = async (id: string) => {
    if (selectedExpId === id) {
      setSelectedExpId(null);
      setExpDetails(null);
      return;
    }
    setSelectedExpId(id);
    setLoadingDetail(true);
    try {
      const data = await api.get(`/experiments/${id}`);
      setExpDetails(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleCreateExperiment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newExpName.trim()) return;
    setCreating(true);
    try {
      await api.post('/experiments', {
        name: newExpName.trim(),
        protocol: newExpProtocol,
        configuration: {
          created_manually: true,
          platform: 'CryptoMAKA Lab Web UI'
        }
      });
      setShowModal(false);
      setNewExpName('');
      fetchExperiments();
    } catch (err: any) {
      alert(`Error creating experiment: ${err.message}`);
    } finally {
      setCreating(false);
    }
  };

  const handleExportJson = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    window.location.href = `/api/v1/experiments/${id}/export/json`;
  };

  const handleExportCsv = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    window.location.href = `/api/v1/experiments/${id}/export/csv`;
  };

  return (
    <div className="space-y-6">
      <header className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Experiment History</h1>
          <p className="text-gray-500 mt-2">Saved experimental records, micro-runs, and academic dataset exports</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg px-4 py-2.5 flex items-center gap-2 self-start sm:self-auto transition-colors shadow-xs"
        >
          <Plus size={18} />
          Create Experiment
        </button>
      </header>

      {/* Main Table */}
      {loading ? (
        <div className="p-12 text-center text-gray-500 bg-white rounded-xl border border-gray-200">
          <Clock className="animate-spin inline-block mr-2" size={20} />
          Loading experiment records...
        </div>
      ) : experiments.length === 0 ? (
        <div className="bg-white p-12 rounded-xl shadow-sm border border-gray-200 text-center flex flex-col items-center">
          <Database size={48} className="text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900">No experiments recorded yet</h3>
          <p className="text-gray-500 mt-1 max-w-sm">
            Execute protocols in the Simulator or click "Create Experiment" to record reproducible runs.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3.5 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Date & Time</th>
                <th className="px-6 py-3.5 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Experiment Name</th>
                <th className="px-6 py-3.5 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Protocol</th>
                <th className="px-6 py-3.5 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">Runs</th>
                <th className="px-6 py-3.5 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">Export</th>
                <th className="px-4 py-3.5 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider"></th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {experiments.map((exp: any) => {
                const isExpanded = selectedExpId === exp.id;
                return (
                  <React.Fragment key={exp.id}>
                    <tr 
                      onClick={() => handleSelectExp(exp.id)}
                      className={`cursor-pointer transition-colors ${isExpanded ? 'bg-blue-50/60' : 'hover:bg-gray-50'}`}
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <div className="flex items-center gap-2">
                          <Clock size={14} className="text-gray-400" />
                          {new Date(exp.created_at).toLocaleString()}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                        {exp.name || exp.id.substring(0, 8)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className="px-2 py-0.5 rounded font-mono text-xs bg-slate-100 text-slate-800 border border-slate-200">
                          {exp.protocol}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-center font-semibold text-gray-700">
                        {exp.run_count}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                        <button 
                          onClick={(e) => handleExportCsv(exp.id, e)} 
                          className="text-indigo-600 hover:text-indigo-900 font-medium mr-4 inline-flex items-center text-xs"
                          title="Export as CSV"
                        >
                          <Download size={13} className="mr-1"/> CSV
                        </button>
                        <button 
                          onClick={(e) => handleExportJson(exp.id, e)} 
                          className="text-blue-600 hover:text-blue-900 font-medium inline-flex items-center text-xs"
                          title="Export as JSON"
                        >
                          <Download size={13} className="mr-1"/> JSON
                        </button>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-center text-gray-400">
                        {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                      </td>
                    </tr>

                    {/* Expanded Detail Panel */}
                    {isExpanded && (
                      <tr>
                        <td colSpan={6} className="px-6 py-5 bg-slate-50 border-y border-blue-100">
                          {loadingDetail ? (
                            <div className="py-4 text-center text-xs text-gray-500">
                              <Clock className="animate-spin inline-block mr-1.5" size={14} />
                              Loading run records...
                            </div>
                          ) : expDetails ? (
                            <div className="space-y-4">
                              <div className="flex justify-between items-center text-xs">
                                <span className="font-semibold text-slate-700 uppercase tracking-wider">
                                  Run History ({expDetails.runs?.length || 0} Executions)
                                </span>
                                <span className="font-mono text-slate-400">ID: {expDetails.id}</span>
                              </div>

                              {expDetails.runs && expDetails.runs.length > 0 ? (
                                <div className="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-2xs">
                                  <table className="min-w-full text-xs divide-y divide-gray-100">
                                    <thead className="bg-slate-100/70 text-slate-600 font-medium">
                                      <tr>
                                        <th className="px-4 py-2 text-left">Run ID</th>
                                        <th className="px-4 py-2 text-left">Protocol</th>
                                        <th className="px-4 py-2 text-center">Auth Status</th>
                                        <th className="px-4 py-2 text-center">Key Match</th>
                                        <th className="px-4 py-2 text-right">Messages</th>
                                        <th className="px-4 py-2 text-right">Latency</th>
                                        <th className="px-4 py-2 text-right">Time</th>
                                      </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-100">
                                      {expDetails.runs.map((r: any, idx: number) => (
                                        <tr key={idx} className="hover:bg-slate-50/50">
                                          <td className="px-4 py-2 font-mono text-slate-500">{r.run_id ? r.run_id.substring(0, 8) : `run-${idx+1}`}</td>
                                          <td className="px-4 py-2 font-medium">{r.protocol}</td>
                                          <td className="px-4 py-2 text-center">
                                            {r.authentication_success ? (
                                              <span className="inline-flex items-center text-green-700 font-semibold gap-1">
                                                <CheckCircle2 size={12} /> OK
                                              </span>
                                            ) : (
                                              <span className="inline-flex items-center text-red-600 font-semibold gap-1">
                                                <XCircle size={12} /> Failed
                                              </span>
                                            )}
                                          </td>
                                          <td className="px-4 py-2 text-center">
                                            {r.session_key_match ? (
                                              <span className="inline-flex items-center text-emerald-700 font-semibold gap-1">
                                                <CheckCircle2 size={12} /> Match
                                              </span>
                                            ) : (
                                              <span className="inline-flex items-center text-amber-600 gap-1">
                                                <XCircle size={12} /> Mismatch
                                              </span>
                                            )}
                                          </td>
                                          <td className="px-4 py-2 text-right font-mono">{r.message_count || '-'}</td>
                                          <td className="px-4 py-2 text-right font-mono text-slate-800">
                                            {r.duration_ms ? `${Number(r.duration_ms).toFixed(3)} ms` : '-'}
                                          </td>
                                          <td className="px-4 py-2 text-right text-slate-400">
                                            {r.created_at ? new Date(r.created_at).toLocaleTimeString() : '-'}
                                          </td>
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                </div>
                              ) : (
                                <p className="text-xs text-slate-500 italic">No micro-runs attached to this experiment.</p>
                              )}

                              {expDetails.configuration && (
                                <div className="text-xs bg-slate-900 text-slate-300 p-3 rounded-lg font-mono">
                                  <div className="text-slate-500 mb-1">// Experiment Configuration</div>
                                  <pre>{JSON.stringify(expDetails.configuration, null, 2)}</pre>
                                </div>
                              )}
                            </div>
                          ) : null}
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Experiment Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6 border border-gray-200">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-gray-900">Launch New Experiment</h3>
              <button 
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleCreateExperiment} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Experiment Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Head-to-Head Latency Benchmark"
                  value={newExpName}
                  onChange={(e) => setNewExpName(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-300 rounded-lg p-2.5 text-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Protocol Variant</label>
                <select
                  value={newExpProtocol}
                  onChange={(e) => setNewExpProtocol(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-300 rounded-lg p-2.5 text-sm focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="ju_park">Ju-Park 2023 Normalized (Hash/XOR)</option>
                  <option value="ecc">ECC/ECDH P-256 Counterpart</option>
                  <option value="reduced_roundtrip">Proposed Reduced-Roundtrip Extension</option>
                </select>
              </div>

              <div className="pt-4 flex justify-end gap-3 border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="px-5 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center gap-1.5 transition-colors disabled:opacity-50"
                >
                  {creating ? <Clock className="animate-spin" size={16}/> : <Play size={16}/>}
                  Execute & Record
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
