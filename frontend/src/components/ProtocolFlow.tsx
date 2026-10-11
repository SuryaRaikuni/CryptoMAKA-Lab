import React from 'react';
import { ArrowRight, ArrowLeft, Shield, Server, Laptop } from 'lucide-react';

export interface ProtocolMessage {
  name: string;
  direction: string;
  size_bits: number;
  note?: string;
}

interface ProtocolFlowProps {
  protocolId: string;
  messages: ProtocolMessage[];
}

export const ProtocolFlow: React.FC<ProtocolFlowProps> = ({ protocolId, messages }) => {
  const getPartyOffset = (direction: string) => {
    const dir = direction.toLowerCase();
    if (dir.includes('user') && dir.includes('cloud') && !dir.includes('control')) {
      if (dir.includes('cloud → user') || dir.includes('cloud->user')) {
        return { from: 'Cloud', to: 'User', arrow: 'left-user-cloud' };
      }
      return { from: 'User', to: 'Cloud', arrow: 'right-user-cloud' };
    }
    if (dir.includes('cloud') && (dir.includes('control') || dir.includes('cs') || dir.includes('rc'))) {
      if (dir.includes('control → cloud') || dir.includes('cs → cloud') || dir.includes('rc → cloud')) {
        return { from: 'Control Server', to: 'Cloud', arrow: 'left-cloud-cs' };
      }
      return { from: 'Cloud', to: 'Control Server', arrow: 'right-cloud-cs' };
    }
    if (dir.includes('user') && (dir.includes('control') || dir.includes('rc'))) {
      return { from: 'User', to: 'Control Server', arrow: 'right-user-cs' };
    }
    return { from: 'Origin', to: 'Destination', arrow: 'generic' };
  };

  return (
    <div className="bg-slate-900 rounded-xl p-6 text-white border border-slate-800 shadow-lg my-6">
      <div className="flex justify-between items-center mb-6 border-b border-slate-800 pb-4">
        <div>
          <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
            Interactive Protocol Sequence Diagram
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            {protocolId === 'ju_park' && 'Ju-Park 2023 Normalized 3-Party Hash/XOR Authentication Exchange'}
            {protocolId === 'ecc' && 'NIST P-256 Ephemeral ECDH Counterpart Exchange'}
            {protocolId === 'reduced_roundtrip' && 'Proposed 3-Message Reduced-Round-Trip Extension (Cloud Relaying Combined M3)'}
          </p>
        </div>
        <span className="px-2.5 py-1 text-xs font-mono rounded bg-slate-800 text-blue-400 border border-slate-700">
          {messages.length} Steps
        </span>
      </div>

      {/* Lifeline Headers */}
      <div className="grid grid-cols-3 gap-4 text-center mb-8 relative">
        <div className="flex flex-col items-center">
          <div className="w-12 h-12 rounded-xl bg-blue-500/20 text-blue-400 border border-blue-500/40 flex items-center justify-center mb-2 shadow-inner">
            <Laptop size={24} />
          </div>
          <span className="font-semibold text-sm text-slate-200">User / IoT Node</span>
          <span className="text-[11px] text-slate-400 font-mono">(Smart Card, $U_i$)</span>
        </div>

        <div className="flex flex-col items-center">
          <div className="w-12 h-12 rounded-xl bg-indigo-500/20 text-indigo-400 border border-indigo-500/40 flex items-center justify-center mb-2 shadow-inner">
            <Server size={24} />
          </div>
          <span className="font-semibold text-sm text-slate-200">Cloud Server</span>
          <span className="text-[11px] text-slate-400 font-mono">(Service Provider, $S_j$)</span>
        </div>

        <div className="flex flex-col items-center">
          <div className="w-12 h-12 rounded-xl bg-purple-500/20 text-purple-400 border border-purple-500/40 flex items-center justify-center mb-2 shadow-inner">
            <Shield size={24} />
          </div>
          <span className="font-semibold text-sm text-slate-200">Control Server</span>
          <span className="text-[11px] text-slate-400 font-mono">(Trusted Registrar, $CS$)</span>
        </div>
      </div>

      {/* Messages Timeline */}
      <div className="space-y-6 relative py-4 before:absolute before:inset-0 before:left-1/6 before:right-1/6 before:bg-transparent">
        {messages.map((msg, idx) => {
          const { from, to } = getPartyOffset(msg.direction);
          const isLeftToRight = msg.direction.includes('User → Cloud') || msg.direction.includes('Cloud → Control');
          
          return (
            <div key={idx} className="relative bg-slate-800/80 hover:bg-slate-800 border border-slate-700/80 rounded-lg p-4 transition-all">
              <div className="flex items-center justify-between gap-4 mb-2">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-blue-600 text-white font-bold text-xs flex items-center justify-center">
                    {idx + 1}
                  </span>
                  <span className="font-mono font-bold text-blue-300 text-sm">{msg.name}</span>
                </div>
                <div className="text-xs font-mono bg-slate-900/80 px-2 py-0.5 rounded text-slate-300 border border-slate-700">
                  {msg.size_bits} bits
                </div>
              </div>

              <div className="flex items-center gap-2 text-xs text-slate-300 bg-slate-900/60 p-2 rounded font-mono mb-2">
                <span className="text-blue-400 font-semibold">{from}</span>
                {isLeftToRight ? <ArrowRight size={14} className="text-emerald-400" /> : <ArrowLeft size={14} className="text-amber-400" />}
                <span className="text-purple-400 font-semibold">{to}</span>
                <span className="text-slate-500 ml-auto font-sans">({msg.direction})</span>
              </div>

              {msg.note && (
                <p className="text-xs text-slate-400 mt-2 italic border-l-2 border-slate-600 pl-2">
                  {msg.note}
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
