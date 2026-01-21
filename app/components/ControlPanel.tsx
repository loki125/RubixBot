import React, { useState } from 'react';
import { RobotStatus } from '../types';
import { Scan, Play, Shuffle, Loader2, Settings, ChevronDown, Grid3X3 } from 'lucide-react';

interface ControlPanelProps {
  onDetect: () => void;
  onSolve: () => void;
  onScramble: () => void;
  onManualMove: (move: string) => void;
  status: RobotStatus;
}

export const ControlPanel: React.FC<ControlPanelProps> = ({ onDetect, onSolve, onScramble, onManualMove, status }) => {
  const [isOpen, setIsOpen] = useState(false);
  const isBusy = status !== 'idle';
  
  const moves = [
    { label: 'L', val: 'L' }, { label: 'R', val: 'R' }, { label: 'U', val: 'U' }, { label: 'D', val: 'D' },
    { label: 'F', val: 'F' }, { label: 'B', val: 'B' }, { label: "L'", val: "L'" }, { label: "R'", val: "R'" },
    { label: "U'", val: "U'" }, { label: "D'", val: "D'" }, { label: "F'", val: "F'" }, { label: "B'", val: "B'" }
  ];

  return (
    <div className="flex flex-col gap-3">
      {/* High Level Controls */}
      <button
        onClick={onDetect}
        disabled={isBusy}
        className="group relative flex items-center justify-between px-6 py-5 rounded-2xl bg-gradient-to-r from-slate-800 to-slate-800/80 border border-slate-700 hover:border-cyan-500/50 active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg overflow-hidden"
      >
        <div className="absolute inset-0 bg-cyan-500/5 translate-x-[-100%] group-hover:translate-x-0 transition-transform duration-500"></div>
        <div className="flex items-center gap-4 z-10">
          <div className="p-3 bg-slate-900 rounded-full border border-slate-700 group-hover:border-cyan-500/50 transition-colors">
             {status === 'detecting' ? <Loader2 className="w-6 h-6 animate-spin text-cyan-400" /> : <Scan className="w-6 h-6 text-cyan-400" />}
          </div>
          <div className="text-left">
            <div className="font-bold text-slate-100 tracking-wide text-lg">SCAN CUBE</div>
            <div className="text-xs text-slate-400 font-mono">INITIATE SENSORS</div>
          </div>
        </div>
      </button>

      <div className="grid grid-cols-2 gap-3">
        <button
          onClick={onScramble}
          disabled={isBusy}
          className="group relative flex flex-col items-center justify-center gap-3 p-5 rounded-2xl bg-slate-800 border border-slate-700 hover:border-orange-500/50 active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg overflow-hidden"
        >
          <div className="absolute inset-0 bg-orange-500/5 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
          {status === 'scrambling' ? <Loader2 className="w-6 h-6 animate-spin text-orange-400" /> : <Shuffle className="w-6 h-6 text-orange-400" />}
          <span className="text-sm font-bold tracking-wider z-10 text-slate-200 text-center">RANDOM SCRAMBLE</span>
        </button>

        <button
          onClick={onSolve}
          disabled={isBusy}
          className="group relative flex flex-col items-center justify-center gap-3 p-5 rounded-2xl bg-slate-800 border border-slate-700 hover:border-green-500/50 active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg overflow-hidden"
        >
          <div className="absolute inset-0 bg-green-500/5 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
          {status === 'solving' ? <Loader2 className="w-6 h-6 animate-spin text-green-400" /> : <Play className="w-6 h-6 text-green-400 fill-current" />}
          <span className="text-sm font-bold tracking-wider z-10 text-slate-200">SOLVE</span>
        </button>
      </div>

      {/* Manual Operations Toggle */}
      <div className="pt-2">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={`w-full flex items-center justify-between px-4 py-3 rounded-xl border transition-all duration-300 ${
            isOpen 
            ? 'bg-slate-800 border-cyan-500/30 text-cyan-100' 
            : 'bg-slate-900/40 border-slate-800 text-slate-400 hover:bg-slate-800/60'
          }`}
        >
          <div className="flex items-center gap-3">
            <Grid3X3 className={`w-4 h-4 ${isOpen ? 'text-cyan-400' : 'text-slate-500'}`} />
            <span className="text-sm font-bold tracking-widest uppercase">Manual Operations</span>
          </div>
          <ChevronDown className={`w-4 h-4 transition-transform duration-300 ${isOpen ? 'rotate-180 text-cyan-400' : ''}`} />
        </button>

        {/* Expandable Move Grid */}
        {isOpen && (
          <div className="grid grid-cols-4 gap-2 mt-3 animate-in slide-in-from-top-2 fade-in duration-300">
            {moves.map((m) => (
               <button
                key={m.label}
                onClick={() => onManualMove(m.val)}
                disabled={isBusy}
                className="h-12 rounded-lg bg-slate-800 border border-slate-700 hover:border-cyan-500/50 hover:bg-cyan-900/20 active:bg-cyan-500/20 text-cyan-200 font-mono font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {m.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};