import React, { useState, useEffect } from 'react';
import { 
  ArrowRight, 
  ArrowLeft, 
  Shield, 
  Server, 
  Laptop, 
  Play, 
  Pause, 
  RotateCcw, 
  ChevronRight, 
  ChevronLeft,
  KeyRound,
  Lock,
  Cpu,
  Info
} from 'lucide-react';

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

interface StepDetails {
  title: string;
  sender: 'user' | 'cloud' | 'cs';
  receiver: 'user' | 'cloud' | 'cs';
  directionText: string;
  sizeBits: number;
  parameters: { symbol: string; meaning: string; formula?: string }[];
  localComputation: string[];
  verificationStep?: string;
}

export const ProtocolFlow: React.FC<ProtocolFlowProps> = ({ protocolId, messages }) => {
  const [activeStep, setActiveStep] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);

  useEffect(() => {
    setActiveStep(0);
    setIsPlaying(false);
  }, [protocolId, messages]);

  useEffect(() => {
    let timer: any;
    if (isPlaying) {
      timer = setInterval(() => {
        setActiveStep((prev) => {
          if (prev >= messages.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 3500);
    }
    return () => clearInterval(timer);
  }, [isPlaying, messages.length]);

  const getStepDetails = (stepIndex: number): StepDetails => {
    if (protocolId === 'ju_park') {
      if (stepIndex === 0) {
        return {
          title: 'Message M1: Authentication Request',
          sender: 'user',
          receiver: 'cloud',
          directionText: 'User (Ui) → Cloud Server (Sj)',
          sizeBits: 1056,
          parameters: [
            { symbol: 'PIDi', meaning: 'Current dynamic user pseudonym', formula: 'H(IDi ∥ ni ∥ xcs)' },
            { symbol: 'B1', meaning: 'Masked user fresh nonce ri', formula: 'ri ⊕ H(SIDi ∥ IDCS ∥ ki)' },
            { symbol: 'B2', meaning: 'Masked cloud server identity IDj', formula: 'H(IDj) ⊕ H(IDCS ∥ SIDi ∥ ri)' },
            { symbol: 'V1', meaning: 'User authentication ticket (MAC)', formula: 'H(IDCS ∥ TS1 ∥ SIDi ∥ ki ∥ ri)' },
            { symbol: 'TS1', meaning: 'Freshness timestamp', formula: '32-bit Unix epoch timestamp' },
          ],
          localComputation: [
            'User inserts Smart Card and enters biometric σi and password PWi.',
            'Derives helper RPWi = H(IDi ∥ PWi ∥ σi) to verify local card ownership.',
            'Reconstructs secret ki = A1 ⊕ H(IDi ∥ hpw) and SIDi = A2 ⊕ H(σi ∥ PWi).',
            'Generates fresh CSPRNG nonce ri and samples timestamp TS1.'
          ],
          verificationStep: 'Cloud server Sj checks freshness |TS1 - Tcurrent| ≤ ΔT before proceeding.'
        };
      }
      if (stepIndex === 1) {
        return {
          title: 'Message M2: Forwarded Verification Request',
          sender: 'cloud',
          receiver: 'cs',
          directionText: 'Cloud Server (Sj) → Control Server (CS)',
          sizeBits: 1600,
          parameters: [
            { symbol: 'M1', meaning: 'Forwarded unmodified user request payload', formula: '{PIDi, B1, B2, V1, TS1}' },
            { symbol: 'B3', meaning: 'Masked cloud nonce rj', formula: 'rj ⊕ H(kj ∥ IDj)' },
            { symbol: 'V2', meaning: 'Cloud authentication ticket (MAC)', formula: 'H(kj ∥ TS2 ∥ IDj ∥ rj)' },
            { symbol: 'TS2', meaning: 'Cloud freshness timestamp', formula: '32-bit Unix epoch timestamp' },
          ],
          localComputation: [
            'Cloud server Sj generates fresh CSPRNG nonce rj.',
            'Masks rj with shared cloud key kj registered with Control Server.',
            'Generates authenticator V2 binding timestamp TS2 and identity IDj.'
          ],
          verificationStep: 'CS verifies timestamp TS2, recovers rj using kj, and checks HMAC match for V2.'
        };
      }
      if (stepIndex === 2) {
        return {
          title: 'Message M3: Key Token & Pseudonym Update',
          sender: 'cs',
          receiver: 'cloud',
          directionText: 'Control Server (CS) → Cloud Server (Sj)',
          sizeBits: 1824,
          parameters: [
            { symbol: 'B6', meaning: 'Encrypted nonces for Cloud', formula: '(rk ∥ ri) ⊕ H(rj ∥ kj)' },
            { symbol: 'B7', meaning: 'Masked common session parameter c1', formula: 'c1 ⊕ H(rj ∥ IDj)' },
            { symbol: 'B8', meaning: 'Encrypted nonces for User', formula: '(rj ∥ rk) ⊕ H(SIDi ∥ IDCS ∥ ri)' },
            { symbol: 'B9', meaning: 'Masked Cloud pseudo-identity SIDj', formula: 'SIDj ⊕ H(SIDi ∥ rk)' },
            { symbol: 'V3', meaning: 'Control Server authentication token for Cloud', formula: 'H(rj ∥ rk ∥ c1 ∥ IDj ∥ TS3)' },
            { symbol: 'V4', meaning: 'Control Server authentication token for User', formula: 'H(SIDi ∥ rj ∥ rk ∥ c1 ∥ TS3)' },
            { symbol: 'PIDi*', meaning: 'Newly rotated dynamic user pseudonym', formula: 'PIDi ⊕ H(PIDi ∥ rk ∥ ri)' },
            { symbol: 'TS3', meaning: 'Control Server timestamp', formula: '32-bit Unix epoch timestamp' },
          ],
          localComputation: [
            'CS locates user row via PIDi and unmasks SIDi and ki.',
            'Validates user authenticator V1 = H(IDCS ∥ TS1 ∥ SIDi ∥ ki ∥ ri).',
            'Unmasks destination cloud IDj from B2.',
            'Generates third random nonce rk and evaluates intermediate ticket c1 = H((SIDi ⊕ SIDj) ∥ IDCS).',
            'Updates database record: replaces consumed PIDi with PIDi* for unlinkability.'
          ],
          verificationStep: 'Cloud verifies V3, unmasks ri and rk, and derives session key SK = H(SIDi ∥ SIDj ∥ ri ∥ rj ∥ rk).'
        };
      }
      if (stepIndex === 3) {
        return {
          title: 'Message M4: Authentication Relay to User',
          sender: 'cloud',
          receiver: 'user',
          directionText: 'Cloud Server (Sj) → User (Ui)',
          sizeBits: 1056,
          parameters: [
            { symbol: 'B8', meaning: 'Encrypted nonces (rj, rk) from CS', formula: '(rj ∥ rk) ⊕ H(SIDi ∥ IDCS ∥ ri)' },
            { symbol: 'B9', meaning: 'Masked SIDj parameter from CS', formula: 'SIDj ⊕ H(SIDi ∥ rk)' },
            { symbol: 'V4', meaning: 'Authenticity token for User from CS', formula: 'H(SIDi ∥ rj ∥ rk ∥ c1 ∥ TS3)' },
            { symbol: 'PIDi*', meaning: 'Rotated pseudonym to update Smart Card', formula: 'PIDi ⊕ H(PIDi ∥ rk ∥ ri)' },
            { symbol: 'TS4', meaning: 'Cloud relay timestamp', formula: '32-bit Unix epoch timestamp' },
          ],
          localComputation: [
            'Cloud server forwards user-targeted credentials from M3.',
            'User decrypts rj, rk from B8 using own stored SIDi and ri.',
            'User reconstructs SIDj from B9 and validates V4 token.',
            'User replaces PIDi with PIDi* in smart card non-volatile memory.',
            'Derives identical session key: SK = H(SIDi ∥ SIDj ∥ ri ∥ rj ∥ rk).'
          ],
          verificationStep: 'Both endpoints confirm mutual authentication with matching 256-bit session key SK.'
        };
      }
    }

    if (protocolId === 'ecc') {
      if (stepIndex === 0) {
        return {
          title: 'Message M1: Ephemeral ECDH Public Key Exchange',
          sender: 'user',
          receiver: 'cloud',
          directionText: 'User (Ui) → Cloud Server (Sj)',
          sizeBits: 936,
          parameters: [
            { symbol: 'Pu', meaning: 'User ephemeral NIST P-256 public key', formula: 'Pu = a · G (a ∈R [1, n-1])' },
            { symbol: 'Ni', meaning: 'User fresh 128-bit challenge nonce', formula: 'CSPRNG random 16 bytes' },
            { symbol: 'T1', meaning: 'Freshness timestamp', formula: '32-bit timestamp' },
            { symbol: 'Vi', meaning: 'Ticket authentication signature/MAC', formula: 'HMAC(K_reg, Pu ∥ Ni ∥ T1 ∥ Sj)' },
          ],
          localComputation: [
            'Generates ephemeral private scalar a on secp256r1 curve.',
            'Computes ephemeral public point Pu = a · G.',
            'Signs ticket using pre-shared registration secret derived during setup.'
          ],
          verificationStep: 'Cloud server validates public key point on NIST P-256 curve and freshness |T1 - T| ≤ ΔT.'
        };
      }
      return {
        title: 'Message M2: Cloud Ephemeral ECDH Response & Key Agreement',
        sender: 'cloud',
        receiver: 'user',
        directionText: 'Cloud Server (Sj) → User (Ui)',
        sizeBits: 936,
        parameters: [
          { symbol: 'Pc', meaning: 'Cloud ephemeral NIST P-256 public key', formula: 'Pc = b · G (b ∈R [1, n-1])' },
          { symbol: 'Nc', meaning: 'Cloud fresh 128-bit challenge nonce', formula: 'CSPRNG random 16 bytes' },
          { symbol: 'T2', meaning: 'Cloud freshness timestamp', formula: '32-bit timestamp' },
          { symbol: 'Vj', meaning: 'Server authentication ticket', formula: 'HMAC(K_reg, Pc ∥ Nc ∥ T2 ∥ Ui)' },
        ],
        localComputation: [
          'Cloud generates ephemeral private scalar b and point Pc = b · G.',
          'Cloud computes shared secret point: S = b · Pu = b · (a · G).',
          'User receives Pc and computes: S = a · Pc = a · (b · G).',
          'Both derive symmetric session key via HKDF-SHA256(S.x ∥ Ni ∥ Nc).'
        ],
        verificationStep: 'Both endpoints establish identical session key in 2 direct message passes.'
      };
    }

    // Proposed Reduced Roundtrip
    if (stepIndex === 0) {
      return {
        title: 'Message M1: Initial IoT Authentication Request',
        sender: 'user',
        receiver: 'cloud',
        directionText: 'User (Ui) → Cloud Server (Sj)',
        sizeBits: 1056,
        parameters: [
          { symbol: 'PIDi', meaning: 'User pseudonym', formula: 'H(IDi ∥ ni ∥ xcs)' },
          { symbol: 'B1, B2', meaning: 'Masked nonce & masked destination cloud', formula: 'XOR masking with ki and SIDi' },
          { symbol: 'V1', meaning: 'Ticket authenticator', formula: 'MAC over TS1, SIDi, ki, ri' },
        ],
        localComputation: ['User evaluates local credentials and constructs request.'],
      };
    }
    if (stepIndex === 1) {
      return {
        title: 'Message M2: Aggregated Request to Control Server',
        sender: 'cloud',
        receiver: 'cs',
        directionText: 'Cloud Server (Sj) → Control Server (CS)',
        sizeBits: 1600,
        parameters: [
          { symbol: 'M1', meaning: 'Forwarded user payload', formula: '{PIDi, B1, B2, V1, TS1}' },
          { symbol: 'B3, V2', meaning: 'Cloud nonce & authenticator', formula: 'Masked rj and V2' },
        ],
        localComputation: ['Cloud server adds cloud authentication payload.'],
      };
    }
    return {
      title: 'Message M3: Proposed Combined Response & Relay',
      sender: 'cs',
      receiver: 'user',
      directionText: 'Control Server (CS) → Cloud (Sj) → User (Ui)',
      sizeBits: 1824,
      parameters: [
        { symbol: 'V3, V4', meaning: 'Dual verification tokens for Cloud and User', formula: 'Consolidated into single response' },
        { symbol: 'B6, B8', meaning: 'Relayed session parameters', formula: 'Single round-trip reduction' },
      ],
      localComputation: [
        'CS produces consolidated payload delivering Cloud and User material together.',
        'Cloud verifies V3, extracts its session material, and immediately relays user payload.',
        'Eliminates separate M4 handshake, achieving 3 total message rounds.'
      ],
      verificationStep: 'Requires formal verification to prove equivalence under Dolev-Yao concurrent interception.'
    };
  };

  const currentStep = getStepDetails(activeStep);

  const getActorColumnIndex = (actor: 'user' | 'cloud' | 'cs'): number => {
    switch (actor) {
      case 'user': return 0;
      case 'cloud': return 1;
      case 'cs': return 2;
    }
  };

  const senderCol = getActorColumnIndex(currentStep.sender);
  const receiverCol = getActorColumnIndex(currentStep.receiver);

  return (
    <div className="bg-slate-900 rounded-xl p-6 text-white border border-slate-800 shadow-xl my-6">
      {/* Top Header & Playback Controls */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mb-6 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
            <h3 className="text-lg font-bold text-slate-100">
              Interactive 3-Party Sequence Flow
            </h3>
            <span className="text-xs px-2 py-0.5 rounded bg-blue-900/60 text-blue-300 border border-blue-700/50 font-mono">
              Step {activeStep + 1} of {messages.length}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            {protocolId === 'ju_park' && 'Ju-Park 2023 Normalized 3-Party Hash/XOR Authentication (4 Messages)'}
            {protocolId === 'ecc' && 'NIST P-256 Ephemeral ECDH Counterpart (2 Direct Messages)'}
            {protocolId === 'reduced_roundtrip' && 'Proposed 3-Message Reduced-Round-Trip Extension (Relayed M3)'}
          </p>
        </div>

        {/* Stepper Controls */}
        <div className="flex items-center gap-2 bg-slate-800/90 p-1.5 rounded-lg border border-slate-700">
          <button
            onClick={() => setActiveStep((p) => Math.max(0, p - 1))}
            disabled={activeStep === 0}
            className="p-1.5 hover:bg-slate-700 disabled:opacity-30 rounded text-slate-300 transition-colors"
            title="Previous Step"
          >
            <ChevronLeft size={18} />
          </button>
          
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="flex items-center gap-1.5 px-3 py-1 bg-blue-600 hover:bg-blue-500 rounded text-xs font-semibold text-white transition-colors"
          >
            {isPlaying ? <><Pause size={14} /> Pause</> : <><Play size={14} /> Auto Play</>}
          </button>

          <button
            onClick={() => setActiveStep((p) => Math.min(messages.length - 1, p + 1))}
            disabled={activeStep === messages.length - 1}
            className="p-1.5 hover:bg-slate-700 disabled:opacity-30 rounded text-slate-300 transition-colors"
            title="Next Step"
          >
            <ChevronRight size={18} />
          </button>

          <button
            onClick={() => { setActiveStep(0); setIsPlaying(false); }}
            className="p-1.5 hover:bg-slate-700 rounded text-slate-400 hover:text-white transition-colors ml-1"
            title="Reset to Step 1"
          >
            <RotateCcw size={16} />
          </button>
        </div>
      </div>

      {/* 3 Entity Lifeline Headers */}
      <div className="grid grid-cols-3 gap-4 text-center mb-6 relative">
        {/* User Lifeline */}
        <div className={`p-4 rounded-xl border transition-all duration-300 ${
          currentStep.sender === 'user' || currentStep.receiver === 'user'
            ? 'bg-blue-950/40 border-blue-500 shadow-md shadow-blue-500/10'
            : 'bg-slate-800/40 border-slate-700/60'
        }`}>
          <div className="w-10 h-10 mx-auto rounded-lg bg-blue-500/20 text-blue-400 border border-blue-500/40 flex items-center justify-center mb-2">
            <Laptop size={20} />
          </div>
          <div className="font-semibold text-sm text-slate-200">User / IoT Node</div>
          <div className="text-[11px] text-blue-300 font-mono mt-0.5">Device & Smart Card ($U_i$)</div>
        </div>

        {/* Cloud Server Lifeline */}
        <div className={`p-4 rounded-xl border transition-all duration-300 ${
          currentStep.sender === 'cloud' || currentStep.receiver === 'cloud'
            ? 'bg-indigo-950/40 border-indigo-500 shadow-md shadow-indigo-500/10'
            : 'bg-slate-800/40 border-slate-700/60'
        }`}>
          <div className="w-10 h-10 mx-auto rounded-lg bg-indigo-500/20 text-indigo-400 border border-indigo-500/40 flex items-center justify-center mb-2">
            <Server size={20} />
          </div>
          <div className="font-semibold text-sm text-slate-200">Cloud Server</div>
          <div className="text-[11px] text-indigo-300 font-mono mt-0.5">Service Host ($S_j$)</div>
        </div>

        {/* Control Server Lifeline */}
        <div className={`p-4 rounded-xl border transition-all duration-300 ${
          currentStep.sender === 'cs' || currentStep.receiver === 'cs'
            ? 'bg-purple-950/40 border-purple-500 shadow-md shadow-purple-500/10'
            : 'bg-slate-800/40 border-slate-700/60'
        }`}>
          <div className="w-10 h-10 mx-auto rounded-lg bg-purple-500/20 text-purple-400 border border-purple-500/40 flex items-center justify-center mb-2">
            <Shield size={20} />
          </div>
          <div className="font-semibold text-sm text-slate-200">Control Server</div>
          <div className="text-[11px] text-purple-300 font-mono mt-0.5">Trust Anchor ($CS$)</div>
        </div>
      </div>

      {/* Visual Animated Packet Lane */}
      <div className="bg-slate-950/70 rounded-xl p-5 border border-slate-800 mb-6 relative overflow-hidden">
        <div className="flex justify-between items-center text-xs text-slate-400 mb-2 font-mono">
          <span>Active Packet Transmission:</span>
          <span className="text-emerald-400 font-semibold">{currentStep.directionText}</span>
          <span>{currentStep.sizeBits} bits</span>
        </div>

        {/* Lane Canvas Representation */}
        <div className="relative h-12 w-full flex items-center">
          {/* Base Track */}
          <div className="absolute inset-x-4 h-0.5 bg-slate-800"></div>

          {/* Active transmission line between sender and receiver */}
          <div 
            className="absolute h-1 bg-gradient-to-r from-blue-500 via-indigo-500 to-emerald-400 rounded transition-all duration-500 shadow-sm shadow-blue-500/50"
            style={{
              left: `${Math.min(senderCol, receiverCol) * 33.33 + 16.66}%`,
              width: `${Math.abs(senderCol - receiverCol) * 33.33}%`
            }}
          ></div>

          {/* Moving Animated Packet */}
          <div 
            className="absolute -translate-y-1/2 flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-600 text-white text-[11px] font-mono shadow-lg shadow-blue-600/50 border border-blue-400 transition-all duration-700"
            style={{
              left: senderCol < receiverCol ? '42%' : '42%',
              top: '50%'
            }}
          >
            <KeyRound size={12} className="animate-spin" />
            <span>{messages[activeStep]?.name || `M${activeStep + 1}`}</span>
            {senderCol < receiverCol ? <ArrowRight size={12} /> : <ArrowLeft size={12} />}
          </div>
        </div>

        {/* Step selector pills */}
        <div className="flex gap-2 justify-center mt-3">
          {messages.map((m, idx) => (
            <button
              key={idx}
              onClick={() => { setActiveStep(idx); setIsPlaying(false); }}
              className={`px-3 py-1 rounded text-xs font-mono transition-all ${
                activeStep === idx 
                  ? 'bg-blue-600 text-white font-bold ring-2 ring-blue-400 ring-offset-1 ring-offset-slate-900' 
                  : 'bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700'
              }`}
            >
              {m.name} ({m.size_bits}b)
            </button>
          ))}
        </div>
      </div>

      {/* Cryptographic Inspector Drawer for the Active Step */}
      <div className="bg-slate-850 bg-slate-800/70 rounded-xl p-5 border border-slate-700/80">
        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2 mb-4 border-b border-slate-700/60 pb-3">
          <div className="flex items-center gap-2">
            <Lock size={16} className="text-emerald-400" />
            <h4 className="font-bold text-slate-100 text-sm">
              {currentStep.title}
            </h4>
          </div>
          <span className="text-xs font-mono text-slate-400 bg-slate-900/80 px-2 py-0.5 rounded border border-slate-700">
            Payload Width: {currentStep.sizeBits} bits
          </span>
        </div>

        {/* Parameters Grid */}
        <div className="mb-4">
          <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <Cpu size={14} className="text-blue-400" />
            Transmitted Cryptographic Parameters
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            {currentStep.parameters.map((param, idx) => (
              <div key={idx} className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-700/60 flex flex-col justify-between">
                <div className="flex items-baseline justify-between">
                  <span className="font-mono font-bold text-amber-300 text-xs">{param.symbol}</span>
                  <span className="text-[11px] text-slate-400">{param.meaning}</span>
                </div>
                {param.formula && (
                  <div className="mt-1.5 font-mono text-[11px] text-emerald-300/90 bg-slate-950/70 p-1.5 rounded border border-slate-800 break-all">
                    {param.formula}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Local Computation & Verification */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs pt-2 border-t border-slate-700/60">
          <div>
            <div className="font-semibold text-slate-300 mb-1.5 flex items-center gap-1">
              <Info size={13} className="text-indigo-400" />
              Entity Local Operations:
            </div>
            <ul className="space-y-1 text-slate-400 pl-4 list-disc">
              {currentStep.localComputation.map((comp, idx) => (
                <li key={idx}>{comp}</li>
              ))}
            </ul>
          </div>

          {currentStep.verificationStep && (
            <div>
              <div className="font-semibold text-slate-300 mb-1.5 flex items-center gap-1">
                <Shield size={13} className="text-emerald-400" />
                Receiver Verification Check:
              </div>
              <p className="text-slate-400 bg-slate-900/70 p-2.5 rounded border border-slate-700/60 leading-relaxed">
                {currentStep.verificationStep}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
