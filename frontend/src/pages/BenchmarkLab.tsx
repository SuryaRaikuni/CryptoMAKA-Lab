import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { 
  Play, 
  Clock, 
  BarChart2, 
  Activity, 
  Zap, 
  Info, 
  Wifi, 
  Battery, 
  Cpu, 
  Radio, 
  AlertTriangle, 
  Layers, 
  Sliders 
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';

export default function BenchmarkLab() {
  const [activeMode, setActiveMode] = useState<'cpu_benchmarks' | 'iot_wireless'>('cpu_benchmarks');

  // --- CPU Benchmark State ---
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<any>(null);
  const [error, setError] = useState('');
  const [activeChart, setActiveChart] = useState<'latency' | 'throughput' | 'communication'>('latency');
  const [iterations, setIterations] = useState(100);

  // --- IoT Wireless & Energy State ---
  const [networkProfile, setNetworkProfile] = useState<string>('nbiot');
  const [hardwareProfile, setHardwareProfile] = useState<string>('cortex_m4');
  const [handshakesPerDay, setHandshakesPerDay] = useState<number>(24);
  const [batteryCapacity, setBatteryCapacity] = useState<number>(220);
  const [energyReport, setEnergyReport] = useState<any>(null);
  const [energyLoading, setEnergyLoading] = useState<boolean>(false);
  const [energyError, setEnergyError] = useState<string>('');
  const [energyChartType, setEnergyChartType] = useState<'latency_stacked' | 'energy_split' | 'battery_life'>('latency_stacked');

  // Fetch energy simulation on initial load or parameter change
  useEffect(() => {
    if (activeMode === 'iot_wireless' && !energyReport) {
      runEnergySimulation();
    }
  }, [activeMode]);

  const runComparison = async (count = iterations) => {
    setLoading(true);
    setError('');
    try {
      const data = await api.post('/benchmarks/compare', {
        protocols: ['ju_park', 'ecc', 'reduced_roundtrip', 'ml_kem'],
        iterations: count,
        warmup: 10
      });
      setReport(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const runEnergySimulation = async () => {
    setEnergyLoading(true);
    setEnergyError('');
    try {
      const data = await api.post('/benchmarks/network-energy/simulate', {
        network_profile: networkProfile,
        hardware_profile: hardwareProfile,
        handshakes_per_day: handshakesPerDay,
        battery_capacity_mah: batteryCapacity
      });
      setEnergyReport(data);
    } catch (err: any) {
      setEnergyError(err.message || 'Simulation error');
    } finally {
      setEnergyLoading(false);
    }
  };

  const getProtocolLabel = (proto: string) => {
    switch (proto) {
      case 'ju_park': return 'Ju-Park 2023';
      case 'ecc': return 'ECC P-256';
      case 'reduced_roundtrip': return 'Reduced-RTT';
      case 'ml_kem': return 'ML-KEM-768 (PQ)';
      default: return proto;
    }
  };

  const getLatencyChartData = () => {
    if (!report) return [];
    return report.results.map((r: any) => ({
      name: getProtocolLabel(r.protocol),
      'Mean (ms)': Number(r.total.mean_ms.toFixed(3)),
      'Min (ms)': Number(r.total.min_ms.toFixed(3)),
      'Max (ms)': Number(r.total.max_ms.toFixed(3)),
    }));
  };

  const getThroughputChartData = () => {
    if (!report) return [];
    return report.results.map((r: any) => ({
      name: getProtocolLabel(r.protocol),
      'Throughput (ops/sec)': Math.round(r.total.throughput_ops_per_sec),
    }));
  };

  const getCommChartData = () => {
    return [
      { name: 'Ju-Park (Paper Ref)', 'Bits': 3776, type: 'Published Reference' },
      { name: 'Ju-Park (Normalized)', 'Bits': 4224, type: 'Normalized Measurement' },
      { name: 'ECC P-256', 'Bits': 1872, type: 'Implementation Measurement' },
      { name: 'Proposed Extension', 'Bits': 3616, type: 'Implementation Measurement' },
      { name: 'ML-KEM-768 (FIPS 203)', 'Bits': 38656, type: 'Post-Quantum Baseline' },
    ];
  };

  // IoT Energy Chart Data
  const getEnergyLatencyData = () => {
    if (!energyReport) return [];
    return Object.keys(energyReport.results).map((k) => {
      const item = energyReport.results[k];
      return {
        name: getProtocolLabel(k),
        'Computation (ms)': item.compute_time_ms,
        'Wireless Network (ms)': item.network_latency_ms,
        'Total (ms)': item.total_latency_ms,
      };
    });
  };

  const getEnergySplitData = () => {
    if (!energyReport) return [];
    return Object.keys(energyReport.results).map((k) => {
      const item = energyReport.results[k];
      return {
        name: getProtocolLabel(k),
        'CPU Energy (μJ)': item.cpu_energy_uj,
        'Radio TX/RX Energy (μJ)': item.radio_energy_uj,
        'Total Energy (mJ)': item.total_energy_mj,
      };
    });
  };

  const getBatteryLifeData = () => {
    if (!energyReport) return [];
    return Object.keys(energyReport.results).map((k) => {
      const item = energyReport.results[k];
      return {
        name: getProtocolLabel(k),
        'Battery Lifetime (Years)': item.estimated_battery_lifetime_years,
      };
    });
  };

  return (
    <div className="space-y-6">
      {/* Header and Mode Toggle */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Benchmark Lab</h1>
          <p className="text-gray-500 mt-2">Empirical micro-timing, wireless channel propagation, and microjoule energy modeling</p>
        </div>

        {/* Mode Toggle Navigation */}
        <div className="flex bg-white p-1 rounded-xl border border-gray-200 shadow-2xs text-xs font-semibold">
          <button
            onClick={() => setActiveMode('cpu_benchmarks')}
            className={`px-4 py-2 rounded-lg transition-all flex items-center gap-1.5 ${
              activeMode === 'cpu_benchmarks'
                ? 'bg-indigo-600 text-white shadow-sm font-bold'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Cpu size={14} />
            Host CPU Benchmarks (ms)
          </button>
          <button
            onClick={() => {
              setActiveMode('iot_wireless');
              if (!energyReport) runEnergySimulation();
            }}
            className={`px-4 py-2 rounded-lg transition-all flex items-center gap-1.5 ${
              activeMode === 'iot_wireless'
                ? 'bg-indigo-600 text-white shadow-sm font-bold'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Wifi size={14} />
            IoT Wireless & Energy Lab (μJ)
          </button>
        </div>
      </header>

      {/* ──────────────────────────────────────────────────────────── */}
      {/* MODE 1: HOST CPU BENCHMARKS */}
      {/* ──────────────────────────────────────────────────────────── */}
      {activeMode === 'cpu_benchmarks' && (
        <div className="space-y-6">
          {/* Controls Bar */}
          <div className="flex flex-wrap justify-between items-center gap-3 bg-white p-4 rounded-xl border border-gray-200 shadow-2xs">
            <div className="flex items-center gap-2 text-xs text-gray-600 font-medium">
              <span>Preset Iterations:</span>
              {[50, 100, 500].map((n) => (
                <button
                  key={n}
                  onClick={() => setIterations(n)}
                  className={`px-2.5 py-1 rounded text-xs transition-colors ${
                    iterations === n 
                      ? 'bg-blue-600 text-white font-bold' 
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {n}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-2">
              <input 
                type="number" 
                value={iterations}
                onChange={(e) => setIterations(Math.max(1, parseInt(e.target.value) || 10))}
                className="border border-gray-300 rounded-lg px-2.5 py-1.5 w-24 text-xs font-mono"
                min="1" 
                max="10000"
              />
              <button
                onClick={() => runComparison()}
                disabled={loading}
                className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg px-4 py-1.5 text-xs flex items-center transition-all shadow-sm hover:shadow disabled:opacity-50"
              >
                {loading ? <Clock className="animate-spin mr-1.5" size={14}/> : <Play className="mr-1.5" size={14}/>}
                Run Benchmark
              </button>
            </div>
          </div>

          {/* Academic Methodology Callout */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-xs text-blue-900 leading-relaxed flex items-start gap-3">
            <Info size={18} className="text-blue-600 shrink-0 mt-0.5" />
            <div>
              <strong className="font-semibold block mb-0.5">Benchmarking Methodology Guarantee:</strong>
              Timings are collected using Python's high-resolution monotonic hardware counter (<code className="bg-blue-100 px-1 py-0.5 rounded font-mono">perf_counter_ns</code>). 
              Every trial includes 10 warmup runs to eliminate CPU frequency governor jitter. The published paper's 3,776-bit cost is preserved strictly as an authoritative literature baseline and never merged into empirical runtime measurements.
            </div>
          </div>

          {error && (
            <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-200 text-xs">
              {error}
            </div>
          )}

          {report && (
            <div className="space-y-6">
              {/* Charts Card */}
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
                  <h2 className="text-lg font-bold text-gray-900 flex items-center">
                    {activeChart === 'latency' && <><BarChart2 className="mr-2 text-indigo-600" /> Latency Comparison (ms)</>}
                    {activeChart === 'throughput' && <><Activity className="mr-2 text-emerald-600" /> Throughput Comparison (ops/sec)</>}
                    {activeChart === 'communication' && <><Zap className="mr-2 text-amber-500" /> Communication Overhead (bits)</>}
                  </h2>

                  <div className="flex bg-gray-100 p-1 rounded-lg text-xs font-medium">
                    <button
                      onClick={() => setActiveChart('latency')}
                      className={`px-3 py-1 rounded-md transition-colors ${
                        activeChart === 'latency' ? 'bg-white text-gray-900 shadow-2xs font-bold' : 'text-gray-600 hover:text-gray-900'
                      }`}
                    >
                      Latency (ms)
                    </button>
                    <button
                      onClick={() => setActiveChart('throughput')}
                      className={`px-3 py-1 rounded-md transition-colors ${
                        activeChart === 'throughput' ? 'bg-white text-gray-900 shadow-2xs font-bold' : 'text-gray-600 hover:text-gray-900'
                      }`}
                    >
                      Throughput
                    </button>
                    <button
                      onClick={() => setActiveChart('communication')}
                      className={`px-3 py-1 rounded-md transition-colors ${
                        activeChart === 'communication' ? 'bg-white text-gray-900 shadow-2xs font-bold' : 'text-gray-600 hover:text-gray-900'
                      }`}
                    >
                      Communication Bits
                    </button>
                  </div>
                </div>

                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    {activeChart === 'latency' ? (
                      <BarChart data={getLatencyChartData()} margin={{ top: 10, right: 30, left: 10, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                        <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                        <YAxis unit=" ms" tick={{ fontSize: 12 }} />
                        <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                        <Legend wrapperStyle={{ fontSize: 12 }} />
                        <Bar dataKey="Mean (ms)" fill="#4f46e5" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="Min (ms)" fill="#10b981" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="Max (ms)" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    ) : activeChart === 'throughput' ? (
                      <BarChart data={getThroughputChartData()} margin={{ top: 10, right: 30, left: 10, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                        <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                        <YAxis unit=" ops" tick={{ fontSize: 12 }} />
                        <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                        <Legend wrapperStyle={{ fontSize: 12 }} />
                        <Bar dataKey="Throughput (ops/sec)" fill="#059669" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    ) : (
                      <BarChart data={getCommChartData()} margin={{ top: 10, right: 30, left: 10, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                        <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                        <YAxis unit=" b" tick={{ fontSize: 12 }} />
                        <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                        <Legend wrapperStyle={{ fontSize: 12 }} />
                        <Bar dataKey="Bits" fill="#d97706" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    )}
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Statistical Metrics Table */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div className="p-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
                  <h3 className="font-semibold text-sm text-gray-900">Statistical Measurements ({report.iterations} Iterations + 10 Warmups)</h3>
                  <span className="text-xs text-gray-500 font-mono">Platform: {report.host_metadata.system} {report.host_metadata.machine}</span>
                </div>

                <table className="min-w-full divide-y divide-gray-200 text-xs">
                  <thead className="bg-gray-50 font-semibold text-gray-600">
                    <tr>
                      <th className="px-5 py-3 text-left">Protocol</th>
                      <th className="px-5 py-3 text-right">Mean Latency</th>
                      <th className="px-5 py-3 text-right">Median</th>
                      <th className="px-5 py-3 text-right">Min / Max</th>
                      <th className="px-5 py-3 text-right">StdDev</th>
                      <th className="px-5 py-3 text-right">Throughput</th>
                      <th className="px-5 py-3 text-right">Comm Bits</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-100 font-mono">
                    {report.results.map((r: any, idx: number) => (
                      <tr key={idx} className="hover:bg-gray-50 font-sans">
                        <td className="px-5 py-3.5 whitespace-nowrap font-medium text-gray-900">
                          {getProtocolLabel(r.protocol)}
                        </td>
                        <td className="px-5 py-3.5 whitespace-nowrap text-right font-mono font-semibold text-indigo-700">
                          {r.total.mean_ms.toFixed(3)} ms
                        </td>
                        <td className="px-5 py-3.5 whitespace-nowrap text-right font-mono text-gray-700">
                          {r.total.median_ms ? `${r.total.median_ms.toFixed(3)} ms` : '-'}
                        </td>
                        <td className="px-5 py-3.5 whitespace-nowrap text-right font-mono text-gray-500">
                          {r.total.min_ms.toFixed(3)} / {r.total.max_ms.toFixed(3)}
                        </td>
                        <td className="px-5 py-3.5 whitespace-nowrap text-right font-mono text-gray-500">
                          ±{r.total.stddev_ms.toFixed(3)} ms
                        </td>
                        <td className="px-5 py-3.5 whitespace-nowrap text-right font-mono text-emerald-700 font-bold">
                          {Math.round(r.total.throughput_ops_per_sec)} ops/s
                        </td>
                        <td className="px-5 py-3.5 whitespace-nowrap text-right font-mono text-gray-800">
                          {r.communication_bits ? `${r.communication_bits} b` : '3,616 b'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ──────────────────────────────────────────────────────────── */}
      {/* MODE 2: IOT WIRELESS CHANNEL & ENERGY LAB */}
      {/* ──────────────────────────────────────────────────────────── */}
      {activeMode === 'iot_wireless' && (
        <div className="space-y-6">
          {/* Cyber-Physical Simulation Header Banner */}
          <div className="bg-gradient-to-r from-slate-900 via-teal-950 to-slate-900 text-white p-6 rounded-2xl shadow-md border border-teal-900/40 relative overflow-hidden">
            <div className="relative z-10 space-y-3">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2.5">
                  <span className="p-2 bg-teal-600/30 rounded-xl border border-teal-500/30 text-teal-300">
                    <Radio size={20} />
                  </span>
                  <div>
                    <h2 className="text-lg font-bold text-white flex items-center gap-2">
                      Cyber-Physical Wireless & Energy Modeling Lab
                      <span className="text-xs px-2.5 py-0.5 rounded-full bg-teal-500/20 text-teal-300 border border-teal-400/30 font-medium">
                        LPWAN / Cellular IoT
                      </span>
                    </h2>
                    <p className="text-xs text-teal-200">
                      Evaluates the real-world impact of bandwidth constraints, MTU packet fragmentation, radio TX/RX power, and battery exhaustion.
                    </p>
                  </div>
                </div>

                <button
                  onClick={runEnergySimulation}
                  disabled={energyLoading}
                  className="bg-teal-600 hover:bg-teal-500 text-white font-bold rounded-xl px-4 py-2 text-xs flex items-center gap-2 transition-all shadow-sm hover:shadow disabled:opacity-50"
                >
                  {energyLoading ? <Clock className="animate-spin" size={14} /> : <Sliders size={14} />}
                  Recalculate Channel & Energy
                </button>
              </div>

              <div className="text-xs text-slate-300 leading-relaxed bg-black/20 p-3 rounded-xl border border-white/5">
                <strong className="text-white">Research Takeaway:</strong> In constrained networks like LoRaWAN, post-quantum KEMs (ML-KEM-768) require <strong>dozens of packet fragments</strong> over restricted MTUs (51–115B), multiplying handshake latency by 10x–50x. Lightweight symmetric schemes (Ju-Park) excel precisely in these edge environments.
              </div>
            </div>
          </div>

          {energyError && (
            <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-200 text-xs">
              {energyError}
            </div>
          )}

          {/* Interactive Parameter Control Deck */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 bg-white p-5 rounded-xl border border-gray-200 shadow-2xs">
            {/* 1. Network Profile */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-gray-700 flex items-center gap-1.5">
                <Wifi size={14} className="text-blue-600" />
                Wireless Network
              </label>
              <select
                value={networkProfile}
                onChange={(e) => setNetworkProfile(e.target.value)}
                className="w-full bg-gray-50 border border-gray-300 rounded-lg px-3 py-2 text-xs font-medium text-gray-900 focus:ring-2 focus:ring-blue-500"
              >
                <option value="lorawan_dr0">LoRaWAN EU868 DR0 (250 bps, 51B MTU)</option>
                <option value="lorawan_dr3">LoRaWAN EU868 DR3 (1.76 kbps, 115B MTU)</option>
                <option value="nbiot">NB-IoT Cat-NB1 (64 kbps, 350ms RTT)</option>
                <option value="ltem">LTE-M Cat-M1 (1 Mbps, 85ms RTT)</option>
                <option value="fiveg_iot">5G Industrial URLLC (50 Mbps, 4ms RTT)</option>
                <option value="lan_unconstrained">Local LAN (1 Gbps Unconstrained)</option>
              </select>
            </div>

            {/* 2. Embedded MCU Hardware */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-gray-700 flex items-center gap-1.5">
                <Cpu size={14} className="text-purple-600" />
                Embedded MCU Profile
              </label>
              <select
                value={hardwareProfile}
                onChange={(e) => setHardwareProfile(e.target.value)}
                className="w-full bg-gray-50 border border-gray-300 rounded-lg px-3 py-2 text-xs font-medium text-gray-900 focus:ring-2 focus:ring-blue-500"
              >
                <option value="cortex_m4">ARM Cortex-M4 @ 64MHz (STM32L4, 3.0V)</option>
                <option value="esp32">Espressif ESP32 @ 160MHz (3.3V)</option>
                <option value="rpi_zero">Raspberry Pi Zero W @ 1GHz (5.0V)</option>
              </select>
            </div>

            {/* 3. Handshakes per day */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-gray-700 flex items-center gap-1.5">
                <Clock size={14} className="text-amber-600" />
                Duty Cycle (Handshakes/Day)
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  min="1"
                  max="1440"
                  value={handshakesPerDay}
                  onChange={(e) => setHandshakesPerDay(Math.max(1, parseInt(e.target.value) || 24))}
                  className="w-full bg-gray-50 border border-gray-300 rounded-lg px-3 py-2 text-xs font-mono text-gray-900"
                />
                <span className="text-[11px] text-gray-500 whitespace-nowrap">
                  ({(1440 / handshakesPerDay).toFixed(0)}m interval)
                </span>
              </div>
            </div>

            {/* 4. Battery Capacity */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-gray-700 flex items-center gap-1.5">
                <Battery size={14} className="text-emerald-600" />
                Battery Capacity (mAh)
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  min="10"
                  max="10000"
                  value={batteryCapacity}
                  onChange={(e) => setBatteryCapacity(Math.max(10, parseInt(e.target.value) || 220))}
                  className="w-full bg-gray-50 border border-gray-300 rounded-lg px-3 py-2 text-xs font-mono text-gray-900"
                />
                <span className="text-[11px] text-gray-500 whitespace-nowrap">
                  {batteryCapacity <= 300 ? 'Coin Cell' : 'Pack'}
                </span>
              </div>
            </div>
          </div>

          {/* Dynamic Simulation Output */}
          {energyReport && (
            <div className="space-y-6">
              {/* Network Channel Live Status Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-2xs">
                  <div className="text-[11px] uppercase tracking-wider font-semibold text-gray-500">Channel Bandwidth</div>
                  <div className="text-xl font-bold text-gray-900 mt-0.5">
                    {energyReport.network_profile.bandwidth_kbps >= 1000
                      ? `${(energyReport.network_profile.bandwidth_kbps / 1000).toFixed(1)} Mbps`
                      : `${energyReport.network_profile.bandwidth_kbps} kbps`}
                  </div>
                  <div className="text-[11px] text-gray-500 mt-1">{energyReport.network_profile.technology}</div>
                </div>

                <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-2xs">
                  <div className="text-[11px] uppercase tracking-wider font-semibold text-gray-500">Propagation Delay (RTT)</div>
                  <div className="text-xl font-bold text-indigo-600 mt-0.5">
                    {energyReport.network_profile.base_rtt_ms} ms
                  </div>
                  <div className="text-[11px] text-gray-500 mt-1">One-way transmission base</div>
                </div>

                <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-2xs">
                  <div className="text-[11px] uppercase tracking-wider font-semibold text-gray-500">Payload MTU Limit</div>
                  <div className="text-xl font-bold text-amber-600 mt-0.5">
                    {energyReport.network_profile.mtu_bytes} Bytes
                  </div>
                  <div className="text-[11px] text-gray-500 mt-1">Fragment threshold per packet</div>
                </div>

                <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-2xs">
                  <div className="text-[11px] uppercase tracking-wider font-semibold text-gray-500">MCU Power Budget</div>
                  <div className="text-xl font-bold text-emerald-600 mt-0.5">
                    {energyReport.hardware_profile.voltage}V @ {energyReport.hardware_profile.clock_mhz}MHz
                  </div>
                  <div className="text-[11px] text-gray-500 mt-1">
                    TX: {energyReport.hardware_profile.radio_tx_ma}mA · CPU: {energyReport.hardware_profile.active_cpu_ma}mA
                  </div>
                </div>
              </div>

              {/* Chart Selector and Visualizations */}
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 space-y-4">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 pb-3 border-b border-gray-200">
                  <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2">
                    <BarChart2 className="text-teal-600" size={16} />
                    {energyChartType === 'latency_stacked' && 'End-to-End Handshake Latency Breakdown (Computation vs Wireless Radio)'}
                    {energyChartType === 'energy_split' && 'Energy Consumption Breakdown per Handshake (μJ)'}
                    {energyChartType === 'battery_life' && `Projected Device Battery Lifespan (${batteryCapacity} mAh @ ${handshakesPerDay} handshakes/day)`}
                  </h3>

                  <div className="flex bg-gray-100 p-1 rounded-lg text-xs font-semibold">
                    <button
                      onClick={() => setEnergyChartType('latency_stacked')}
                      className={`px-3 py-1.5 rounded-md transition-all ${
                        energyChartType === 'latency_stacked' ? 'bg-white text-gray-900 shadow-2xs font-bold' : 'text-gray-600 hover:text-gray-900'
                      }`}
                    >
                      Latency (ms)
                    </button>
                    <button
                      onClick={() => setEnergyChartType('energy_split')}
                      className={`px-3 py-1.5 rounded-md transition-all ${
                        energyChartType === 'energy_split' ? 'bg-white text-gray-900 shadow-2xs font-bold' : 'text-gray-600 hover:text-gray-900'
                      }`}
                    >
                      Energy (μJ)
                    </button>
                    <button
                      onClick={() => setEnergyChartType('battery_life')}
                      className={`px-3 py-1.5 rounded-md transition-all ${
                        energyChartType === 'battery_life' ? 'bg-white text-gray-900 shadow-2xs font-bold' : 'text-gray-600 hover:text-gray-900'
                      }`}
                    >
                      Battery Lifespan
                    </button>
                  </div>
                </div>

                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    {energyChartType === 'latency_stacked' ? (
                      <BarChart data={getEnergyLatencyData()} margin={{ top: 20, right: 30, left: 10, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                        <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                        <YAxis unit=" ms" tick={{ fontSize: 12 }} />
                        <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                        <Legend wrapperStyle={{ fontSize: 12 }} />
                        <Bar dataKey="Computation (ms)" stackId="a" fill="#3b82f6" radius={[0, 0, 0, 0]} />
                        <Bar dataKey="Wireless Network (ms)" stackId="a" fill="#0d9488" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    ) : energyChartType === 'energy_split' ? (
                      <BarChart data={getEnergySplitData()} margin={{ top: 20, right: 30, left: 10, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                        <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                        <YAxis unit=" μJ" tick={{ fontSize: 12 }} />
                        <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                        <Legend wrapperStyle={{ fontSize: 12 }} />
                        <Bar dataKey="CPU Energy (μJ)" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="Radio TX/RX Energy (μJ)" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    ) : (
                      <BarChart data={getBatteryLifeData()} margin={{ top: 20, right: 30, left: 10, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                        <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                        <YAxis unit=" Yrs" tick={{ fontSize: 12 }} />
                        <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                        <Legend wrapperStyle={{ fontSize: 12 }} />
                        <Bar dataKey="Battery Lifetime (Years)" fill="#10b981" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    )}
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Detailed Quantitative IoT Comparison Table */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div className="p-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
                  <h3 className="font-semibold text-sm text-gray-900 flex items-center gap-2">
                    <Layers size={16} className="text-teal-600" />
                    Cyber-Physical Handshake Simulation Breakdown
                  </h3>
                  <span className="text-xs text-gray-500 font-mono">
                    Channel: {energyReport.network_profile.name} · Target MCU: {energyReport.hardware_profile.name}
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200 text-xs">
                    <thead className="bg-gray-50 font-semibold text-gray-600">
                      <tr>
                        <th className="px-4 py-3 text-left">Protocol</th>
                        <th className="px-3 py-3 text-right">Wire Size</th>
                        <th className="px-3 py-3 text-right">Flows</th>
                        <th className="px-3 py-3 text-center">MTU Fragments</th>
                        <th className="px-4 py-3 text-right">CPU Time</th>
                        <th className="px-4 py-3 text-right">Network Latency</th>
                        <th className="px-4 py-3 text-right">Total Latency</th>
                        <th className="px-4 py-3 text-right">Radio Energy</th>
                        <th className="px-4 py-3 text-right">Total Energy</th>
                        <th className="px-4 py-3 text-right">Battery Lifespan</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-100">
                      {Object.keys(energyReport.results).map((k) => {
                        const row = energyReport.results[k];
                        const isSevere = row.total_fragments > 10;
                        return (
                          <tr key={k} className="hover:bg-gray-50/80 transition-colors">
                            <td className="px-4 py-3.5 font-bold text-gray-900 whitespace-nowrap">
                              {row.protocol_name}
                              {row.duty_cycle_warning && (
                                <div className="text-[10px] text-amber-700 font-normal mt-0.5 flex items-center gap-1">
                                  <AlertTriangle size={11} className="shrink-0 text-amber-600" />
                                  <span>{row.duty_cycle_warning}</span>
                                </div>
                              )}
                            </td>
                            <td className="px-3 py-3.5 text-right font-mono text-gray-700 whitespace-nowrap">
                              {row.total_wire_bytes} B
                            </td>
                            <td className="px-3 py-3.5 text-right font-mono text-gray-600 whitespace-nowrap">
                              {row.message_count} msgs
                            </td>
                            <td className="px-3 py-3.5 text-center whitespace-nowrap">
                              <span className={`px-2 py-0.5 rounded-full font-mono text-[11px] font-bold ${
                                isSevere
                                  ? 'bg-red-100 text-red-800 border border-red-200'
                                  : row.mtu_exceeded
                                  ? 'bg-amber-100 text-amber-800'
                                  : 'bg-green-100 text-green-800'
                              }`}>
                                {row.total_fragments} {row.total_fragments === 1 ? 'pkt' : 'pkts'}
                              </span>
                            </td>
                            <td className="px-4 py-3.5 text-right font-mono text-gray-600 whitespace-nowrap">
                              {row.compute_time_ms} ms
                            </td>
                            <td className="px-4 py-3.5 text-right font-mono font-medium text-teal-700 whitespace-nowrap">
                              {row.network_latency_ms >= 1000
                                ? `${(row.network_latency_ms / 1000).toFixed(2)} s`
                                : `${row.network_latency_ms.toFixed(1)} ms`}
                            </td>
                            <td className="px-4 py-3.5 text-right font-mono font-bold text-gray-900 whitespace-nowrap">
                              {row.total_latency_ms >= 1000
                                ? `${(row.total_latency_ms / 1000).toFixed(2)} s`
                                : `${row.total_latency_ms.toFixed(1)} ms`}
                            </td>
                            <td className="px-4 py-3.5 text-right font-mono text-amber-700 whitespace-nowrap">
                              {row.radio_energy_uj.toLocaleString()} μJ
                            </td>
                            <td className="px-4 py-3.5 text-right font-mono font-bold text-indigo-700 whitespace-nowrap">
                              {row.total_energy_mj >= 1.0
                                ? `${row.total_energy_mj.toFixed(2)} mJ`
                                : `${row.total_energy_uj.toFixed(0)} μJ`}
                            </td>
                            <td className="px-4 py-3.5 text-right font-mono font-bold text-emerald-700 whitespace-nowrap">
                              {row.estimated_battery_lifetime_years} Years
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
