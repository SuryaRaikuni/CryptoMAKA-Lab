import { useState } from 'react';
import { api } from '../services/api';
import { Play, Clock, BarChart2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function BenchmarkLab() {
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<any>(null);
  const [error, setError] = useState('');
  
  const [iterations, setIterations] = useState(500);

  const runComparison = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api.post('/benchmarks/compare', {
        protocols: ['ju_park', 'ecc', 'reduced_roundtrip'],
        iterations,
        warmup: 10
      });
      setReport(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getChartData = () => {
    if (!report) return [];
    return report.results.map((r: any) => ({
      name: r.protocol,
      'Mean (ms)': r.total.mean_ms,
      'Min (ms)': r.total.min_ms,
      'Max (ms)': r.total.max_ms
    }));
  };

  return (
    <div className="space-y-6">
      <header className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Benchmark Lab</h1>
          <p className="text-gray-500 mt-2">Performance and communication overhead comparison</p>
        </div>
        <div className="flex gap-4 items-center">
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Iterations</label>
            <input 
              type="number" 
              value={iterations}
              onChange={(e) => setIterations(parseInt(e.target.value) || 100)}
              className="border border-gray-300 rounded px-3 py-2 w-24 text-sm"
              min="1" max="10000"
            />
          </div>
          <button
            onClick={runComparison}
            disabled={loading}
            className="bg-indigo-600 hover:bg-indigo-700 mt-5 text-white font-medium rounded-lg px-5 py-2 flex items-center transition-colors disabled:opacity-50"
          >
            {loading ? <Clock className="animate-spin mr-2" size={20}/> : <Play className="mr-2" size={20}/>}
            Run Comparison
          </button>
        </div>
      </header>

      {error && (
        <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-200">
          {error}
        </div>
      )}

      {report && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h2 className="text-xl font-bold mb-6 flex items-center text-gray-800">
              <BarChart2 className="mr-2 text-indigo-500" />
              Execution Time (ms)
            </h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={getChartData()} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip cursor={{fill: 'transparent'}}/>
                  <Legend />
                  <Bar dataKey="Mean (ms)" fill="#4f46e5" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Protocol</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Mean (ms)</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">StdDev (ms)</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Throughput (ops/s)</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Comm Cost (bits)</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {report.results.map((r: any, idx: number) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">{r.protocol}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-700">{r.total.mean_ms.toFixed(3)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">{r.total.stddev_ms.toFixed(3)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-700 font-mono">{r.total.throughput_ops_per_sec.toFixed(1)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-700 font-mono">{r.communication_bits || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          <div className="text-xs text-gray-400 text-right">
            System: {report.host_metadata.system} {report.host_metadata.machine} | Python {report.host_metadata.python_version}
          </div>
        </div>
      )}
    </div>
  );
}
