import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Download, Database, Clock } from 'lucide-react';

export default function ExperimentHistory() {
  const [experiments, setExperiments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/experiments').then(data => {
      setExperiments(data);
      setLoading(false);
    }).catch(console.error);
  }, []);

  const handleExportJson = (id: string) => {
    window.location.href = `/api/v1/experiments/${id}/export/json`;
  };

  const handleExportCsv = (id: string) => {
    window.location.href = `/api/v1/experiments/${id}/export/csv`;
  };

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-gray-900">Experiment History</h1>
        <p className="text-gray-500 mt-2">Saved experimental runs and data exports</p>
      </header>

      {loading ? (
        <div className="p-8 text-center text-gray-500">Loading history...</div>
      ) : experiments.length === 0 ? (
        <div className="bg-white p-12 rounded-xl shadow-sm border border-gray-200 text-center flex flex-col items-center">
          <Database size={48} className="text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900">No experiments yet</h3>
          <p className="text-gray-500 mt-1">Run tests in the simulator to see them here.</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Protocol</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Runs</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Export</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {experiments.map((exp: any) => (
                <tr key={exp.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="flex items-center">
                      <Clock size={14} className="mr-2" />
                      {new Date(exp.created_at).toLocaleString()}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">{exp.name || exp.id.substring(0,8)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 font-mono">{exp.protocol}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium">{exp.run_count}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button onClick={() => handleExportCsv(exp.id)} className="text-indigo-600 hover:text-indigo-900 mr-4 inline-flex items-center">
                      <Download size={14} className="mr-1"/> CSV
                    </button>
                    <button onClick={() => handleExportJson(exp.id)} className="text-blue-600 hover:text-blue-900 inline-flex items-center">
                      <Download size={14} className="mr-1"/> JSON
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
