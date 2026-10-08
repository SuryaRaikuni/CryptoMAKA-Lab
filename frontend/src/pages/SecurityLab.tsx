import { useState } from 'react';
import { api } from '../services/api';
import { Shield, ShieldAlert, ShieldCheck, Play, Clock } from 'lucide-react';

export default function SecurityLab() {
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<any>(null);
  const [error, setError] = useState('');

  const runSecurityTests = async () => {
    setLoading(true);
    setError('');
    try {
      // currently only ju_park is supported for full security suite
      const data = await api.post('/security/run', { protocol: 'ju_park' });
      setReport(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <header className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Security Lab</h1>
          <p className="text-gray-500 mt-2">Automated cryptographic attack simulations</p>
        </div>
        <button
          onClick={runSecurityTests}
          disabled={loading}
          className="bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg px-5 py-2.5 flex items-center transition-colors disabled:opacity-50"
        >
          {loading ? <Clock className="animate-spin mr-2" size={20}/> : <Play className="mr-2" size={20}/>}
          Run All Threats
        </button>
      </header>

      {error && (
        <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-200">
          {error}
        </div>
      )}

      {report && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 text-center">
              <div className="text-4xl font-bold text-gray-900 mb-2">{report.total}</div>
              <div className="text-gray-500 font-medium text-sm uppercase tracking-wider">Total Tests</div>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-sm border border-green-200 text-center">
              <div className="text-4xl font-bold text-green-600 mb-2">{report.passed}</div>
              <div className="text-green-600 font-medium text-sm uppercase tracking-wider">Passed</div>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-sm border border-red-200 text-center">
              <div className="text-4xl font-bold text-red-600 mb-2">{report.failed}</div>
              <div className="text-red-600 font-medium text-sm uppercase tracking-wider">Failed</div>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800">
            <h4 className="font-bold flex items-center mb-1"><Shield className="mr-2" size={16}/> Disclaimer</h4>
            {report.disclaimer}
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Test Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Evidence</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {report.results.map((r: any, idx: number) => (
                  <tr key={idx} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{r.test.replace(/_/g, ' ').toUpperCase()}</div>
                      <div className="text-xs text-gray-500 max-w-xs truncate" title={r.description}>{r.description}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {r.status === 'PASS' 
                        ? <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"><ShieldCheck size={14} className="mr-1"/> PASS</span>
                        : <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800"><ShieldAlert size={14} className="mr-1"/> FAIL</span>
                      }
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{r.evidence}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium uppercase ${
                        r.severity === 'high' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {r.severity}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
