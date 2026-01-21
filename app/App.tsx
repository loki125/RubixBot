import React, { useState, useEffect } from 'react';
import { ControlPanel } from './components/ControlPanel';
import { StatusLog } from './components/StatusLog';
import { detectCube, solveCube, scrambleCube, getInstructions, performMove } from './services/robotApi';
import { RobotStatus, CubeState, LogEntry } from './types';
import { Cpu, RotateCcw, Activity, Server, Smartphone, Wifi, Radio } from 'lucide-react';

const App: React.FC = () => {
  const [cubeState, setCubeState] = useState<CubeState | null>(null);
  const [status, setStatus] = useState<RobotStatus>('idle');
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [instructions, setInstructions] = useState<string[]>([]);
  const [useMock, setUseMock] = useState<boolean>(true);

  const addLog = (message: string, type: 'info' | 'success' | 'error' | 'warning' = 'info') => {
    setLogs(prev => [{ id: Date.now().toString(), timestamp: new Date(), message, type }, ...prev]);
  };

  useEffect(() => {
    addLog("Mobile Interface initialized.", 'info');
    detectCube(useMock)
      .then(state => {
        setCubeState(state);
        addLog("Robot connected. State synced.", 'success');
      })
      .catch(err => {
        addLog("Connection failed. Offline mode.", 'warning');
      });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleDetect = async () => {
    setStatus('detecting');
    addLog("Scanning...", 'info');
    try {
      const state = await detectCube(useMock);
      setCubeState(state);
      setStatus('idle');
      addLog("Scan complete.", 'success');
      setInstructions([]);
    } catch (error) {
      setStatus('error');
      addLog(`Scan Error: ${(error as Error).message}`, 'error');
    }
  };

  const handleScramble = async () => {
    setStatus('scrambling');
    addLog("Scrambling...", 'info');
    try {
      const newState = await scrambleCube(useMock);
      setCubeState(newState);
      setStatus('idle');
      addLog("Scramble complete.", 'success');
      setInstructions([]);
    } catch (error) {
      setStatus('error');
      addLog(`Scramble Error: ${(error as Error).message}`, 'error');
    }
  };

  const handleSolve = async () => {
    setStatus('solving');
    addLog("Solving...", 'info');
    try {
      const result = await solveCube(useMock);
      if (result.success) {
        addLog(`Solved in ${result.moves} moves.`, 'success');
        setStatus('idle');
        const steps = await getInstructions(useMock);
        setInstructions(steps);
        setCubeState(result.finalState);
      } else {
         throw new Error("No solution found.");
      }
    } catch (error) {
      setStatus('error');
      addLog(`Solve Error: ${(error as Error).message}`, 'error');
    }
  };

  const handleManualMove = async (move: string) => {
    if (status !== 'idle') return;
    addLog(`Executing manual move: ${move}`, 'info');
    try {
      await performMove(move, useMock);
      // In a real app we might fetch new state here
    } catch (error) {
      addLog(`Move Error: ${(error as Error).message}`, 'error');
    }
  };

  return (
    <div className="h-full w-full flex flex-col bg-slate-950 text-cyan-50 font-sans">
      {/* Mobile Header */}
      <header className="h-14 border-b border-cyan-900/30 flex items-center justify-between px-4 bg-slate-900/80 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center gap-2">
          <Smartphone className="w-5 h-5 text-cyan-400" />
          <h1 className="text-lg font-bold tracking-wider text-cyan-100">RUBIX<span className="text-cyan-500">BOT</span></h1>
        </div>
        
        <button 
          onClick={() => {
            setUseMock(!useMock);
            addLog(useMock ? "Switched to LIVE" : "Switched to SIM", 'warning');
          }}
          className={`p-2 rounded-full border transition-all ${
            useMock 
            ? 'border-yellow-500/30 bg-yellow-500/10 text-yellow-400' 
            : 'border-green-500/30 bg-green-500/10 text-green-400 animate-pulse'
          }`}
        >
          {useMock ? <Activity className="w-4 h-4" /> : <Server className="w-4 h-4" />}
        </button>
      </header>

      {/* Main Content - Mobile Scrollable */}
      <main className="flex-1 overflow-y-auto overflow-x-hidden p-4 space-y-4 pb-8">
        
        {/* Connection/Status Card */}
        <div className="bg-slate-900/50 border border-cyan-900/30 rounded-2xl p-4 flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-3">
             <div className={`w-3 h-3 rounded-full ${status === 'idle' ? 'bg-cyan-500' : 'bg-yellow-500 animate-ping'}`}></div>
             <div>
               <div className="text-xs text-slate-400 uppercase tracking-widest">System Status</div>
               <div className="font-mono text-cyan-100 font-bold uppercase">{status}</div>
             </div>
          </div>
          <Wifi className="w-5 h-5 text-slate-600" />
        </div>

        {/* Primary Controls */}
        <section>
           <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-2 ml-1">
            <Radio className="w-3 h-3" /> Command Center
          </h2>
          <ControlPanel 
            onDetect={handleDetect}
            onSolve={handleSolve}
            onScramble={handleScramble}
            onManualMove={handleManualMove}
            status={status}
          />
        </section>

        {/* Moves / Instructions */}
        {instructions.length > 0 && (
          <section className="animate-in slide-in-from-bottom-4 duration-500">
             <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-2 ml-1">
              <RotateCcw className="w-3 h-3" /> Solution Path
            </h2>
            <div className="bg-slate-900/50 rounded-2xl p-4 border border-cyan-900/20">
              <div className="grid grid-cols-5 gap-2">
                {instructions.map((move, idx) => (
                  <div key={idx} className="bg-slate-800 text-center py-2 rounded-lg text-cyan-300 font-bold font-mono text-sm border border-slate-700/50 shadow-sm">
                    {move}
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}

        {/* System Logs */}
        <section className="flex-1 min-h-[150px]">
          <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-2 ml-1">
            <Cpu className="w-3 h-3" /> Terminal
          </h2>
          <div className="bg-slate-950 rounded-2xl p-4 border border-slate-800 h-48 shadow-inner overflow-hidden flex flex-col">
             <StatusLog logs={logs} />
          </div>
        </section>

      </main>
    </div>
  );
};

export default App;