import React, { useState } from 'react';
import { api } from '../services/api';
import { 
  ShieldAlert, 
  ShieldCheck, 
  Play, 
  Clock, 
  ChevronDown, 
  ChevronUp, 
  AlertTriangle,
  FileCheck2
} from 'lucide-react';

export default function SecurityLab() {
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<any>(null);
  const [error, setError] = useState('');
  const [selectedTest, setSelectedTest] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'high'>('all');

  const runSecurityTests = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api.post('/security/run', { protocol: 'ju_park' });
      setReport(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getAdversaryContext = (testName: string) => {
    switch (testName) {
      case 'replay_attack':
        return {
          dolevYao: 'Adversary records message M1 from a legitimate session and replays it to the Cloud Server after the session finishes.',
          defenseMechanism: 'The Control Server rotates the user pseudonym PIDi into PIDi* upon successful authentication. When the replayed M1 is processed, PIDi is not found, returning "unknown PID".',
          formalProof: 'Validated under Random Oracle Model (RoR) for fresh ticket unlinkability.'
        };
      case 'stale_timestamp':
        return {
          dolevYao: 'Adversary captures and delays message transmission by > 30 seconds before delivering it to the receiver.',
          defenseMechanism: 'Receiving node verifies freshness |T_current - TS| ≤ 30s before computing MAC authenticators, mitigating replay and resource exhaustion.',
          formalProof: 'Strict freshness check modeled in BAN logic idealization.'
        };
      case 'message_tampering':
        return {
          dolevYao: 'Adversary modifies bit patterns in transit on public channels (e.g. flips bits in B1, B2, or B3).',
          defenseMechanism: 'Message authenticators V1, V2, V3, V4 act as keyed cryptographic MACs. Constant-time comparison rejects modified payloads.',
          formalProof: 'Preimage and collision resistance of SHA-256 enforces integrity.'
        };
      case 'user_impersonation':
        return {
          dolevYao: 'Adversary fabricates an unauthorized login request with random credentials or counterfeit identities.',
          defenseMechanism: 'Without possessing ki = H(SIDi ∥ xcs ∥ ni), adversary cannot produce valid V1.',
          formalProof: 'RoR game reduces forgery to breaking SHA-256 PRF.'
        };
      case 'mitm_cloud_impersonation':
        return {
          dolevYao: 'A malicious server attempts to spoof a legitimate cloud provider without registration credentials.',
          defenseMechanism: 'Rogue server lacks registration key kj = H(IDj ∥ xcs ∥ nj), failing V2 check.',
          formalProof: 'Mutual server authentication verified via Control Server ticket.'
        };
      case 'nonce_reuse':
        return {
          dolevYao: 'Adversary tests if pseudo-random nonces repeat, leading to keystream reuse in XOR operations.',
          defenseMechanism: 'Fresh nonces ri, rj, rk are 256 bits drawn from OS CSPRNG (os.urandom(32)). Collisions occur with probability ≤ 2^-128.',
          formalProof: 'Guaranteed pseudo-random uniqueness under Birthday bound.'
        };
      case 'session_key_agreement':
        return {
          dolevYao: 'Evaluates legitimate session key convergence under uncorrupted channels.',
          defenseMechanism: 'Both User and Cloud Server derive identical 256-bit SK = H(SIDi ∥ SIDj ∥ ri ∥ rj ∥ rk).',
          formalProof: 'Positive control baseline ensuring protocol correctness.'
        };
      default:
        return {
          dolevYao: 'Simulated adversary capability against protocol state.',
          defenseMechanism: 'Cryptographic binding and HMAC validation.',
          formalProof: 'Paper formal evaluation.'
        };
    }
  };

  const filteredResults = report?.results.filter((r: any) => {
    if (filter === 'high') return r.severity === 'high';
    return true;
  });

  return (
    <div className="space-y-6">
      <header className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Security Lab</h1>
          <p className="text-gray-500 mt-2">Automated cryptographic attack simulations & Dolev-Yao threat resistance</p>
        </div>
        <button
          onClick={runSecurityTests}
          disabled={loading}
          className="bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg px-5 py-2.5 flex items-center transition-all shadow-sm hover:shadow disabled:opacity-50"
        >
          {loading ? <Clock className="animate-spin mr-2" size={18}/> : <Play className="mr-2" size={18}/>}
          Run Threat Engine
        </button>
      </header>

      {error && (
        <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-200">
          {error}
        </div>
      )}

      {report && (
        <div className="space-y-6">
          {/* Summary Metric Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 text-center">
              <div className="text-4xl font-extrabold text-gray-900 mb-1">{report.total}</div>
              <div className="text-gray-500 font-semibold text-xs uppercase tracking-wider">Total Attack Scenarios</div>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-sm border border-green-200 text-center bg-green-50/20">
              <div className="text-4xl font-extrabold text-green-600 mb-1">{report.passed}</div>
              <div className="text-green-700 font-semibold text-xs uppercase tracking-wider">Attacks Resisted (PASS)</div>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-sm border border-red-200 text-center bg-red-50/20">
              <div className="text-4xl font-extrabold text-red-600 mb-1">{report.failed}</div>
              <div className="text-red-700 font-semibold text-xs uppercase tracking-wider">Breaches Detected (FAIL)</div>
            </div>
          </div>

          {/* Academic Integrity Alert */}
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-xs text-amber-900 flex items-start gap-3">
            <AlertTriangle size={18} className="text-amber-600 shrink-0 mt-0.5" />
            <div>
              <strong className="font-semibold block mb-0.5">Faculty Evaluation & Academic Notice:</strong>
              {report.disclaimer} An empirical test status of <strong>PASS</strong> confirms that the implementation successfully repelled the simulated exploit scenario in code. Formal proofs of provable security (RoR Model / BAN Logic) are maintained separately in <span className="font-mono text-amber-800">docs/security-analysis.md</span>.
            </div>
          </div>

          {/* Results Table & Filter */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
              <h3 className="font-semibold text-sm text-gray-900 flex items-center gap-2">
                <FileCheck2 size={16} className="text-blue-600" />
                Attack Vector Results Table
              </h3>

              <div className="flex gap-1.5 bg-white p-1 rounded-lg border border-gray-200 text-xs font-medium">
                <button
                  onClick={() => setFilter('all')}
                  className={`px-2.5 py-1 rounded transition-colors ${filter === 'all' ? 'bg-blue-600 text-white font-bold' : 'text-gray-600 hover:text-gray-900'}`}
                >
                  All ({report.total})
                </button>
                <button
                  onClick={() => setFilter('high')}
                  className={`px-2.5 py-1 rounded transition-colors ${filter === 'high' ? 'bg-blue-600 text-white font-bold' : 'text-gray-600 hover:text-gray-900'}`}
                >
                  High Severity
                </button>
              </div>
            </div>

            <table className="min-w-full divide-y divide-gray-200 text-xs">
              <thead className="bg-gray-50 text-gray-600 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-3 text-left">Attack Vector</th>
                  <th className="px-6 py-3 text-left">Outcome</th>
                  <th className="px-6 py-3 text-left">Evidence & Log</th>
                  <th className="px-6 py-3 text-left">Severity</th>
                  <th className="px-4 py-3 text-center"></th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-100">
                {filteredResults.map((r: any, idx: number) => {
                  const isSelected = selectedTest === r.test;
                  const context = getAdversaryContext(r.test);
                  return (
                    <React.Fragment key={idx}>
                      <tr 
                        onClick={() => setSelectedTest(isSelected ? null : r.test)}
                        className={`cursor-pointer transition-colors ${isSelected ? 'bg-blue-50/70' : 'hover:bg-gray-50'}`}
                      >
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="font-bold text-gray-900 text-xs">{r.test.replace(/_/g, ' ').toUpperCase()}</div>
                          <div className="text-[11px] text-gray-500 max-w-xs truncate mt-0.5">{r.description}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {r.status === 'PASS' ? (
                            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800 border border-green-200">
                              <ShieldCheck size={14} className="mr-1 text-green-600"/> PASS
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-800 border border-red-200">
                              <ShieldAlert size={14} className="mr-1 text-red-600"/> FAIL
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-gray-800 text-xs leading-relaxed max-w-md">{r.evidence}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold uppercase ${
                            r.severity === 'high' ? 'bg-red-100 text-red-700 border border-red-200' : 'bg-yellow-100 text-yellow-800 border border-yellow-200'
                          }`}>
                            {r.severity}
                          </span>
                        </td>
                        <td className="px-4 py-4 text-center text-gray-400">
                          {isSelected ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                        </td>
                      </tr>

                      {/* Expandable Dolev-Yao Threat Context Panel */}
                      {isSelected && (
                        <tr>
                          <td colSpan={5} className="px-6 py-4 bg-slate-900 text-slate-200 border-y border-slate-800 text-xs">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                              <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700/70">
                                <span className="font-semibold text-amber-400 block mb-1">Dolev-Yao Adversary Vector:</span>
                                <p className="text-slate-300 text-[11px] leading-relaxed">{context.dolevYao}</p>
                              </div>
                              <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700/70">
                                <span className="font-semibold text-emerald-400 block mb-1">Protocol Defense Mechanism:</span>
                                <p className="text-slate-300 text-[11px] leading-relaxed">{context.defenseMechanism}</p>
                              </div>
                              <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700/70">
                                <span className="font-semibold text-blue-400 block mb-1">Formal Literature Context:</span>
                                <p className="text-slate-300 text-[11px] leading-relaxed">{context.formalProof}</p>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
